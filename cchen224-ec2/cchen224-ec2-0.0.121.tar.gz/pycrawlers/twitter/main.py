import csv
import traceback
from random import random
from time import sleep

from cutils import Gmail
from cutils import ProgressBar
from sys import stdout
from webparser_tweet import parse_tweet
from webparser_user_info import parse_user_info
from webparser_user_timeline import parse_user_timeline


class TwitterCrawler:

    def __init__(self, job):
        self._job = job.lower()
        self._p_sleep = 0.999
        self._t_sleep = 10
        self._input_fp = ''
        self._output_fp = ''

        if 'info' in self._job.lower():
            self._extension = '.info'
        elif 'timeline' in self._job.lower():
            self._extension = '.timeline'
        elif 'threads' in self._job.lower():
            self._extension = '.threads'
        elif 'tweet' in self._job.lower():
            self._extension = '.tweet'

    def set_input(self, input, **kwargs):
        if isinstance(input, str):
            delimiter = kwargs.get('delimiter', ',')
            index = kwargs.get('index', 0)
            start_value = kwargs.get('start_value', '')
            self._input_fp = input
            with open(input, 'r') as i:
                csvreader = csv.reader(i, delimiter=delimiter)
                if isinstance(index, int):
                    self._input = [row[index] for row in csvreader]
                if isinstance(index, dict):
                    self._input = [row[index.get('tid', 1)] + '@' + row[index.get('uid', index.get('screen_name', 0))] for row in csvreader]
            self._input_total = len(self._input)
            try:
                self._start_index = self._input.index(start_value) if start_value != '' else 0
            except:
                self._start_index = 0
            self._input = self._input[(self._start_index + 1) :]
        if isinstance(input, list):
            self._input = input
            self._input_fp = ''
        return self

    def set_output(self, output_fp, output_delimiter=','):
        self._output_fp = output_fp
        self._output_delimiter = output_delimiter
        return self

    def set_notifier(self, notifier_type, **kwargs):
        if 'gmail' in notifier_type.lower():
            credential_fp = kwargs.get('credential', './')
            self._notifier = Gmail() \
                .set_from_to() \
                .set_credentials(credential_fp) \
                .set_subject('AWS Twitter' + self._extension) \
                .send_message(self._input_fp + '\n\n\n')
            self._notifier_error = Gmail() \
                .set_from_to() \
                .set_credentials(credential_fp) \
                .set_subject('AWS Twitter' + self._extension + ' Error!') \
                .send_message(self._input_fp + '\n\n\n')
        return self

    def log(self, message, is_close=False):
        if isinstance(self._notifier, Gmail):
            self._notifier.send_message(message)
        if is_close:
            self._notifier.close()
            self._notifier.send_message(self._input_fp + '\n\n\n')

    def set_progress_bar(self, hspace=1):
        self._hspace = int(hspace)
        return self

    def throw(self, message):
        if isinstance(self._notifier_error, Gmail):
            self._notifier_error.send_message(message).close()
            self._notifier_error.send_message(self._input_fp + '\n\n\n')

    def crawl(self):
        bar = ProgressBar(total=self._input_total, start_count=self._start_index, hspace=self._hspace)
        with open(self._output_fp if self._output_fp != '' else self._input_fp + self._extension, 'a') as o:
            csvwriter = csv.writer(o, delimiter = self._output_delimiter)
            print self._input_fp, ':'
            bar.move()
            for item in self._input:
                if random() > self._p_sleep:
                    t = random() * self._t_sleep
                    stdout.write('Random sleeping' + str(t) + 'sec\r')
                    stdout.flush()
                    sleep(t)
                parsed_items = self.parse(item)
                self.log(' ' + item + '...')
                try:
                    for parsed_item in parsed_items:
                        if parsed_item:
                            csvwriter.writerow(parsed_item)
                    self.log('\n')
                except:
                    self.throw(self._input_fp + ':user ' + item + '\n' + traceback.format_exc())
                bar.skip_move(0.8)
            self.log('\n\n' + '\nDone', True)
        bar.close()

    def record(self):
        self.log('KeyboardInterrupt!\n', True)


    def parse(self, item):
        if self._extension == '.info':
            return parse_user_info(item, picture=False)
        if self._extension == '.tweet':
            return parse_tweet(item)
        if self._extension == '.timeline':
            return parse_user_timeline(item)