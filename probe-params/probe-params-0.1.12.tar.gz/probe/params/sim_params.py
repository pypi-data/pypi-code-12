import consts
from math import sqrt, exp, erf, pi, log
import logging
import subprocess
import os
import ConfigParser
import tempfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SimParams(object):

    INPUT_PARAMS_LINES = {
        0: 'r_p',
        1: 'profile_type',
        2: 'r_d',
        3: 'geom',
        5: 'pressure',
        6: 'T_g',
        7: 'T_e',
        8: 'T_i',
        9: 'n_e',
        10: 'phi_p',
        11: 'phi_d',
        12: 'dr',
        13: 'I', #Steady state current
        14: 'dt',
        15: 'NSP',
        16: 'ntimes',
        17: 'out_every',
        18: 'ions',
    }

    GEOM_TYPES = {
        1: 'spherical',
        2: 'cylindrical',
        3: 'planar',
    }

    CFG2INPUT = {
        ('domain', 'r_p'): 'r_p',
        ('domain', 'r_d'): 'r_d',
        ('domain', 'geom'): 'geom',
        ('domain', 'phi_p'): 'phi_p',
        ('domain', 'phi_d'): 'phi_d',

        ('init', 'profile_type'): 'profile_type',

        ('plasma', 'T_e'): 'T_e',
        ('plasma', 'T_i'): 'T_i',
        ('plasma', 'n_0'): 'n_e',

        ('gas', 'pressure'): 'pressure',
        ('gas', 'T_g'): 'T_g',

        ('simulation', 'dt'): 'dt',
        ('simulation', 'dr'): 'dr',
        ('simulation', 'NSP'): 'NSP',
        ('simulation', 'Ntimes'): 'ntimes',
        ('simulation', 'out_every'): 'out_every',
        ('simulation', 'every_ions'): 'ions',

        ('drift', 'I_e'): 'I',
    }

    CFG2INPUT_DEFAULT = {
        ('domain', 'surface_sheath'): 1.0,

        ('drift', 'I_i'): 0.0,

        ('stats', 'global'): 1,
        ('stats', 'local'): 1,

        ('sweep', 'sweep'): 0,
        ('sweep', 'sweep_period'): 0,
        ('sweep', 'sweep_start'): 0,
        ('sweep', 'sweep_stop'): 0,

        ('boundary', 'reflecting_probe'): 0,
        ('boundary', 'boundary_condition_type'): 0,

        ('hist', 'HIST_NEW_PARTICLES'): 0,
        ('hist', 'HIST_PROBE_PARTICLES'): 0,
        ('hist', 'HIST_SHEATH_PARTICLES'): 0,
    }

    @staticmethod
    def convert_input_params(input_params='input.params', params_cfg='params.cfg'):
        params = SimParams.read_params_from_inputparams(input_params)
        input2cfg = SimParams.input2cfg()
        new_params = {}
        for k, v in params.iteritems():

            if input2cfg.get(k) is not None:
                new_params[input2cfg[k]] = v

        new_params.update(SimParams.CFG2INPUT_DEFAULT)

        for k in sorted(new_params.iterkeys()):
            v = new_params[k]
            print '{k}: {v}'.format(k=k, v=v)

        config = ConfigParser.SafeConfigParser()
        # this will make options case sensitive
        config.optionxform = str

        sections = set()
        for k, value in new_params.iteritems():
            section, option = k
            if not section in sections:
                config.add_section(section)
                sections.add(section)

            config.set(section, option, str(value))

        with open(params_cfg, 'wb') as configfile:
            config.write(configfile)

    PARAMS_CFG = [
        # (section, param, default, type)
        ('domain', 'r_p', None, float), #
        ('domain', 'r_d', None, float), #
        ('domain', 'geom', None, int), #
        ('domain', 'phi_p', None, float), #
        ('domain', 'phi_d', None, float), #
        ('domain', 'surface_sheath', 1.0, float), #

        ('init', 'profile_type', None, int), #

        ('plasma', 'T_e', None, float), #
        ('plasma', 'T_i', None, float), #
        ('plasma', 'n_0', None, float), #

        ('gas', 'pressure', None, float), #
        ('gas', 'T_g', None, float), #

        ('simulation', 'dt', None, float), #
        ('simulation', 'dr', None, float), #
        ('simulation', 'NSP', None, int), #
        ('simulation', 'Ntimes', None, int),
        ('simulation', 'out_every', None, int),
        ('simulation', 'every_ions', None, int),

        ('drift', 'I_e', None, float),
        ('drift', 'I_i', None, float),

        ('stats', 'global', None, int),
        ('stats', 'local', None, int),

        ('sweep', 'sweep', None, int),
        ('sweep', 'sweep_period', None, float),
        ('sweep', 'sweep_start', None, float),
        ('sweep', 'sweep_stop', None, float),

        ('boundary', 'reflecting_probe', None, int),
        ('boundary', 'boundary_condition_type', None, int),

        ('hist', 'HIST_NEW_PARTICLES', None, int),
        ('hist', 'HIST_PROBE_PARTICLES', None, int),
        ('hist', 'HIST_SHEATH_PARTICLES', None, int),
    ]

    H5_DATATYPE_CONVERSION = {
        '<type \'int\'>': 'H5T_NATIVE_INT',
        '<type \'float\'>': 'H5T_NATIVE_DOUBLE',
    }

    LOG_PARAMS_WIDTHS = (12, 25, 10, 15, 50)
    LOG_CFG_WIDTHS = (30, 25)

    @staticmethod
    def current2drift_speed(I, n, S):
        return I / (consts.e * n * S)

    def __init__(self, file_with_params, old_type=True, debye_fraction_user=None):

        self.debye_fraction_user = debye_fraction_user

        if isinstance(file_with_params, basestring):
            params_filename = os.path.split(file_with_params)[1]
            # assert params_filename in ['input.params', 'params.cfg']

            params_filename_split = params_filename.split('.')
            if params_filename_split[-1].strip() == 'params':
                print 'SimParams - reading from input.params'
                self.is_old_input_type = True
                self.params = self.read_params_from_inputparams(file_with_params, debye_fraction_user=self.debye_fraction_user)
            else:
                self.is_old_input_type = False
                print 'SimParams - reading from params.cfg'
                self.params = self.get_params(file_with_params)

            self.geom = SimParams.GEOM_TYPES[int(self.params['geom'])]

        elif isinstance(file_with_params, file):
            if old_type:
                self.is_old_input_type = True
                self.params = self.read_params_from_inputparams(file_with_params, debye_fraction_user=self.debye_fraction_user)
            else:
                self.is_old_input_type = False
                self.params = self.get_params(file_with_params)

            self.geom = SimParams.GEOM_TYPES[int(self.params['geom'])]

        elif isinstance(file_with_params, dict):
            self.params = file_with_params

            if self.params['geom'] == 's':
                self.geom = 'spherical'
            elif self.params['geom'] == 'c':
                self.geom = 'cylindrical'
            elif self.params['geom'] == 'p':
                self.geom = 'planar'
            else:
                raise Exception('only s,c,p')

            self.is_old_input_type = True
            self.params['T_g'] = self.params['T_gas']
        else:
            raise Exception('file_with_params can be only of type string or file')

        self.cparams = self.compute_cparams(self.params)
        self.sparams = self.compute_sparams(self.params, self.cparams, debye_fraction_user=self.debye_fraction_user)

    @staticmethod
    def input2cfg():
        return {
            v: k for k, v in SimParams.CFG2INPUT.iteritems()
        }

    def get_params(self, path_to_params_cfg='params.cfg'):

        if isinstance(path_to_params_cfg, basestring):
            config = ConfigParser.SafeConfigParser()
            config.read(path_to_params_cfg)
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tempfile_:
                tempfile_.writelines(path_to_params_cfg.readlines())
                tempfilename = tempfile_.name

            config = ConfigParser.SafeConfigParser()
            config.read(tempfilename)

        cfg = dict()
        for section, var, default, var_type in SimParams.PARAMS_CFG:
            print section, var, default, var_type
            w = SimParams.LOG_PARAMS_WIDTHS
            param = config.get(section, var, default)
            if param is None:
                raise ValueError('var {var} in section {section} not found in file'.format(var=var, section=section))

            cfg[var] = var_type(float(param))

            logger.debug('{section} {var} {default} {var_type} :  {param}'.
                         format(section=str(section).ljust(w[0]),
                                var=str(var).ljust(w[1]),
                                default=str(default).ljust(w[2]),
                                var_type=str(var_type).ljust(w[3]),
                                param=str(param).ljust(w[4])))

        self.geom = SimParams.GEOM_TYPES[int(cfg['geom'])]
        # tohle je tak nejak zafixovane a asi by to chtelo v budoucnu vytahnout ven do params.cfg nebo nekam
        cfg['sigma_cs'] = 6e-20
        cfg['VmaxElectronCollision'] = 2.5e6
        cfg['P_coll'] = 0.02
        cfg['N_grid_user'] = 1000
        cfg['is_old_input_type'] = self.is_old_input_type

        cparams = self.compute_cparams(cfg)
        sparams = self.compute_sparams(cfg, cparams)

        cfg.update(cparams)
        cfg.update(sparams)

        for key in sorted(cfg.iterkeys()):
            w = SimParams.LOG_CFG_WIDTHS
            logger.debug(' cfg[{key}] : {param}'.format(key=str(key).ljust(w[0]),
                                                        param=str(cfg[key])).ljust(w[1]))

        if isinstance(path_to_params_cfg, file):
            os.remove(tempfilename)

        return cfg

    def prepare_sim(self, h5file='sim.h5', groupno=0):
        groupstr = '/common_{:04d}'.format(groupno)

        subprocess.check_call(['h5mkgrp', h5file, groupstr])

        for _, param, default, param_type in self.PARAMS_CFG:

            value = None
            if param_type is int:
                value = '{:d}'.format(self.params[param])
            if param_type is float:
                # value = '{0:f}'.format(self.params[param])
                # value = '{:0.100f}'.format(self.params[param])
                value = '{:e}'.format(self.params[param])

            cmd = ['h5edit', '--atomic', 'no', '--command',
                   'CREATE {path} {{{type} DATASPACE SIMPLE(1) DATA {{{value}}}}};'.
                   format(path=os.path.join(groupstr, param), type=self.H5_DATATYPE_CONVERSION[str(param_type)],
                          value=value), h5file]
            logger.debug('cmd: %s', cmd)
            subprocess.check_call(cmd)

    @staticmethod
    def read_params_from_inputparams(input_params, **kwargs):
        debye_fraction_user = kwargs.get('debye_fraction_user', None)
        params = dict()
        keys = SimParams.INPUT_PARAMS_LINES.keys()

        if isinstance(input_params, basestring):
            with open(input_params) as f:
                lines = f.readlines()

        elif isinstance(input_params, file):
            lines = input_params.readlines()

        else:
            raise TypeError('input_params has to be string or file')

        for iline, line in enumerate(lines):
            if iline in keys:
                new_key = SimParams.INPUT_PARAMS_LINES[iline]
                new_value = float(line.split('!')[0])
                params[new_key] = new_value

        params['sigma_cs'] = 6e-20
        params['VmaxElectronCollision'] = 2.5e6
        params['P_coll'] = 0.02
        params['N_grid_user'] = 1000
        if debye_fraction_user is not None:
            params['debye_fraction_user'] = debye_fraction_user

        return params

    def compute_cparams(self, params):

        cparams = {}

        if self.is_old_input_type:
            cparams['omega_pl'] = sqrt(params['n_e'] * consts.elementary_charge**2/(consts.epsilon_0*consts.m_e))
            cparams['debye'] = sqrt(consts.epsilon_0 * consts.k*params['T_e'] / (params['n_e'] * consts.e**2))
        else:
            cparams['omega_pl'] = sqrt(params['n_0'] * consts.elementary_charge**2/(consts.epsilon_0*consts.m_e))
            cparams['debye'] = sqrt(consts.epsilon_0 * consts.k*params['T_e'] / (params['n_0'] * consts.e**2))

        cparams['n_g'] = params['pressure'] / (consts.k * params['T_g'])
        cparams['ve_thermal'] = sqrt(consts.k * params['T_e'] / consts.m_e)
        cparams['vari_thermal'] = sqrt(consts.k * params['T_i'] / (39.948 * consts.atomic_mass))
        if self.geom == 'spherical':
            try:
                if self.is_old_input_type:
                    cparams['v_drift'] = params['I'] / (consts.e * 4.0 *
                                                        consts.pi * params['r_d']**2 *
                                                        params['n_e'])
                else:
                    cparams['ve_drift'] = params['I_e'] / (consts.e * 4.0 *
                                                            consts.pi * params['r_d']**2 *
                                                            params['n_0'])
                    cparams['vi_drift'] = params['I_i'] / (consts.e * 4.0 *
                                                             consts.pi * params['r_d']**2 *
                                                             params['n_0'])
            except:
                pass

        return cparams

    def compute_sparams(self, params, cparams, debye_fraction_user=None):
        sparams = {}

        try:
            #cell size assuming dr is one tenth of debye length
            sparams['dr_debye'] = cparams['debye'] / 10.0
            #number of grid points
            sparams['number_of_grid_points_debye'] = (params['r_d'] - params['r_p']) / sparams['dr_debye']

            #timestep estimated from plasma frequency:
            sparams['dt_omega_pl'] = 0.1 / cparams['omega_pl']
            #timestep estimated from probability of collision in one timestep:
            sparams['dt_coll'] = -1 / (params['sigma_cs'] * params['VmaxElectronCollision'] * cparams['n_g']) * log(1 - params['P_coll'])
            #grid_size as specified by user
            sparams['dr_user'] = (params['r_d'] - params['r_p']) / (params['N_grid_user'] - 1)

            if debye_fraction_user is not None:
                #debye user fraction
                sparams['dr_debye_user'] = cparams['debye'] / self.debye_fraction_user
                #number of grid points
                sparams['number_of_grid_points_debye_user'] = (params['r_d'] - params['r_p']) / sparams['dr_debye_user']
                #time for electron to travel half of dr_debye_user:
                if self.is_old_input_type:
                    sparams['dt_thermal_debye_user'] = sparams['dr_debye_user'] / (2 * cparams['ve_thermal'])
                    #time for electron to travel half of dr_user:
                    sparams['dt_thermal_user'] = sparams['dr_user'] / (2 * cparams['ve_thermal'])
                    #time for electron to travel half of dr_debye:
                    sparams['dt_thermal_debye'] = sparams['dr_debye'] / (2 * cparams['ve_thermal'])
                else:
                    sparams['dt_thermal_debye_user'] = sparams['dr_debye_user'] / (2 * cparams['ve_thermal'])
                    #time for electron to travel half of dr_user:
                    sparams['dt_thermal_user'] = sparams['dr_user'] / (2 * cparams['ve_thermal'])
                    #time for electron to travel half of dr_debye:
                    sparams['dt_thermal_debye'] = sparams['dr_debye'] / (2 * cparams['ve_thermal'])

            #volume of computational domain:
            if self.geom == 'spherical':
                sparams['volume_domain'] = 4.0/3.0 * pi * (params['r_d']**3 - params['r_p']**3)
            else:
                sparams['volume_domain'] = pi * (params['r_d']**2 - params['r_p']**2)
            #approximate weight of particle:
            if self.is_old_input_type:
                sparams['weight_global'] = sparams['volume_domain'] * params['n_e'] / params['NSP']
            else:
                sparams['weight_global'] = sparams['volume_domain'] * params['n_0'] / params['NSP']

            return sparams
        except:
            pass

        return None

    def print_params(self, name):
        self.print_dict(self.params, name)

    def print_cparams(self, name):
        self.print_dict(self.cparams, name)

    def print_sparams(self, name):
        self.print_dict(self.sparams, name)

    @staticmethod
    def print_dict(dictionary, name):
        print '{}:'.format(name)
        for key in sorted(dictionary.keys()):
            print '{} = {:g}'.format(key, dictionary[key])
        print

    #pylint: disable=R0914
    def OML_exact(self, r_sheath, n_sheath, particle):
        params, cparams, sparams = self.params, self.cparams, self.sparams
        assert cparams, sparams

        if particle == 'electron':
            T = params['T_e']
            m = consts.m_e
            ## watch out!!! this needs to be a charge of given particle (positive or negative)
            charge = -consts.e
        elif particle == 'argon_ion':
            T = params['T_i']
            m = 39.948 * consts.atomic_mass
            charge = consts.e
        else:
            raise NotImplementedError('only electron and argon_ion are implemented')

        if self.geom == 'spherical':

            mean = sqrt(8 * consts.k * T / (pi * m))
            Ss = 4 * pi * r_sheath ** 2

            return n_sheath / 4 * charge * mean * Ss * (1-(1-(params['r_p'] / r_sheath)**2) * \
                   exp((charge * params['phi_p']) / (consts.k * T * ((r_sheath / params['r_p'])**2-1))))

        elif self.geom == 'cylindrical':
            # this formula is taken from Chen, chapter Electrin probes, page 130:
            # there is uncertainty in which order to apply functions (erf and sqrt),
            # this approach was verified by Granowski
            s = r_sheath
            a = self.params['r_p']
            eta = - charge * self.params['phi_p'] / (consts.k * T)
            Phi = a**2 / (s**2 - a**2) * eta
            F = s/a * erf(sqrt(Phi)) + exp(eta) * (1 - erf(sqrt(eta + Phi)))
            # surface of probe (taking probe 1 m long)
            A_a = 2 * pi * a
            mean = sqrt(8 * consts.k * T / (pi * m))
            j_r = 1.0 / 4.0 * n_sheath * mean
            current = charge * A_a * j_r * F

            return current
        else:
            raise NotImplementedError('only spherical and cylindrical geomteries are implemented')

    def OML_simplified(self, particle):
        params, cparams, sparams = self.params, self.cparams, self.sparams
        assert cparams, sparams

        if particle == 'electron':
            T = params['T_e']
            m = consts.m_e
            ## watch out!!! this needs to be a charge of given particle (positive or negative)
            charge = -consts.e

        elif particle == 'argon_ion':
            T = params['T_i']
            m = 39.948 * consts.atomic_mass
            charge = consts.e
        else:
            raise NotImplementedError('only electron and argon_ion are implemented')

        if self.geom == 'spherical':
            mean = sqrt(8 * consts.k * T / (pi * m))
            Sp = 4 * pi * params['r_p']**2
            current = params['n_e'] / 4 * charge * mean * Sp * (1 - (charge * params['phi_p']) / (consts.k * T))

            return current
        elif self.geom == 'cylindrical':
            # again from Chen, page 131
            # surface of probe (taking probe 1 m long)
            A_a = 2 * pi * self.params['r_p']
            mean = sqrt(8 * consts.k * T / (pi * m))
            j_r = 1.0 / 4.0 * self.params['n_e'] * mean
            eta = - charge * self.params['phi_p'] / (consts.k * T)
            F = 2.0 / sqrt(pi) * sqrt(eta + 1)
            current = charge * A_a * j_r * F

            return current

        else:
            raise NotImplementedError('only spherical and cylindrical geomteries are implemented')
