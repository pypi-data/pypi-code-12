#
# otopi -- plugable installer
# Copyright (C) 2012-2014 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#


"""
Module implements machine dialog parser.
Please refer to README.dialog.
"""


import re
import six
from otopi import base
from otopi import util

NOTE_EVENT = 'note'
LOG_EVENT = 'log'
TERMINATE_EVENT = 'terminate'
QUERY_STRING_EVENT = 'query_string'
QUERY_MULTI_STRING_EVENT = 'query_multi_string'
QUERY_VALUE_EVENT = 'query_value'
CONFIRM_EVENT = 'confirm'
DISPLAY_VALUE_EVENT = 'display_value'
DISPLAY_MULTI_STRING_EVENT = 'display_multi_string'

TYPE_KEY = 'type'
REGEX_KEY = 'regex'
ATTRIBUTES_KEY = 'attributes'
REPLY_KEY = 'reply'
ABORT_KEY = 'abort'

TRANSLATION = (
    {
        TYPE_KEY: NOTE_EVENT,
        REGEX_KEY: re.compile(r'^#+ *(?P<note>.*)$'),
    },
    {
        TYPE_KEY: LOG_EVENT,
        REGEX_KEY: re.compile(
            r'^[*]{3}L:(?P<severity>[^ ]+) (?P<record>.*)$'
        ),
    },
    {
        TYPE_KEY: TERMINATE_EVENT,
        REGEX_KEY: re.compile(r'^[*]{3}TERMINATE$'),
    },
    {
        TYPE_KEY: QUERY_STRING_EVENT,
        REGEX_KEY: re.compile(r'^[*]{3}Q:STRING (?P<name>.*)$'),
    },
    {
        TYPE_KEY: QUERY_MULTI_STRING_EVENT,
        REGEX_KEY: re.compile(
            r'^[*]{3}Q:MULTI-STRING '
            r'(?P<name>[^ ]+) '
            r'(?P<boundary>[^ ]+) '
            r'(?P<abort_boundary>.+)$'
        ),
    },
    {
        TYPE_KEY: QUERY_VALUE_EVENT,
        REGEX_KEY: re.compile(r'^[*]{3}Q:VALUE (?P<name>.*)$'),
    },
    {
        TYPE_KEY: CONFIRM_EVENT,
        REGEX_KEY: re.compile(
            r'^[*]{3}CONFIRM (?P<what>[^ ]+) (?P<description>.*)$'
        ),
    },
    {
        TYPE_KEY: DISPLAY_VALUE_EVENT,
        REGEX_KEY: re.compile(
            r'^[*]{3}D:VALUE '
            r'(?P<name>[^=]+)='
            r'(?P<type>[^:]+):'
            r'(?P<value>.*)$'
        ),
    },
    {
        TYPE_KEY: DISPLAY_MULTI_STRING_EVENT,
        REGEX_KEY: re.compile(
            r'^[*]{3}D:MULTI-STRING (?P<name>[^ ]+) (?P<boundary>.*)$'
        ),
    },
)


class ParseError(Exception):
    pass


class UnexpectedEOF(ParseError):
    pass


class HeadDoesNotMatch(ParseError):
    pass


class DialogError(ParseError):
    pass


class UnexpectedEventError(DialogError):
    pass


@util.export
class MachineDialogParser(base.Base):
    """
    Machine dialog parser.
    """

    def __init__(self, input_=None, output=None):
        """
        Keyword arguments:
        input_ -- file like object
        output -- file like object
        """
        super(MachineDialogParser, self).__init__()
        self.output = None
        self.input_ = None
        self.set_streams(input_, output)

    def _write(self, data):
        """
        Writes data to output stream

        Keyword arguments:
        data -- string to be written
        """
        self.logger.debug("writing data {{{\n%s\n}}}", data)
        self.output.write(data)
        self.output.write('\n')
        self.output.flush()

    def next_line(self):
        """
        Returns next line from input
        """
        line = ""
        while True:
            char = self.input_.read(1)
            if char == '\r':
                continue
            if not char:
                if not line:
                    raise UnexpectedEOF()
                return line
            if char == '\n':
                return line
            line += char

    def set_streams(self, input_, output):
        self.input_ = input_
        self.output = output

    def next_event(self):
        """
        Returns instance of Event
        """
        line = self.next_line()
        for event_type in TRANSLATION:
            match = event_type[REGEX_KEY].match(line)
            if not match:
                continue
            event = dict(
                (
                    (TYPE_KEY, event_type[TYPE_KEY]),
                    (ATTRIBUTES_KEY, match.groupdict()),
                )
            )
            self._process_event(event_type[TYPE_KEY], event[ATTRIBUTES_KEY])
            self.logger.debug("Next event: %s", event)
            return event
        # W/A for hosted-engine deploy job
        self.logger.warning("This line doesn't match no event: %s", line)

    def _process_event(self, event_type, attributes):
        if event_type == DISPLAY_VALUE_EVENT:
            type_ = attributes['type'].lower()
            if type_ == 'none':
                attributes['value'] = None
            elif type_ == 'str':
                attributes['value'] = str(attributes['value'])
            elif type_ == 'int':
                attributes['value'] = int(attributes['value'])
            elif type_ == 'bool':
                attributes['value'] = attributes['value'].lower() == "true"
            else:
                raise TypeError(
                    "Unexpected type of %s.value: '%s'" % (
                        DISPLAY_VALUE_EVENT,
                        attributes['value']
                    )
                )

        if event_type == DISPLAY_MULTI_STRING_EVENT:
            lines = []
            while True:
                line = self.next_line()
                if line != attributes['boundary']:
                    lines.append(line)
                else:
                    break
            attributes['value'] = lines

    def send_response(self, event):
        """
        Sends response for replyable events.

        :param event: instance of replyable event
        """
        self.logger.debug("Response for: %s", event)
        self._write(self._send_response(event))

    @staticmethod
    def _send_response(event):
        type_ = event[TYPE_KEY]
        if type_ == QUERY_STRING_EVENT:
            reply = event[REPLY_KEY]
            if not isinstance(reply, six.string_types) or '\n' in reply:
                raise TypeError(
                    "QueryString.value must be single-line string, "
                    "got: %s" % reply
                )
            return reply
        elif type_ == QUERY_MULTI_STRING_EVENT:
            if event.get(ABORT_KEY, False):
                return event[ATTRIBUTES_KEY]['abort_boundary']
            lines = '\n'.join(event.get(REPLY_KEY, list()))
            if lines:
                return "%s\n%s" % (lines, event[ATTRIBUTES_KEY]['boundary'])
            return event[ATTRIBUTES_KEY]['boundary']
        elif type_ == QUERY_VALUE_EVENT:
            if event.get(ABORT_KEY, False):
                return "ABORT %s" % event[ATTRIBUTES_KEY]['name']
            reply = event[REPLY_KEY]
            value_type = type(reply).__name__
            if value_type == 'NoneType':
                value_type = 'none'
            if value_type == 'str' and '\n' in reply:
                raise TypeError(
                    ("String '%s' should not contain new lines" %
                        event[ATTRIBUTES_KEY]['name']
                     )
                )
            if value_type not in ('none', 'str', 'bool', 'int'):
                raise TypeError("Invalid type of value: %s" % value_type)
            return "VALUE %s=%s:%s" % (
                event[ATTRIBUTES_KEY]['name'],
                value_type,
                reply
            )
        elif type_ == CONFIRM_EVENT:
            if event.get(ABORT_KEY, False):
                return "ABORT %s" % event[ATTRIBUTES_KEY]['what']
            reply = "yes" if event.get(REPLY_KEY, False) else "no"
            return "CONFIRM %s=%s" % (event[ATTRIBUTES_KEY]['what'], reply)
        else:
            raise TypeError("%s is not replayable" % type_)

    # NOTE: all these methods doesn't fit here,
    # I would move it to separate class.
    def cli_env_get(self, key):
        """
        Get value of environment variable

        :param key: name of variable
        :type key: str
        :return: returns value for environment variable
        :rtype: str
        """
        cmd = 'env-get -k %s' % key
        self._write(cmd)

        event = self.next_event()
        if event[TYPE_KEY] not in (
            DISPLAY_VALUE_EVENT,
            DISPLAY_MULTI_STRING_EVENT,
        ):
            raise UnexpectedEventError(event)
        return event[ATTRIBUTES_KEY]['value']

    def cli_env_set(self, key, value):
        """
        Sets given value for given environment variable

        :param key: name of variable
        :type key: str
        :param value: value to be set
        :type value: str
        """
        cmd = 'env-query'
        if isinstance(value, (list, tuple)):
            cmd += '-multi'
        cmd += " -k %s" % key
        self._write(cmd)

        event = self.next_event()
        if event[TYPE_KEY] not in (
            QUERY_STRING_EVENT,
            QUERY_MULTI_STRING_EVENT,
            QUERY_VALUE_EVENT,
        ):
            raise UnexpectedEventError(event)
        event[REPLY_KEY] = value
        self.send_response(event)

    def cli_download_log(self):
        """
        Returns log
        """
        self._write('log')
        event = self.next_event()
        if event[TYPE_KEY] == DISPLAY_MULTI_STRING_EVENT:
            return '\n'.join(event[ATTRIBUTES_KEY]['value']) + '\n'
        raise UnexpectedEventError(event)

    def cli_noop(self):
        """
        noop command
        """
        self._write('noop')

    def cli_quit(self):
        """
        quit command
        """
        self._write('quit')

    def cli_install(self):
        """
        install command
        """
        self._write('install')

    def cli_abort(self):
        """
        abort command
        """
        self._write('abort')
