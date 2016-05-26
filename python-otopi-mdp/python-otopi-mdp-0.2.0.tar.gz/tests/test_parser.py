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


import sys
import logging
import unittest
import six
import pytest
from otopimdp.parser import MachineDialogParser
from otopimdp import constants as c
from otopimdp import errors as e


class MachineDialogParserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def create_parser(self, data, output=sys.stdout):
        input_ = six.StringIO()
        input_.write(data)
        input_.seek(0)
        parser = MachineDialogParser()
        parser.set_streams(input_, output)
        return parser

    def _compare_outputs(self, out, expected):
        out.seek(0)
        self.assertEqual(expected, out.read())

    def _expect_note(self, event, msg=None):
        self.assertEqual(event[c.TYPE_KEY], c.NOTE_EVENT)
        if msg is not None:
            self.assertEqual(event[c.ATTRIBUTES_KEY]['note'], msg)

    def _expect_log(self, event, msg=None, severity=None):
        self.assertTrue(event[c.TYPE_KEY], c.LOG_EVENT)
        if msg is not None:
            self.assertEqual(event[c.ATTRIBUTES_KEY]['record'], msg)
        if severity is not None:
            self.assertEqual(event[c.ATTRIBUTES_KEY]['severity'], severity)

    def _expect_query(self, type_, event, name=None):
        self.assertEqual(event[c.TYPE_KEY], type_)
        if name is not None:
            self.assertEqual(name, event[c.ATTRIBUTES_KEY]['name'])

    def _expect_qstring(self, event, name=None):
        self._expect_query(c.QUERY_STRING_EVENT, event, name)

    def _expect_qmstring(self, event, name=None):
        self._expect_query(c.QUERY_MULTI_STRING_EVENT, event, name)

    def _expect_qvalue(self, event, name=None):
        self._expect_query(c.QUERY_VALUE_EVENT, event, name)

    def _expect_dvalue(self, event, name=None):
        self._expect_query(c.DISPLAY_VALUE_EVENT, event, name)

    def _expect_dmstring(self, event, name=None):
        self._expect_query(c.DISPLAY_MULTI_STRING_EVENT, event, name)

    def _expect_confirm(self, event, what=None, dscr=None):
        self.assertEqual(event[c.TYPE_KEY], c.CONFIRM_EVENT)
        if what is not None:
            self.assertEqual(what, event[c.ATTRIBUTES_KEY]['what'])
        if dscr is not None:
            self.assertEqual(dscr, event[c.ATTRIBUTES_KEY]['description'])

    def _expect_terminate(self, event):
        self.assertEqual(event[c.TYPE_KEY], c.TERMINATE_EVENT)

    def test_basic(self):
        data = (
            "***TERMINATE\n"
        )
        expected_output = ""
        out = six.StringIO()
        parser = self.create_parser(data, out)
        event = parser.next_event()
        self._expect_terminate(event)
        self.assertEqual(expected_output, out.read())

    def test_invalid_token1(self):
        data = "XXX"
        parser = self.create_parser(data)
        assert parser.next_event() is None

    def test_invalid_token2(self):
        data = "***Q:STRING1 hello\n"
        parser = self.create_parser(data)
        assert parser.next_event() is None

    def test_invalid_token3(self):
        data = "***Q:MUTLI-STRING hello\n"
        parser = self.create_parser(data)
        assert parser.next_event() is None

    def test_note_event(self):
        expected_msg = "Some nice comment"
        data = "### %s\n" % expected_msg
        expected_output = ""
        out = six.StringIO()
        parser = self.create_parser(data, out)
        event = parser.next_event()
        self._expect_note(event, expected_msg)
        self.assertEqual(expected_output, out.read())

    def test_log_event(self):
        expected_msg = "Some nice comment"
        data = "***L:INFO %s\n" % expected_msg
        expected_output = ""
        out = six.StringIO()
        parser = self.create_parser(data, out)
        event = parser.next_event()
        self._expect_log(event, expected_msg, 'INFO')
        self.assertEqual(expected_output, out.read())

    def test_coverage(self):
        data = (
            "#NOTE\n"
            "#### NOTE\n"
            "***L:DEBUG log record\n"
            "***L:INFO log record\n"
            "***L:WARNING log record\n"
            "***L:ERROR log record\n"
            "***L:CRITICAL log record\n"
            "***L:FATAL log record\n"
            "#INFO\n"
            "***Q:STRING str1\n"
            "***Q:MULTI-STRING mstr0 boundary1 boundary2\n"
            "***Q:MULTI-STRING mstr1 boundary1 boundary2\n"
            "***Q:MULTI-STRING mstr2 boundary1 boundary2\n"
            "***Q:VALUE value0\n"
            "***Q:VALUE value1\n"
            "***Q:VALUE value2\n"
            "***Q:VALUE value3\n"
            "***Q:VALUE value4\n"
            "***Q:VALUE value5\n"
            "***D:VALUE value10=none:NoneType\n"
            "***D:VALUE value11=bool:True\n"
            "***D:VALUE value12=bool:False\n"
            "***D:VALUE value13=int:52\n"
            "***D:VALUE value14=str:value 2\n"
            "***D:MULTI-STRING mstr3 boundary2\n"
            "line 1\n"
            "line 2\n"
            "boundary2\n"
            "***CONFIRM confirm0 description 0\n"
            "***CONFIRM confirm1 description 1\n"
            "***CONFIRM confirm2 description 1\n"
            "**%QStart: MyFrame\n"
            "**%QHidden: FALSE\n"
            "***Q:VALUE value20\n"
            "**%QDefault: one\n"
            "**%QValidValues: one|two|three\n"
            "**%QEnd: MyFrame\n"
            "***TERMINATE\n"
        )

        expected_output = (
            "value 1\n"
            "boundary2\n"
            "line 1\n"
            "line 2\n"
            "boundary1\n"
            "boundary1\n"
            "ABORT value0\n"
            "VALUE value1=none:None\n"
            "VALUE value2=bool:True\n"
            "VALUE value3=bool:False\n"
            "VALUE value4=int:47\n"
            "VALUE value5=str:string 1\n"
            "ABORT confirm0\n"
            "CONFIRM confirm1=no\n"
            "CONFIRM confirm2=yes\n"
            "VALUE value20=str:two\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_note(event, "NOTE")
        event = parser.next_event()
        self._expect_note(event, "NOTE")

        severities = (
            'DEBUG',
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL',
            'FATAL'
        )
        for severity in severities:
            event = parser.next_event()
            self._expect_log(event, 'log record', severity)

        event = parser.next_event()
        self._expect_note(event, "INFO")

        event = parser.next_event()
        self._expect_qstring(event, 'str1')
        event[c.REPLY_KEY] = "value 1"
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qmstring(event, 'mstr0')
        event[c.ABORT_KEY] = True
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qmstring(event, 'mstr1')
        event[c.REPLY_KEY] = ["line 1", 'line 2']
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qmstring(event, 'mstr2')
        event[c.REPLY_KEY] = []
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value0')
        event[c.ABORT_KEY] = True
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value1')
        event[c.REPLY_KEY] = None
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value2')
        event[c.REPLY_KEY] = True
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value3')
        event[c.REPLY_KEY] = False
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value4')
        event[c.REPLY_KEY] = 47
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value5')
        event[c.REPLY_KEY] = "string 1"
        parser.send_response(event)

        event = parser.next_event()
        self._expect_dvalue(event, 'value10')
        self.assertEqual(None, event[c.ATTRIBUTES_KEY]['value'])

        event = parser.next_event()
        self._expect_dvalue(event, 'value11')
        self.assertEqual(True, event[c.ATTRIBUTES_KEY]['value'])

        event = parser.next_event()
        self._expect_dvalue(event, 'value12')
        self.assertEqual(False, event[c.ATTRIBUTES_KEY]['value'])

        event = parser.next_event()
        self._expect_dvalue(event, 'value13')
        self.assertEqual(52, event[c.ATTRIBUTES_KEY]['value'])

        event = parser.next_event()
        self._expect_dvalue(event, 'value14')
        self.assertEqual("value 2", event[c.ATTRIBUTES_KEY]['value'])

        event = parser.next_event()
        self._expect_dmstring(event, 'mstr3')
        self.assertEqual(
            ['line 1', 'line 2'],
            event[c.ATTRIBUTES_KEY]['value']
        )

        event = parser.next_event()
        self._expect_confirm(event, 'confirm0', 'description 0')
        event[c.ABORT_KEY] = True
        parser.send_response(event)

        event = parser.next_event()
        self._expect_confirm(event, 'confirm1', 'description 1')
        parser.send_response(event)

        event = parser.next_event()
        self._expect_confirm(event, 'confirm2', 'description 1')
        event[c.REPLY_KEY] = True
        parser.send_response(event)

        event = parser.next_event()
        self._expect_qvalue(event, 'value20')
        assert event[c.ATTRIBUTES_KEY][c.FRAME_NAME_KEY] == 'MyFrame'
        assert not event[c.ATTRIBUTES_KEY][c.HIDDEN_KEY]
        assert event[c.ATTRIBUTES_KEY][c.DEFAULT_KEY] == 'one'
        assert event[c.ATTRIBUTES_KEY][c.VALID_VALUES_KEY] == [
            'one', 'two', 'three',
        ]
        event[c.REPLY_KEY] = "two"
        parser.send_response(event)

        event = parser.next_event()
        self._expect_terminate(event)

        self._compare_outputs(out, expected_output)

    def test_empty_qframe(self):
        data = (
            "**%QStart: MyFrame\n"
            "**%QHidden: FALSE\n"
            "**%QDefault: one\n"
            "**%QValidValues: one|two|three\n"
            "**%QEnd: MyFrame\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        with pytest.raises(e.IncompleteQueryFrameError):
            parser.next_event()

    def test_unpaired_name_of_qframe(self):
        data = (
            "**%QStart: MyFrame\n"
            "**%QHidden: FALSE\n"
            "***Q:VALUE value1\n"
            "**%QDefault: one\n"
            "**%QValidValues: one|two|three\n"
            "**%QEnd: MyFrame2\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        assert event[c.ATTRIBUTES_KEY][c.FRAME_NAME_KEY] == "MyFrame"

    def test_invalid_hiden_attribute_in_qframe(self):
        data = (
            "**%QStart: MyFrame\n"
            "**%QHidden: something\n"
            "***Q:VALUE value1\n"
            "**%QDefault: one\n"
            "**%QValidValues: one|two|three\n"
            "**%QEnd: MyFrame\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        assert not event[c.ATTRIBUTES_KEY][c.HIDDEN_KEY]

    def test_true_hiden_attribute_in_qframe(self):
        data = (
            "**%QStart: MyFrame\n"
            "**%QHidden: TRUE\n"
            "***Q:VALUE value1\n"
            "**%QDefault: one\n"
            "**%QValidValues: one|two|three\n"
            "**%QEnd: MyFrame\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        assert event[c.ATTRIBUTES_KEY][c.HIDDEN_KEY]

    def test_wrong_framed_event(self):
        data = (
            "**%QStart: MyFrame\n"
            "**%QHidden: TRUE\n"
            "something wrong\n"
            "**%QDefault: one\n"
            "**%QValidValues: one|two|three\n"
            "**%QEnd: MyFrame\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        with pytest.raises(e.UnexpectedInputError):
            parser.next_event()

    def test_return_character(self):
        data = (
            "#NOTE\r\n"
            "#### NOTE\r\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_note(event, "NOTE")
        event = parser.next_event()
        self._expect_note(event, "NOTE")

    def test_unexpected_end(self):
        data = ""
        out = six.StringIO()
        parser = self.create_parser(data, out)

        with pytest.raises(e.UnexpectedEOF):
            parser.next_event()

    def test_wrong_input(self):
        data = (
            "some wrong input data\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        # I am not sure whether it is good behav ...
        assert parser.next_event() is None

    def test_wrong_data_type(self):
        data = (
            "***D:VALUE value11=WRONG:True\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        with pytest.raises(TypeError):
            parser.next_event()

    def test_wrong_reply(self):
        data = (
            "***Q:STRING str1\n"
            "#### NOTE\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        # NEW LINE IN RESPONSE
        event[c.REPLY_KEY] = "multiline\nreply"
        with pytest.raises(TypeError):
            parser.send_response(event)

        # NOT STRING
        event[c.REPLY_KEY] = 1
        with pytest.raises(TypeError):
            parser.send_response(event)

        event = parser.next_event()
        # CAN NOT REPLY FOR NOTE
        with pytest.raises(TypeError):
            parser.send_response(event)

    def test_cli_log(self):
        data = (
            "***Q:STRING prompt\n" +
            "***D:MULTI-STRING log boundary1\n" +
            "line 1\n" +
            "line 2\n" +
            "boundary1\n" +
            "***TERMINATE\n"
        )

        expected_output = "log\n"

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        self.assertEqual(parser.cli_download_log(), "line 1\nline 2\n")

        event = parser.next_event()
        self._expect_terminate(event)

        self._compare_outputs(out, expected_output)

    def test_cli_evn_get(self):
        data = (
            "***Q:STRING prompt\n"
            "***D:VALUE key1=str:value1\n"
            "***Q:STRING prompt\n"
            "***D:MULTI-STRING key2 boundary1\n"
            "line 1\n"
            "line 2\n"
            "boundary1\n"
            "***Q:STRING prompt\n"
            "***TERMINATE\n"
        )

        expected_output = (
            "env-get -k key1\n"
            "env-get -k key2\n"
            "env-get -k something\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        value = parser.cli_env_get('key1')
        self.assertEqual(value, "value1")

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        value = parser.cli_env_get('key2')
        self.assertEqual(value, ['line 1', 'line 2'])

        with pytest.raises(e.UnexpectedEventError):
            parser.cli_env_get("something")

        event = parser.next_event()
        self._expect_terminate(event)

        self._compare_outputs(out, expected_output)

    def test_cli_evn_set(self):
        data = (
            "***Q:STRING prompt\n"
            "***Q:VALUE key1\n"
            "***Q:STRING prompt\n"
            "***Q:MULTI-STRING key2 boundary1 boundary2\n"
            "***D:VALUE key1=str:value1\n"
            "***TERMINATE\n"
        )

        expected_output = (
            "env-query -k key1\n"
            "VALUE key1=str:value 1\n"
            "env-query-multi -k key2\n"
            "line 1\n"
            "line 2\n"
            "boundary1\n"
            "env-query -k something\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_qstring(event, "prompt")
        parser.cli_env_set('key1', 'value 1')

        event = parser.next_event()
        self._expect_qstring(event, "prompt")
        parser.cli_env_set('key2', ['line 1', 'line 2'])

        with pytest.raises(e.UnexpectedEventError):
            parser.cli_env_set("something", "else")

        event = parser.next_event()
        self._expect_terminate(event)

        self._compare_outputs(out, expected_output)

    def test_cli_evn_set_invalid_type(self):
        data = (
            "***Q:STRING prompt\n"
            "***Q:VALUE key1\n"
        )

        expected_output = "env-query -k key1\n"

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        self.assertRaises(TypeError, parser.cli_env_set, "key1", self)

        self._compare_outputs(out, expected_output)

    def test_cli_evn_set_invalid_string(self):
        data = (
            "***Q:STRING prompt\n"
            "***Q:VALUE key1\n"
        )

        expected_output = "env-query -k key1\n"

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        self.assertRaises(
            TypeError,
            parser.cli_env_set, "key1",
            "test\nwith new line"
        )

        self._compare_outputs(out, expected_output)

    def test_misc_cli(self):
        data = (
            "***Q:STRING prompt\n"
            "***Q:STRING prompt\n"
            "***Q:STRING prompt\n"
            "***Q:STRING prompt\n"
            "***TERMINATE\n"
        )

        expected_output = (
            "install\n"
            "quit\n"
            "abort\n"
            "noop\n"
        )

        out = six.StringIO()
        parser = self.create_parser(data, out)

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        parser.cli_install()

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        parser.cli_quit()

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        parser.cli_abort()

        event = parser.next_event()
        self._expect_qstring(event, 'prompt')
        parser.cli_noop()

        event = parser.next_event()
        self._expect_terminate(event)

        self._compare_outputs(out, expected_output)

    def test_wrong_log(self):
        data = (
            "***Q:VALUE value0\n"
        )

        expected_output = (
            "log\n"
        )
        out = six.StringIO()
        parser = self.create_parser(data, out)

        with pytest.raises(e.UnexpectedEventError):
            parser.cli_download_log()

        self._compare_outputs(out, expected_output)


# vim: expandtab tabstop=4 shiftwidth=4
