# -*- coding: utf-8 -*-
import sys


class ArgumentParser(object):

    OPTION_SINGLE = 1
    OPTION_PARAMETERIZED = 2

    PARAM_SHORT = 1
    PARAM_LONG = 2

    @classmethod
    def from_argv(cls):
        """
            Creates an ArgumentParser engine with args from
            sys.argv[].
        """
        return cls(sys.argv)

    def __init__(self, args, mapping={}):
        """ Initializes an ArgumentParser instance.  Parses out
            things that we already know, like args[0] (should be the
            executable script).
        """

        try:
            self.exec_file = args[0]
        except:
            self.exec_file = ''

        self.__args = args

        self._default_types = {
            ArgumentParser.PARAM_SHORT: ArgumentParser.OPTION_SINGLE,
            ArgumentParser.PARAM_LONG: ArgumentParser.OPTION_SINGLE
        }
        self._opt_types = {}
        self._mapping = mapping
        self._descriptions = {}
        self.options = {}
        self.parameters = []

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, traceback):

        return None

    def param_defined(self, param):
        """ Checks all of the various ways a parameter can be a defined to see
            if the given parameter actually is defined.

            :param str param: Parameter to check for
            :return: parameter is defined
            :rtype: bool
        """

        if param.startswith('-'):
            param = param.lstrip('-')

        is_typed = param in self._opt_types
        is_mapped = param in self._mapping
        is_described = False

        for _p in self.get_option_descriptions().keys():
            if param in _p:
                is_described = True
            continue

        return is_typed or is_mapped or is_described

    def set_default_param_type(self, param_type, opt=OPTION_SINGLE):
        """ Sets the default type map that a parameter will be treated as.
            Can help force more uniform arguments without having to pre-define
            options.

            :param int param_type: Parameter type (PARAM_LONG, PARAM_SHORT)
            :param int opt: Option type (OPTION_PARAMETERIZED, OPTION_SINGLE)
            :return: none
            :rtype: None
        """

        self._default_types[param_type] = opt

    def add_option_type(self, option, opt=OPTION_SINGLE):
        """ Adds a type mapping to a specific option. Allowed types are
            OPTION_SINGLE and OPTION_PARAMETERIZED.

            :param str option: Option to set type for
            :param int opt: Option type (OPTION_PARAMETERIZED, OPTION_SINGLE)
            :return: none
            :rtype: None
        """

        self._opt_types[option] = opt

    def add_option_mapping(self, option, map_name):
        """ Maps a option value (-a, -g, --thing, etc.) to a full word or
            phrase that will be stored in the options dictionary after parsing
            is finished.  Makes option usage easier.

            :param str option: Option to map from
            :param str map_name: Option name to map to
            :return: none
            :rtype: None
        """

        self._mapping[option] = map_name

    def add_option_description(self, option, description):
        """ Adds a helpful description for an argument. Is returned when
            get_option_descriptions is called.

            :param str option: Option to describe
            :param str description: Description of option
            :return: none
            :rtype: None
        """

        self._descriptions[option] = description

    def get_option_descriptions(self):
        """ Returns a map of options to their respective descriptions.  Good
            for printing out a series of help messages describing usage.

            :return: Dictionary of option => description pairs
            :rtype: dict
        """

        processed_descriptions = {}
        for option, description in self._descriptions.items():
            if len(option) == 1:  # This is a flag. Prepend a dash.
                option = '-' + option
                processed_descriptions.update({option: description})
            elif len(option) > 1 and option.startswith('--'):
                # Option. Append blindly.
                processed_descriptions.update({option: description})
            elif len(option) > 1 and not option.startswith('--'):
                # Option. Append double-dash.
                option = '--' + option
                processed_descriptions.update({option: description})
            else:
                # What is this? Blindly append.
                processed_descriptions.update({option: description})

        return processed_descriptions

    def parse(self):
        """ Parses out the args into the mappings provided in self.mapping,
            stores the result in self.options.

            :return: none
            :rtype: None
        """

        waiting_argument = None

        for param in self.__args:
            if param[0] in ['"', "'"]:
                param = param.lstrip(param[0])

            if param[-1] in ['"', "'"]:
                param = param.rstrip(param[-1])

            if param.startswith('--'):
                # Long option mapping.
                paraml = param[2:]
                if '=' in paraml:
                    param, value = paraml.split('=')
                    # Store a PARAMETERIZED option type, if none exists.
                    if param not in self._opt_types:
                        self.add_option_type(
                            param,
                            ArgumentParser.OPTION_PARAMETERIZED)
                else:
                    param = paraml
                    if param not in self._opt_types:
                        self.add_option_type(
                            param,
                            self._default_types[ArgumentParser.PARAM_LONG])
                store_as = param
                if param in self._mapping:
                    self.options.update({self._mapping[param]: True})
                    store_as = self._mapping[param]
                else:
                    self.options.update({param: True})
                if param in self._opt_types:
                    ptype = self._opt_types[param]
                    if ptype == ArgumentParser.OPTION_PARAMETERIZED:
                        if '=' in paraml:
                            # Option is long and contains the value.
                            self.options.update({store_as: value})
                            waiting_argument = None
                        else:
                            waiting_argument = store_as
            elif param.startswith('-') and not self.param_defined(param):
                # Starts with a -, but is not a defined parameter.
                if waiting_argument is not None:
                    self.options.update({waiting_argument: param})
                    waiting_argument = None
                else:
                    self.parameters.append(param)

                continue
            elif param.startswith('-'):
                # Short option mapping.
                param = param[1:]
                for opt in param:
                    store_as = opt
                    if opt in self._mapping:
                        self.options.update({self._mapping[opt]: True})
                        store_as = self._mapping[opt]
                    else:
                        self.options.update({opt: True})
                    if opt in self._opt_types:
                        ptype = self._opt_types[opt]
                        if ptype == ArgumentParser.OPTION_PARAMETERIZED:
                            waiting_argument = store_as
            else:
                # Option parameter or command parameter.
                if waiting_argument is not None:
                    self.options.update({waiting_argument: param})
                    waiting_argument = None
                else:
                    self.parameters.append(param)
