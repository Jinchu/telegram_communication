"""
Script for communicating to RaspberryPi wia Telegram
- Panu Simolin
"""
import json
import argparse
import os
import sys
import subprocess
import configparser

from random import choice
from time import sleep
from datetime import datetime

import telepot
import daemon3
import _thread
from why_the_flag import AlmanakkaParser

CONFIG = configparser.ConfigParser()
BOT = None


def handle_input(raw_data):
    """ Based on the received message decide to which program or module forward
    the request in the message. """
    global BOT
    master_id = CONFIG['Telegram']['master_id']
    trusted_chat_rooms = [-125639654, -238588551, 88290184]
    ignored_chats = [-1001124920652]
    ignored_peeps = []
    manual_resp = []
    auto_resp = []

    content_type, chat_type, chat_id = telepot.glance(raw_data)
    print('%s %s %s\n' % (content_type, chat_type, chat_id))

    if chat_id in ignored_chats:
        return

    command = raw_data['text']

    if chat_id in trusted_chat_rooms:
        print('This chat room can be trusted')
        param = command.strip().split()
        print(param)
        if param[0].lower().endswith('lippu') or param[0].lower().endswith('flag'):
            flag_d = AlmanakkaParser(CONFIG)
            flag_d.get_the_reason()
            BOT.sendMessage(raw_data['chat']['id'], flag_d.reason_for_flag)
            print(flag_d.reason_for_flag)
            return

        stripped = param[0].lower().strip('/')
        print(stripped)
        if stripped == 'help':
            BOT.sendMessage(raw_data['chat']['id'], ' '
                            + 'flag, lippu, status')
            return

        if stripped == 'status':
            proc = subprocess.Popen(['uptime'], stdout=subprocess.PIPE)
            BOT.sendMessage(master_id, proc.stdout.read())
            return

        if chat_id != 88290184:
            return

    if chat_id != int(master_id):
        if chat_id in trusted_chat_rooms:
            print("Known chat room. no actions taken")
            return
        send_warning_to_admin(BOT, CONFIG, raw_data, chat_id)
        return

    if content_type != 'text':
        print(content_type)
        if content_type == 'photo' and choice([True, False]):
            BOT.sendMessage(master_id, "Quite beautiful pic, sir.")
        else:
            BOT.sendMessage(master_id, "I'm a bot. Please use text, ok?")
        return

    # This command stops the whole program.
    if command == 'exit' or command == 'stopit':
        _thread.interrupt_main()
        sys.exit(1)

    param = command.strip().split()

    if param[0].lower() == 'open' and param[1].lower() == 'gate':
        print("k:")
        gclient = [CONFIG['gate-keeper']['path'], "127.0.0.1"]
        gclient += CONFIG['gate-keeper']['ports'].strip().split(',')
        print(gclient)
        subprocess.Popen(gclient)

    if param[0] == 'dippa' or param[0] == 'Dippa':
        if len(param) == 2:
            subprocess.Popen(['/home/psimolin/dippa_skript', param[1]])
        else:
            subprocess.Popen(['/home/psimolin/dippa_skript'])
        BOT.sendMessage(master_id, 'compiling thesis')

    if param[0].lower() == 'echo':
        BOT.sendMessage(master_id, param[1])

    """
    Here could be also a generic shell call. Something like:
    result = subprocess.check_output([param[1], param[2]]).decode('utf-8')
    BOT.sendMessage(result)
    """

    if param[0].lower() == 'lippu' or param[0].lower() == 'flag':
        flag_d = AlmanakkaParser(CONFIG)
        flag_d.get_the_reason()
        BOT.sendMessage(raw_data['chat']['id'], flag_d.reason_for_flag)
        print(flag_d.reason_for_flag)

    if param[0].lower() == 'archive_pics':
        arc_p = CONFIG['daemon']['archive_exec_path']
        config_path = CONFIG['daemon']['conf_path']
        subprocess.Popen(['python3', arc_p, '-c', config_path])
        BOT.sendMessage(master_id, 'Pictures archived')

    if param[0].lower() == 'commands' or param[0].lower() == 'help_master':
        BOT.sendMessage(master_id, 'archive_pics, dippa, echo, exit, '
                + 'flag, insta, lippu, shell, status, stopit')


def send_warning_to_admin(target_bot, conf, raw_data, chat_id=0):
    """ Send admin a message that someone is messaging the bot. """
    master_str = conf['Telegram']['master_id']

    target_bot.sendMessage(master_str, "Someone is on to us: " + json.dumps(
        raw_data['from']) + '  chat id: ' + str(chat_id))
    target_bot.sendMessage(master_str, "S/He says:  " + raw_data['text'])
    target_bot.sendMessage(raw_data['chat']['id'], "Who are you?")


def check_the_amount_of_pics(target_folder, threshold, cleaner):
    """ Checks the number of files in the folder. If the number exceeds the
    threshold calls a cleaner program. """
    global BOT
    master_id = CONFIG['Telegram']['master_id']

    n_pics = 0
    for name in os.listdir(target_folder):
        if os.path.isfile(os.path.join(target_folder, name)):
            n_pics += 1

    if n_pics > int(threshold):
        print("number of pics (%d) exceeds the threshold (%s)" %
              (n_pics, threshold))
        subprocess.check_output(cleaner)
        BOT.sendMessage(master_id, '%d pictures archived' % n_pics)

    else:
        print("number of pics (%d) is bellow the threshold (%s)" %
              (n_pics, threshold))


def cur_time_str():
    """ Returns string with current time. """
    return datetime.now().strftime("%H:%M:%S  %A %d.%m.%y")


def parse_telegram_bot_args():
    """ uses argparse to parse given parameters and print help for Telegram. """
    parser = argparse.ArgumentParser(description='Telegram bot that passes '
                                                 'command to the raspberry pi')
    parser.add_argument("-d", dest='mode', action='store_true',
                        help='run as daemon. Default')
    parser.add_argument("-f", dest='mode', action='store_false',
                        help='Run foreground')
    parser.add_argument("-c", dest='config', type=str,
            help='Path to the configuration file',
            default='/home/psimolin/hack_helpers/Configuration.txt')
    parser.add_argument("-s", dest='reply', action='store_false',
            help='program does not send status message to telegram')
    parser.set_defaults(mode=True)

    return parser.parse_args()


def main():
    """ Main function. """
    global BOT
    global CONFIG

    # parse arguments and read configuration
    args = parse_telegram_bot_args()
    CONFIG.read(args.config)

    if args.mode:
        daemon3.daemonize(CONFIG['daemon']['pid_location'])

    BOT = telepot.Bot(CONFIG['Telegram']['bot_id'][3:])
    BOT.message_loop(handle_input,
                     timeout=int(CONFIG['Telegram']['poll_timeout']))
    BOT.sendMessage('88290184', 'Bot online ' +
                    cur_time_str())
    while True:
        sleep(6000)


if __name__ == "__main__":
    main()
