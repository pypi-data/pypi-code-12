import csv
import traceback
from time import sleep
from access_tokens import access_tokens

from cutils import ProgressBar, Gmail

from parser_location import parse_location


class Foursquare:

    def __init__(self, job, **kwargs):
        self._job = job
        self._access_token = int(kwargs.get('access_token', 0))
        self._extension = ''
        self._speed = 0.7

        if 'location' in self._job.lower():
            self._extension = '.location'
        elif 'city' in self._job.lower():
            self._extension = '.city'

    def crawl(self):
        with open(self._input_fp, 'r') as i:
            inputs = [row.strip() for row in i]
        n_retry = 10
        i_retry = 0
        bar = ProgressBar(total=len(inputs))
        with open(self._output_fp, 'a') as o:
            csvwriter = csv.writer(o, delimiter=self._output_delimiter)
            for item in inputs:
                bar.move().log()
                self.log(' ' + item + '...')

                try:
                    parsed_item = self.parse(item)
                    if parsed_item:
                        out = [item]
                        out.extend(parsed_item)
                        csvwriter.writerow(out)
                        self.log('Done.\n')
                    else:
                        self.log('NotFound.\n')
                    i_retry = 0
                except:
                    i_retry += 1
                    if i_retry <= n_retry:
                        self.throw(self._input_fp + ' ' + item + '\n' + traceback.format_exc())
                        sleep(10 * i_retry)
                        continue
                    else:
                        self.throw(self._input_fp + ' ' + item + '\n' + traceback.format_exc())
                        break
                sleep(self._speed)
            self.log('\n\n' + '\nDone', True)
        bar.close()

    def set_input(self, fp_in, **kwargs):
        self._input_fp = fp_in
        self._input_index = int(kwargs.get('index', 0))
        return self

    def set_output(self, fp_out, **kwargs):
        self._output_fp = fp_out
        self._output_delimiter = kwargs.get('delimiter', ',')
        return self

    def set_speed(self, sec):
        self._speed = sec
        return self

    def set_notifier(self, notifier_type, **kwargs):
        if 'gmail' in notifier_type.lower():
            credential_fp = kwargs.get('credential', './')
            self._notifier = Gmail() \
                .set_from_to() \
                .set_credentials(credential_fp) \
                .set_subject('AWS Foursquare' + self._extension) \
                .send_message(self._input_fp + '\n\n\n')
            self._notifier_error = Gmail() \
                .set_from_to() \
                .set_credentials(credential_fp) \
                .set_subject('AWS Foursquare' + self._extension + ' Error!') \
                .send_message(self._input_fp + '\n\n\n')
        return self

    def log(self, message, is_close=False):
        if isinstance(self._notifier, Gmail):
            self._notifier.send_message(message)
        if is_close:
            self._notifier.close()
            self._notifier.send_message(self._input_fp + '\n\n\n')

    def throw(self, message):
        if isinstance(self._notifier_error, Gmail):
            self._notifier_error.send_message(message).close()
            self._notifier_error.send_message(self._input_fp + '\n\n\n')

    def record(self):
        self.log('KeyboardInterrupt!\n', True)

    def parse(self, item):
        if self._extension == '.location':
            return parse_location(item, access_tokens[self._access_token])
