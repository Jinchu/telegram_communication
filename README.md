# telegram_communication

## Motivation
I needed a quick and dirty way to manage my raspberry pi server via my phone. Of course, there are
ssh apps for Android (and IOS), but they are a little complicated. Telegram bot API has a couple of
benefits.
	- No phone app development needed
	- Two way communication
	- The Telegram app is already in use, so no increased battery drain on phone

There are some drawbacks as well
	- You rely on Telegram
	- The Telegram bot API is notorious for it's bad security
	- All traffic goes via external server, while the target is also a server

## Installation
This script relies on Nick Lee's telepot library. I was lazy and cloned his repository from
https://github.com/nickoala/telepot to my home directory. The location does not really matter. Just
make a soft link to the telepot/telepot folder to this directory. In my case this would be:

ln -s ~/telepot/telepot

Also create a file for storing the pid number of the communication program.

touch ~/communicate.pid

I have tested this with telepot version 12.7

## Usage

python3 communicate_raspb.py -h

You need to have your own configuration file. There is an example configuration example_config.txt

## Note
Running this in your computer opens it to many possible attacks. If you decide to use this, you are
the one taking the risks.

