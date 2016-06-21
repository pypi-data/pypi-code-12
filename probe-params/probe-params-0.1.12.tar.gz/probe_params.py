#!/usr/bin/env python

from cleo import Command, InputArgument, InputOption
from cleo import Application
from probe.params import SimParams
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(logging.StreamHandler())


class PrintParamsCommand(Command):
    name = 'params:print'

    description = 'loads an input.params file and print all parameters'

    arguments = [
        {
            'name': 'input',
            'description': 'path to input.params file',
            'required': True
        }
    ]

    options = [
        {
            'name': 'debye_fraction_user',
            'shortcut': 'f',
            'description': 'integer, how many grid points per one Debye length',
            'value_required': True,
            'default': None,
        }
    ]

    @staticmethod
    def execute(i, o):
        input_arg = i.get_argument('input')
        debye_fraction_user = i.get_option('debye_fraction_user')
        if debye_fraction_user:
            debye_fraction_user = int(debye_fraction_user)

        sp = SimParams(input_arg, debye_fraction_user=debye_fraction_user)

        sp.print_params('params')
        sp.print_sparams('sparams')
        sp.print_cparams('cparams')


class PrepareSimCommand(Command):
    name = 'params:prepare_sim'

    description = 'loads params.cfg and creates sim.h5 with common_0000 group set'

    options = [
        {
            'name': 'cfg',
            'shortcut': 'f',
            'description': 'path to params.cfg [default: params.cfg]',
            'value_required': True,
            'default': 'params.cfg',
        },
        {
            'name': 'h5file',
            'shortcut': 'i',
            'description': 'name of h5 file [default: sim.h5]',
            'value_required': True,
            'default': 'sim.h5',
        },
        {
            'name': 'group-number',
            'shortcut': 'u',
            'description': 'number of common group that will be created [default: 0]',
            'value_required': True,
            'default': 0,
        }
    ]

    @staticmethod
    def execute(i, o):
        params_cfg = i.get_option('cfg')
        h5file = i.get_option('h5file')
        group_number = int(i.get_option('group-number'))
        sp = SimParams(params_cfg)
        sp.prepare_sim(h5file=h5file, groupno=group_number)


class ConvertInputParamsCommand(Command):
    name = 'params:convert_input_params'

    description = 'transform old input.params into new params.cfg'

    options = [
        {
            'name': 'input_params',
            'shortcut': 'i',
            'description': 'path to input.params',
            'value_required': True,
            'default': 'input.params',
        },
        {
            'name': 'params_cfg',
            'shortcut': 'p',
            'description': 'save params.cfg as',
            'value_required': True,
            'default': 'params.cfg',
        },
    ]

    @staticmethod
    def execute(i, o):
        input_params = i.get_option('input_params')
        params_cfg = i.get_option('params_cfg')
        new_params = SimParams.convert_input_params(input_params)


if __name__ == '__main__':
    application = Application()
    application.add(PrintParamsCommand())
    application.add(PrepareSimCommand())
    application.add(ConvertInputParamsCommand())
    application.run()
