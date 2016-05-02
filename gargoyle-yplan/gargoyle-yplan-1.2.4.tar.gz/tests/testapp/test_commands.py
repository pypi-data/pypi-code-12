from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from gargoyle.management.commands.add_switch import Command as AddSwitchCmd
from gargoyle.management.commands.remove_switch import Command as RemoveSwitchCmd
from gargoyle.manager import SwitchManager
from gargoyle.models import DISABLED, GLOBAL, Switch


class CommandAddSwitchTestCase(TestCase):

    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)

    def test_requires_single_arg(self):
        too_few_too_many = [
            [],
            ['one', 'two'],
        ]
        for args in too_few_too_many:
            command = AddSwitchCmd()

            with pytest.raises(CommandError):
                command.handle(*args)

    def test_add_switch_default_status(self):
        assert 'switch_default' not in self.gargoyle

        call_command('add_switch', 'switch_default')

        assert 'switch_default' in self.gargoyle
        assert GLOBAL == self.gargoyle['switch_default'].status

    def test_add_switch_with_status(self):
        assert 'switch_disabled' not in self.gargoyle

        call_command('add_switch', 'switch_disabled', status=DISABLED)

        assert 'switch_disabled' in self.gargoyle
        assert DISABLED == self.gargoyle['switch_disabled'].status

    def test_update_switch_status_disabled(self):
        Switch.objects.create(key='test', status=GLOBAL)
        assert GLOBAL == self.gargoyle['test'].status

        call_command('add_switch', 'test', status=DISABLED)

        assert DISABLED == self.gargoyle['test'].status

    def test_update_switch_status_to_default(self):
        Switch.objects.create(key='test', status=DISABLED)
        assert DISABLED == self.gargoyle['test'].status

        call_command('add_switch', 'test')

        assert GLOBAL == self.gargoyle['test'].status


class CommandRemoveSwitchTestCase(TestCase):

    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)

    def test_requires_single_arg(self):
        too_few_too_many = [
            [],
            ['one', 'two'],
        ]
        for args in too_few_too_many:
            command = RemoveSwitchCmd()

            with pytest.raises(CommandError):
                command.handle(*args)

    def test_removes_switch(self):
        Switch.objects.create(key='test')
        assert 'test' in self.gargoyle

        call_command('remove_switch', 'test')

        assert 'test' not in self.gargoyle

    def test_remove_non_switch_doesnt_error(self):
        assert 'idontexist' not in self.gargoyle

        call_command('remove_switch', 'idontexist')

        assert 'idontexist' not in self.gargoyle
