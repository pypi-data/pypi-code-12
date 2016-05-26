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


import six
from otopi import base
from otopi import util
from otopimdp import errors
from otopimdp import constants as c
from otopimdp import utils


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
                    raise errors.UnexpectedEOF()
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
        return self._next_event()

    def _next_event(self, line=None):
        if not line:
            line = self.next_line()
        for event_type in c.TRANSLATION:
            match = event_type[c.REGEX_KEY].match(line)
            if not match:
                continue
            event = dict(
                (
                    (c.TYPE_KEY, event_type[c.TYPE_KEY]),
                    (c.ATTRIBUTES_KEY, match.groupdict()),
                )
            )
            self._process_event(event)
            self.logger.debug("Next event: %s", event)
            return event
        # W/A for hosted-engine deploy job
        self.logger.warning("This line doesn't match no event: %s", line)

    def _process_event(self, event):
        event_type = event[c.TYPE_KEY]
        attributes = event[c.ATTRIBUTES_KEY]

        if event_type == c.DISPLAY_VALUE_EVENT:
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
                        c.DISPLAY_VALUE_EVENT,
                        attributes['value']
                    )
                )

        if event_type == c.DISPLAY_MULTI_STRING_EVENT:
            lines = []
            while True:
                line = self.next_line()
                if line != attributes['boundary']:
                    lines.append(line)
                else:
                    break
            attributes['value'] = lines

        if event_type == c.QUERY_FRAME_EVENT:
            self._process_frame_event(event)

    def _process_frame_event(self, event):
        attributes = event[c.ATTRIBUTES_KEY]
        framed_event = None
        while True:
            line = self.next_line()
            m = c.QUERY_FRAME_PATTERNS[c.QUERY_FRAME_PART_END].match(line)
            if m:
                if m.group(c.FRAME_NAME_KEY) != attributes[c.FRAME_NAME_KEY]:
                    self.logger.warning(
                        "The QStart:NAME != QEnd:NAME (%s != %s)",
                        m.group(c.FRAME_NAME_KEY),
                        attributes[c.FRAME_NAME_KEY],
                    )
                break
            m = c.QUERY_FRAME_PATTERNS[c.QUERY_FRAME_PART_DEFAULT].match(line)
            if m:
                attributes[c.DEFAULT_KEY] = m.group(c.DEFAULT_KEY)
                continue
            m = c.QUERY_FRAME_PATTERNS[c.QUERY_FRAME_PART_HIDDEN].match(line)
            if m:
                if m.group(c.HIDDEN_KEY) == "TRUE":
                    attributes[c.HIDDEN_KEY] = True
                elif m.group(c.HIDDEN_KEY) == "FALSE":
                    attributes[c.HIDDEN_KEY] = False
                else:
                    self.logger.warning(
                        "The QHidden(%s) has invalid option: "
                        "%s not in (TRUE, FALSE)",
                        attributes[c.FRAME_NAME_KEY],
                        m.group(c.HIDDEN_KEY),
                    )
                    attributes[c.HIDDEN_KEY] = False
                continue
            m = c.QUERY_FRAME_PATTERNS[
                c.QUERY_FRAME_PART_VALID_VALUES
            ].match(line)
            if m:
                attributes[c.VALID_VALUES_KEY] = utils.split_valid_options(
                    m.group('valid')
                )
                continue

            framed_event = self._next_event(line)
            if framed_event is None:
                raise errors.UnexpectedInputError(
                    c.QUERY_FRAME_EVENT, attributes, line,
                )

            event[c.ATTRIBUTES_KEY].update(framed_event[c.ATTRIBUTES_KEY])
            event[c.TYPE_KEY] = framed_event[c.TYPE_KEY]

        if framed_event is None:
            raise errors.IncompleteQueryFrameError(
                "The frame %s doesn't contain query.",
                event,
            )

    def send_response(self, event):
        """
        Sends response for replyable events.

        :param event: instance of replyable event
        """
        self.logger.debug("Response for: %s", event)
        self._write(self._send_response(event))

    @staticmethod
    def _send_response(event):
        type_ = event[c.TYPE_KEY]
        if type_ == c.QUERY_STRING_EVENT:
            reply = event[c.REPLY_KEY]
            if not isinstance(reply, six.string_types) or '\n' in reply:
                raise TypeError(
                    "QueryString.value must be single-line string, "
                    "got: %s" % reply
                )
            return reply
        elif type_ == c.QUERY_MULTI_STRING_EVENT:
            if event.get(c.ABORT_KEY, False):
                return event[c.ATTRIBUTES_KEY]['abort_boundary']
            lines = '\n'.join(event.get(c.REPLY_KEY, list()))
            if lines:
                return "%s\n%s" % (lines, event[c.ATTRIBUTES_KEY]['boundary'])
            return event[c.ATTRIBUTES_KEY]['boundary']
        elif type_ == c.QUERY_VALUE_EVENT:
            if event.get(c.ABORT_KEY, False):
                return "ABORT %s" % event[c.ATTRIBUTES_KEY]['name']
            reply = event[c.REPLY_KEY]
            value_type = type(reply).__name__
            if value_type == 'NoneType':
                value_type = 'none'
            if value_type == 'str' and '\n' in reply:
                raise TypeError(
                    ("String '%s' should not contain new lines" %
                        event[c.ATTRIBUTES_KEY]['name']
                     )
                )
            if value_type not in ('none', 'str', 'bool', 'int'):
                raise TypeError("Invalid type of value: %s" % value_type)
            return "VALUE %s=%s:%s" % (
                event[c.ATTRIBUTES_KEY]['name'],
                value_type,
                reply
            )
        elif type_ == c.CONFIRM_EVENT:
            if event.get(c.ABORT_KEY, False):
                return "ABORT %s" % event[c.ATTRIBUTES_KEY]['what']
            reply = "yes" if event.get(c.REPLY_KEY, False) else "no"
            return "CONFIRM %s=%s" % (event[c.ATTRIBUTES_KEY]['what'], reply)
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
        if event[c.TYPE_KEY] not in (
            c.DISPLAY_VALUE_EVENT,
            c.DISPLAY_MULTI_STRING_EVENT,
        ):
            raise errors.UnexpectedEventError(event)
        return event[c.ATTRIBUTES_KEY]['value']

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
        if event[c.TYPE_KEY] not in (
            c.QUERY_STRING_EVENT,
            c.QUERY_MULTI_STRING_EVENT,
            c.QUERY_VALUE_EVENT,
        ):
            raise errors.UnexpectedEventError(event)
        event[c.REPLY_KEY] = value
        self.send_response(event)

    def cli_download_log(self):
        """
        Returns log
        """
        self._write('log')
        event = self.next_event()
        if event[c.TYPE_KEY] == c.DISPLAY_MULTI_STRING_EVENT:
            return '\n'.join(event[c.ATTRIBUTES_KEY]['value']) + '\n'
        raise errors.UnexpectedEventError(event)

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
