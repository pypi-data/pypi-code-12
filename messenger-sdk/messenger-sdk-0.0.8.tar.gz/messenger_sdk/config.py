from configparser import ConfigParser
import os


class Config:
    def __init__(self):
        self._config = ConfigParser()
        config_file = os.path.dirname(os.path.realpath('__main__')) + '/config.ini'
        self.check_config_file_exists(config_file)
        self._config.read(config_file)
        required_options = self.required_options
        self.check_required_config_options(self._config, required_options)

    @staticmethod
    def check_config_file_exists(config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError('File {config_file} does not exist.'.format(config_file=config_file))

    @property
    def required_options(self):
        return {
            'facebook': [
                {'name': 'FB_VERIFICATION_TOKEN', 'type': str},
                {'name': 'FB_TOKEN', 'type': str},
                {'name': 'FB_API', 'type': str},
                {'name': 'FB_GRAPH', 'type': str}
            ],
            'app': [
                {'name': 'PORT', 'type': int},
                {'name': 'LOG_FILE_NAME', 'type': str},
                {'name': 'LOG_TO_TERMINAL', 'type': bool}
            ]
        }

    def check_required_config_options(self, config, required_options):
        if not isinstance(config, ConfigParser):
            raise TypeError(
                'Invalid config type. Expected {expected}, {given} given.'.format(expected=ConfigParser.__name__,
                                                                                  given=type(config)))
        for section in required_options:
            if not config.has_section(section):
                Config.raise_missing_section_error(section)
            for option in required_options.get(section):
                if not config.has_option(section, option.get('name')):
                    Config.raise_missing_option_error(option, section)
                self.check_option(section, option)

    def check_option(self, section, option):
        option_name = option.get('name')
        option_type = option.get('type')
        if not option_name or not option_type:
            raise ValueError(
                'Missing section or option in function: {function}'.format(function=self.check_option.__name__))
        if option_type is str:
            if not self.get_parameter(section, option_name):
                raise self.raise_missing_option_error(option_name, section)
        elif option_type is int:
            try:
                parameter = self.get_int_parameter(section, option_name)
            except ValueError:
                raise ValueError(
                    '[{section}]{option} is not integer.'.format(option=option_name, section=section))
            if not parameter:
                raise self.raise_missing_option_error(option_name, section)
        elif option_type is bool:
            try:
                self.get_bool_parameter(section, option_name)
            except ValueError:
                raise ValueError(
                    '[{section}]{option} is not boolean.'.format(option=option_name, section=section))
        else:
            raise TypeError(
                'Unsupported config value type: [{section}]{option}.'.format(section=section, option=option_name))

    @staticmethod
    def raise_missing_section_error(section):
        raise ValueError('Missing config section:{section}.'.format(section=section))

    @staticmethod
    def raise_missing_option_error(option, section):
        raise ValueError(
            'Missing config option: [{section}]{option}.'.format(option=option, section=section))

    @property
    def config(self):
        return self._config

    def get_parameter(self, section, option):
        parameter = self._config[section][option]
        if not parameter:
            self.raise_missing_option_error(option, section)
        return parameter

    def get_int_parameter(self, section, option):
        parameter = self._config.getint(section, option)
        if not parameter:
            self.raise_missing_option_error(option, section)
        return parameter

    def get_bool_parameter(self, section, option):
        return self._config.getboolean(section, option)
