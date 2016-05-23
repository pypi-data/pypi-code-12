#!/usr/bin/env python2.7
import argparse
import requests
import json
from datetime import datetime, timedelta
import logging
import logging.handlers
import logging.config
from twx.botapi import TelegramBot

__author__ = 'Wim Fournier <wim.fournier@oracle.com>'
__docformat__ = 'plaintext'
__date__ = '2016-03-21'


class RepeaterStatusBot(object):
    def __init__(self, tg_group, tg_credentials,
                 repeater_info_url, repeater_json_stream_url):
        self.logger = logging.getLogger(__name__)
        self.tg_group = tg_group
        self.tg_credentials = tg_credentials
        self.repeater_json_stream_url = repeater_json_stream_url
        self.repeater_info_url = repeater_info_url
        self.rx_status = {}
        self.statuses = {
            True: 'in',
            False: 'uit',
        }
        self.last_updated = datetime(1970, 1, 1)
        self.RXes = {}
        self.update_rxes()
        self.last_message_send = datetime(1970, 1, 1)
        self._init_telegram()

    def _init_telegram(self):
        self.telegram = TelegramBot(self.tg_credentials)
        self.telegram.update_bot_info().wait()

    def update_rxes(self):
        if datetime.now() - self.last_updated > timedelta(minutes=60):
            self.logger.info('Updating repeater info')
            try:
                repeater_info = requests.get(self.repeater_info_url).json()
            except ValueError:
                repeater_info = {}
            self.last_updated = datetime.now()
            self.RXes = repeater_info.get('rx', {})

    def signal_telegram(self, message, retry=3):
        self.logger.info('Sending via TGL: {msg}'.format(msg=message))
        if retry < 1:
            self.logger.error('Failed sending message, exceeded retries')
            return False
        try:
            result = self.telegram.send_message(self.tg_group, message).wait()
            if not result:
                new_retry = retry - 1
                self.signal_telegram(message, retry=new_retry)
            else:
                return True
        except Exception as error:
            self.logger.error('Caught exception while transmitting message: {type}: {message}'.format(
                type=type(error),
                message=str(error)
            ))
            self._init_telegram()
            new_retry = retry - 1
            return self.signal_telegram(message, retry=new_retry)

    def queue_message(self, receiver, enabled):
        if receiver in self.RXes:
            receiver = self.RXes[receiver]['name']
        msg = '"{receiver} is {status}geschakeld"'.format(
            receiver=receiver, status=self.statuses[enabled]
        )
        self.logger.info('Queueing: {msg}'.format(msg=msg))
        result = self.signal_telegram(msg)

    def run(self):
        for line in requests.get(self.repeater_json_stream_url,
                                 stream=True).iter_lines(1):
            self.logger.debug('Received: {data}'.format(data=line))
            if line.startswith('data: '):
                data = line.split('data: ')[1].strip()
                try:
                    line_json = json.loads(data)
                except Exception as e:
                    self.logger.warn('FAILED (%s): %s', data, e.message)
                else:
                    self.update_rxes()
                    if line_json.get('event') == 'Voter:sql_state':
                        for rx in line_json.get('rx', []).keys():
                            if rx not in self.rx_status:
                                self.rx_status[rx] = None
                            status = line_json['rx'][rx]['sql'] != "off"
                            if self.rx_status[rx] is not None and \
                                    self.rx_status[rx] != status:
                                self.queue_message(rx, status)
                            self.rx_status[rx] = status


def get_arguments():
    """
    This get us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description='Produces an OTL time sheet for on call')
    parser.add_argument('--verbose',
                        '-v',
                        help='Enable verbose logging',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        )
    parser.add_argument('--json-url', '-j',
                        dest='json_url',
                        action='store',
                        help='URL to the json stream',
                        required=True)
    parser.add_argument('--info-url', '-i',
                        dest='info_url',
                        action='store',
                        help='URL to the info stream',
                        required=True)
    parser.add_argument('--telegram-group', '-g',
                        dest='telegram_group',
                        action='store',
                        help='Telegram group to connect to',
                        required=True)
    parser.add_argument('--telegram-credentials', '-c',
                        dest='telegram_credentials',
                        action='store',
                        help='Telegram credentials',
                        required=True)
    parser.add_argument('--logfile', '-l',
                        dest='log_file',
                        action='store',
                        help='Log file to write logs to. When not specified, logs to stdout',
                        required=False)
    args = parser.parse_args()
    return args


def setup_logging(args):
    """
    This sets up the logging.

    Needs the args to get the log level supplied
    :param args: The command line arguments
    """
    if args.verbose:
        log_level=logging.DEBUG
    else:
        log_level=logging.INFO

    if args.log_file:
        logging.basicConfig(filename=args.log_file, level=log_level)
    else:
        logging.basicConfig(level=log_level)


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    setup_logging(args)

    bot = RepeaterStatusBot(
        tg_group=args.telegram_group,
        tg_credentials=args.telegram_credentials,
        repeater_info_url=args.info_url,
        repeater_json_stream_url=args.json_url
    )
    bot.run()


if __name__ == '__main__':
    main()
