"""
Script that finds the next flag day in Finland
- Panu Simolin
"""
from bs4 import BeautifulSoup
import urllib.request
from datetime import date, timedelta
import argparse
import configparser


class AlmanakkaParser:
    def __init__(self, configuration):
        self.url = 'https://almanakka.helsinki.fi/fi/'
        self.url += 'liputus-ja-juhlapaivat/liputuspaivat-2018.html'
        self.configuration = configuration
        self.reason_for_flag = None

    def date_found_on_page(self, lines, date_str):
        for line in lines:
            if date_str in line:
                self.reason_for_flag = line
                return True

        return False

    def parse_html_and_react(self, html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        lines = soup.get_text().split('\n')
        try_date = date.today()
        increment = timedelta(days=1)
        found = False

        while not found:
            date_str = '%d.%d.' % (try_date.day, try_date.month)
            found = self.date_found_on_page(lines, date_str)
            try_date += increment

    def get_the_reason(self):
        try:
            print('site: %s' % self.url)
            site = urllib.request.urlopen(self.url)
            self.parse_html_and_react(site.read())
        except urllib.error.URLError:
            print("Connection error")


def main():
    config = configparser.ConfigParser()
    parser = argparse.ArgumentParser(description='Script that finds the ' +
                                                 'next flag day in ' +
                                                 'Finland')

    parser.add_argument("-c", dest='config', type=str,
                        help='Path to the configuration file',
                        default='/home/psimolin/hack_helpers/Configuration.txt')
    parser.set_defaults(mode=False)

    # parse arguments and read configuration
    args = parser.parse_args()
    config.read(args.config)

    flag_d = AlmanakkaParser(config)

    flag_d.get_the_reason()
    print(flag_d.reason_for_flag)


if __name__ == "__main__":
    main()
