__author__ = 'ziky'

import cleo
import h5py
from sim_params import SimParams

class PrintParamsCommand(cleo.Command):
    name = 'params:test'

    description = 'run test'

    arguments = [
        {
            'name': 'h5file',
            'description': 'path to h5 file file',
            'required': True
        },
    ]

    options = [
        {
            'name': 'h5file',
            'description': 'path to h5 file file [default: sim.h5]',
            'value_required': True,
            'default': 'sim.h5',
        },
        {
            'name': 'cfg',
            'shortcut': 'f',
            'description': 'path to params.cfg [default: params.cfg]',
            'value_required': True,
            'default': 'params.cfg',
        },
        {
            'name': 'test_type',
            'shortcut': 't',
            'description': 'test type: {params_loading,} [default: params_loading]',
            'value_required': True,
            'default': 'params_loading',
        },
    ]

    @staticmethod
    def execute(i, o):
        h5file = i.get_argument('h5file')
        cfg = i.get_argument('cfg')
        test_type = i.get_option('test_type')

        assert test_type in ['params_loading']

        if test_type == 'params_loading':

            f = h5py.File(h5file, is_old_input_type='False', )
            params_h5 = f['/common_0000'].attrs
            params_cfg = SimParams()