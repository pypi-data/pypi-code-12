
import os, re, sys, time
from configparser import ConfigParser, BasicInterpolation, ExtendedInterpolation
from bl.dict import Dict         # needed for dot-attribute notation

LIST_PATTERN = "^\[\s*([^,]*)\s*(,\s*[^,]*)*,?\s*\]$"
DICT_ELEM = """(\s*['"].+['"]\s*:\s*[^,]+)"""
DICT_PATTERN = """^\{\s*(%s,\s*%s*)?,?\s*\}$""" % (DICT_ELEM, DICT_ELEM)

class Config(Dict):
    """class for holding application configuration in an Ini file. Sample Usage:
    >>> cf_filename = os.path.join(os.path.dirname(__file__), "config_test.ini")
    >>> cf = Config(cf_filename)
    >>> cf.filename
    >>> cf.__dict__['__filename__'] == os.path.join(os.path.dirname(__file__), "config_test.ini")
    True
    >>> cf.Archive.path             # basic string conversion
    '/data/files'
    >>> cf.Test.debug               # boolean 
    True
    >>> cf.Test.list                # list with several types
    [1, 2, 'three', True, 4.0]
    >>> cf.Test.dict                # dict => Dict
    {'a': 1, 'b': 'two', 'c': False}
    >>> cf.Test.dict.a              # Dict uses dot-notation
    1
    """

    Interpolation = ExtendedInterpolation()

    def __init__(self, fn=None, interpolation=None, 
                split_list=None, join_list=None, **params):
        config = ConfigParser(interpolation=interpolation or self.Interpolation)
        self.__dict__['__filename__'] = fn
        self.__dict__['__join_list__'] = join_list
        if fn is not None:
            if config.read(fn):
                self.parse_config(config, split_list=split_list)
            else:
                raise KeyError("Config file not found at %s" % fn)
        self.update(**params)

    def __repr__(self):
        return "Config('%s')" % self.__filename__

    def parse_config(self, config, split_list=None):
        for s in config.sections():
            self[s] = Dict()
            for k, v in config.items(s):
                # resolve common data types
                if v.lower() in ['true', 'false', 'yes', 'no']:     # boolean
                    self[s][k] = config.getboolean(s, k)
                elif re.match("^\-?\d+$", v):                       # integer
                    self[s][k] = int(v)
                elif re.match("^\-?\d+\.\d*$", v):                  # float
                    self[s][k] = float(v)
                elif re.match(LIST_PATTERN, v):                     # list
                    self[s][k] = eval(v)
                elif re.match(DICT_PATTERN, v):                     # dict
                    self[s][k] = Dict(**eval(v))
                elif split_list is not None \
                and re.search(split_list, v) is not None:
                    self[s][k] = re.split(split_list, v)
                else:                                               # default: string
                    self[s][k] = v.strip()

    def write(self, fn=None, sorted=False, wait=0):
        """write the contents of this config to fn or its __filename__.
        NOTE: All interpolations will be expanded in the written file.
        """
        config = ConfigParser(interpolation=None)
        keys = self.keys()
        if sorted==True: keys.sort()
        for key in keys:
            config[key] = {}
            ks = self[key].keys()
            if sorted==True: ks.sort()
            for k in ks:
                if type(self[key][k])==list and self.__join_list__ is not None:
                    config[key][k] = self.__join_list__.join([v for v in self[key][k] if v!=''])
                else:
                    config[key][k] = str(self[key][k])
        fn = fn or self.__dict__.get('__filename__')
        # use advisory locking on this file
        i = 0
        while os.path.exists(fn+'.LOCK') and i < wait:
            i += 1
            time.sleep(1)
        if os.path.exists(fn+'.LOCK'):
            raise FileExistsError(fn + ' is locked for writing')
        else:
            with open(fn+'.LOCK', 'w') as lf:
                lf.write(time.strftime("%Y-%m-%d %H:%M:%S %Z"))
            with open(fn, 'w') as f:
                config.write(f)
            os.remove(fn+'.LOCK')

class ConfigTemplate(Config):
    """load the config with interpolation=None, so as to provide a template"""
    Interpolation = None

    def expects(self):
        """returns a Dict of params that this ConfigTemplate expects to receive"""
        params = Dict()
        regex = re.compile("(?<![\{\$])\{([^\{\}]+)\}")
        for block in self.keys():
            for key in self[block].keys():
                for param in re.findall(regex, str(self[block][key])):
                    b, k = param.split('.')
                    if b not in params: params[b] = Dict()
                    params[b][k] = None
        return params

    def render(self, fn=None, prompt=False, **params):
        """return a Config with the given params formatted via str.format(**params).
        fn=None         : If given, will assign this filename to the rendered Config.
        prompt=False    : If True, will prompt for any param that is None.
        """
        from getpass import getpass
        expected_params = self.expects()
        params = Dict(**params)
        if prompt==True:
            for block in expected_params.keys():
                if block not in params.keys():
                    params[block] = Dict()
                for key in expected_params[block].keys():
                    if params[block].get(key) is None:
                        if key=='password':
                            params[block][key] = getpass("%s.%s: " % (block, key))
                        else:
                            params[block][key] = input("%s.%s: " % (block, key)).replace(r'\ ', ' ')
        config = Config(**self)
        if fn is None and self.__dict__.get('__filename__') is not None: 
            fn = os.path.splitext(self.__dict__.get('__filename__'))[0]
        config.__dict__['__filename__'] = fn
        for block in config.keys():
            for key in config[block].keys():
                if type(config[block][key])==str:
                    config[block][key] = config[block][key].format(**params)
        return config

def configure_package(path, packages=[], template_name='config.ini.TEMPLATE', 
        config_name='config.ini', **config_params):
    """configure the package at the given path with a config template and file.
    packages        = a list of packages to search for config templates
    config_params   = a dict containing config param blocks.
    """
    import importlib

    # create a ConfigTemplate from the config.ini.TEMPLATE in each dependency module.
    # "first precedence": The first package in the packages list to include a particular config block
    # is the one that defines that block.
    config_template = ConfigTemplate()
    for package in packages:
        module = importlib.import_module(package)
        ct_fn = os.path.join(os.path.dirname(module.__file__), template_name)
        if os.path.exists(ct_fn):
            ct = ConfigTemplate(fn=ct_fn)
            for key in ct.keys():
                if key not in config_template.keys():
                    config_template[key] = ct[key]

    # render the config
    config = config_template.render(prompt=True, **config_params)
    config.write(fn=os.path.join(path, config_name))
    return Config(os.path.join(path, config_name))

if __name__ == "__main__":
    if len(sys.argv) == 0 or sys.argv[0]=='test':
        import doctest
        doctest.testmod()
