import telnetlib
from cloudshell.core.logger import qs_logger
import re
import time


class ProvisionTelnetHandler(telnetlib.Telnet):

    default_prompt_set = ['\\x1b.*?\(config\)', '\\x1b.*?#', '\\x1b.*?>', '[Pp]ress any key to continue']
    last_result = ''
    last_result_stripped = ''
    last_pattern_index = -1

    control_char_pattern = re.compile('\\x1B.+?[HK]')

    def __init__(self, address, port=22, timeout=60, logger=None):

            if logger is None:
                logger = qs_logger.get_qs_logger('Provision Telnet')

            self.logger = logger

            logger.info('Initialize ProvisionTelnetHandler: {address=' + address + ' port=' + str(port) + ' timeout=' +
                        str(timeout))
            if timeout is 0:
                telnetlib.Telnet.__init__(self, address, port)
            else:
                telnetlib.Telnet.__init__(self, address, port, timeout)

    def login(self, username='', password=''):

        self.logger.info('Logging in telnet handler')
        self.send_and_receive('\r\n')
        self.send_and_receive('\r\n')
        if self.last_pattern_index == -1:
            self.logger.error('Incorrect login result, no matching prompt')
            self.logger.debug(self.last_result_stripped)
            return -1

        if self.last_pattern_index == 3:
            self.logger.info('startup prompt found - sending newline')
            self.send_and_receive('\r\n')

        if self.last_pattern_index == 2:
            self.logger.info('Disabled prompt found - sending "enable"')
            self.send_and_receive('enable')
            if self.last_pattern_index != 1:
                self.logger.error('Enable Failed')
                return -1

        elif self.last_pattern_index == 0:
            self.logger.info('Config mode prompt found, sending "exit"')
            self.send_and_receive('exit')
            if self.last_pattern_index != 1:
                self.logger.error('Failed to exit config mode')
                return -1
        self.logger.info('Successful login')

        self.send_and_receive('terminal length 1000')
        return 1

    def strip_last_line(self, content):
        try:
            return content.rsplit('\r\n', 1)[0]
        except IndexError:
            return content

    def strip_first_line(self, content):
        try:
            return content.split('\r\n', 1)[1]
        except IndexError:
            return content

    def clear_read_buffer(self):
        result = None

        while result != '':
            result = self.read_very_eager()

    def send_and_receive(self, line, use_pattern=True, patterns=[]):
        self.logger.info('sending "' + line + '" via telnet Handler')
        self.clear_read_buffer()
        self.last_result = ''
        self.last_result_stripped = ''
        self.last_pattern_index = -1
        if '\r\n' not in line:
            line += '\r\n'

        self.write(line)
        self.logger.info('Line sent')
        if not use_pattern:
            self.logger.info('Reading very eager')
            result = ''
            temp_result = None
            time.sleep(2)
            while temp_result != '':

                temp_result = self.read_very_eager()
                result += temp_result

            # result = self.read_very_eager()
            self.last_result = self._clean_control_chars_from_terminal(result)
            self.last_result_stripped = self._clean_control_chars_from_terminal(self.strip_first_line(
                self.strip_last_line(result)))
            self.logger.info('read complete')
        else:
            self.logger.info('expecting pattern set')
            if len(patterns) == 0:
                patterns = self.default_prompt_set
            try:
                result = self.expect(patterns)
            except:
                self.last_pattern_index = -1
                try:
                    self.logger.debug(result[2])
                except:
                    self.logger.debug('unable to log result')
                return
            self.last_result = result[2]
            self.last_result_stripped = self.strip_first_line(self.strip_last_line(result[2]))
            self.last_pattern_index = result[0]
            self.logger.info('Expect complete')
            self.logger.info('Last Pattern Index: ' + str(self.last_pattern_index))
        self.logger.debug(self.last_result)
        self.logger.debug(self.last_result_stripped)

    def _clean_control_chars_from_terminal(self, result_buffer):
        return self.control_char_pattern.sub('', result_buffer)


class ComwareTelnetHandler(telnetlib.Telnet):

    default_prompt_set = ['\[.*]', '<.*>', 'Please press ENTER']
    last_result = ''
    last_result_stripped = ''
    last_pattern_index = -1

    control_char_pattern = re.compile('\\x1B.+?[HK]')

    def __init__(self, address, port=22, timeout=60, logger=None):

            if logger is None:
                logger = qs_logger.get_qs_logger('Provision Telnet')
            self.logger = logger

            logger.info('Initialize ProvisionTelnetHandler: {address=' + address + ' port=' + str(port) + ' timeout=' +
                        str(timeout))
            if timeout is 0:
                telnetlib.Telnet.__init__(self, address, port)
            else:
                telnetlib.Telnet.__init__(self, address, port, timeout)
            logger.info('Telnet Handler Initialized')

    def login(self, username='', password=''):

        self.logger.info('Logging in telnet handler')
        self.send_and_receive('\r\n')
        if self.last_pattern_index == -1:
            self.logger.error('Incorrect login result, no matching prompt')
            return -1
        if self.last_pattern_index == 2:
            self.logger.info('startup prompt found - sending newline')
            self.send_and_receive('\r\n')

        if self.last_pattern_index == 0:
            self.logger.info('ambiguous pattern found, geting to sys mode')
            count = 0
            while self.last_pattern_index != 1 and count < 10:
                self.send_and_receive('quit')
                count += 1
            self.send_and_receive('screen-length disable')
            self.send_and_receive('sys')
            if self.last_pattern_index != 0:
                self.logger.error('Unable to get to sys mode')
                return -1

        elif self.last_pattern_index == 1:
            self.logger.info('User mode prompt found, sending "sys"')
            self.send_and_receive('screen-length disable')
            self.send_and_receive('sys')
            if self.last_pattern_index != 0:
                self.logger.error('Failed to enter sys mode')
                return -1
        self.logger.info('Successful login')
        return 1

    def strip_last_line(self, content):
        try:
            return content.rsplit('\r\n', 1)[0]
        except IndexError:
            return content

    def strip_first_line(self, content):
        try:
            return content.split('\r\n', 1)[1]
        except IndexError:
            return content

    def clear_read_buffer(self):
        result = None

        while result != '':
            result = self.read_very_eager()

    def send_and_receive(self, line, use_pattern=True, patterns=[]):
        self.logger.info('sending "' + line + '" via telnet Handler')
        self.clear_read_buffer()
        self.last_result = ''
        self.last_result_stripped = ''
        self.last_pattern_index = -1
        if '\r\n' not in line:
            line += '\r\n'

        self.write(line)
        self.logger.info('Line sent')
        if not use_pattern:
            self.logger.info('Reading very eager')
            result = ''
            temp_result = None
            time.sleep(2)
            while temp_result != '':

                temp_result = self.read_very_eager()
                result += temp_result

            # result = self.read_very_eager()
            self.last_result = result
            self.last_result_stripped = self._clean_control_chars_from_terminal(self.strip_first_line(
                self.strip_last_line(result)))
            self.logger.info('read complete')
        else:
            self.logger.info('expecting pattern set')
            if len(patterns) == 0:
                patterns = self.default_prompt_set
            result = self.expect(patterns)
            self.last_result = result[2]
            self.last_result_stripped = self.strip_first_line(self.strip_last_line(result[2]))
            self.last_pattern_index = result[0]
            self.logger.info('Expect complete')
            self.logger.info('Last Pattern Index: ' + str(self.last_pattern_index))

        self.logger.debug(self.last_result)
        self.logger.debug(self.last_result_stripped)

    def _clean_control_chars_from_terminal(self, result_buffer):
        return self.control_char_pattern.sub('', result_buffer)
