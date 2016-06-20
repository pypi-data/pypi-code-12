#!/usr/bin/env python
import os
import logging
from .exceptions import FaffException


class Core(object):
    '''
    Package core class.
    '''
    def __init__(self, name='faff', stdout=None, stderr=None):
        '''
        Initial default configuration.
        '''
        # Package name, version and description.
        self._name = name
        self._version = (0, 1, 0)
        self._description = ''

        # Standard output/error streams.
        self._stdout = stdout
        self._stderr = stderr

        # Default logging level, file.
        self._log_level = 'ERROR'
        self._log_file = None

        # Default logger object.
        self.log = self.get_logger()

    def __call__(self, *args, **kwargs):
        '''
        Reinitialise on call.
        '''
        self.__init__(*args, **kwargs)

    def get_name(self):
        '''
        Get package name.
        '''
        return self._name

    def get_version(self):
        '''
        Get package version.
        '''
        return '.'.join([str(x) for x in self._version])

    def get_description(self):
        '''
        Get package description.
        '''
        return self._description

    def get_default_input_file(self):
        '''
        Get default input file path.
        '''
        return os.path.join(os.getcwd(), 'faffin.py')

    def write_stdout(self, x, raw=False):
        '''
        Write to internally configured stdout.
        '''
        if self._stdout is not None:
            if raw:
                x = '{0}\n'.format(x)
            else:
                x = '{0}: {1}\n'.format(self._name, x)

            self._stdout.write(x)

    def write_stderr(self, x, raw=False):
        '''
        Write to internally configured stderr.
        '''
        if self._stderr is not None:
            if raw:
                x = '{0}\n'.format(x)
            else:
                x = '{0}: {1}\n'.format(self._name, x)

            self._stderr.write(x)

    def raise_exception(self, x, cls=FaffException):
        '''
        Raise exception with message.
        '''
        raise cls('{0}\n'.format(x))

    def configure_args(self, args):
        '''
        Command line arguments configuration.
        '''
        # Logging configuration.
        self.configure_logging(args.log_level, args.log_file)

        # Report configuration via logger.
        self.log = self.get_logger()
        self.log.debug('{0}: configured'.format(self.get_name()))

    def configure_logging(self, log_level, log_file):
        '''
        Logging configuration.
        '''
        self._log_level = log_level.upper()
        self._log_file = log_file

    def get_logger(self):
        '''
        Get configured logger object.
        '''
        kwargs = {'level': self._log_level}
        if self._log_file is not None:
            kwargs['filename'] = self._log_file

        # Root logger object.
        logging.basicConfig(**kwargs)
        return logging.getLogger()


# Internal core instance.
core = Core()
