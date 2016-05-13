import os
import re
import types
from subprocess import call


class commandRunner():

    def __init__(self, **kwargs):
        '''
            Constructs a local job
            takes
            tmp_id = string
            tmp_path="/tmp/"
            command="ls /tmp > $OUTPUT"

            out_globs=['file',]
            input_data={filename:data_string}
            input_string="test.file"
            output_string="out.file"
            options = {flag:entry}
            flags = [strings,]
            identifier = "string"
            std_out_string="str.stdout"
            env_vars = {name:value}
        '''
        self.tmp_id = None
        self.tmp_path = None
        self.out_globs = None
        self.command = None
        self.input_data = None
        self.command = None
        self.params = []
        self.ge_params = []
        self.identifier = None

        self.input_string = None
        self.output_string = None
        self.options = None
        self.flags = None
        self.output_data = None
        self.path = None
        self.std_out_str = None
        self.env_vars = None

        self.__check_arguments(kwargs)

        self.tmp_path = re.sub("/$", '', self.tmp_path)
        self.path = self.tmp_path+"/"+self.tmp_id+"/"
#       self.command = self.__translate_command(kwargs.pop('command', ''))
        self.command = self._translate_command(self.command)

    def __check_arguments(self, kwargs):
        # flags = (strings,)
        if os.path.isdir(kwargs['tmp_path']):
            self.tmp_path = kwargs.pop('tmp_path', '')
        else:
            raise OSError('tmp_path provided does not exist')

        if isinstance(kwargs['tmp_id'], str):
            self.tmp_id = kwargs.pop('tmp_id', '')
        else:
            raise TypeError('tmp_id must be a string')

        if isinstance(kwargs['command'], str):
            self.command = kwargs.pop('command', '')
        else:
            raise TypeError('command must be a string')

        if 'identifier' in kwargs:
            if isinstance(kwargs['identifier'], str):
                self.identifier = kwargs.pop('identifier', '')
            else:
                raise TypeError('identifier must be a str')

        if 'std_out_str' in kwargs:
            if isinstance(kwargs['std_out_str'], str):
                self.std_out_str = kwargs.pop('std_out_str', '')
            else:
                raise TypeError('std_out_str must be a str')

        if 'input_data' in kwargs:
            if isinstance(kwargs['input_data'], dict):
                self.input_data = kwargs.pop('input_data', '')
            else:
                raise TypeError('input_data must be a dict')

        if 'out_globs' in kwargs:
            if isinstance(kwargs['out_globs'], list):
                self.out_globs = kwargs.pop('out_globs', '')
            else:
                raise TypeError('out_globs must be array')

        if 'input_string' in kwargs:
            if isinstance(kwargs['input_string'], str):
                self.input_string = kwargs.pop('input_string', '')
            else:
                raise TypeError('input_string must be str')
        if 'output_string' in kwargs:
            if isinstance(kwargs['output_string'], str):
                self.output_string = kwargs.pop('output_string', '')
            else:
                raise TypeError('output_string must be str')

        if 'options' in kwargs:
            if isinstance(kwargs['options'], dict):
                self.options = kwargs.pop('options', '')
            else:
                raise TypeError('options must be dict')

        if 'env_vars' in kwargs:
            if isinstance(kwargs['env_vars'], dict):
                self.env_vars = kwargs.pop('env_vars', '')
            else:
                raise TypeError('env_vars must be dict')
            if not all(isinstance(x, str) for x in self.env_vars.keys()):
                raise TypeError('env_vars keys must be strings')
            if not all(isinstance(x, str) for x in self.env_vars.values()):
                raise TypeError('env_vars values must be strings')


        if 'flags' in kwargs:
            if isinstance(kwargs['flags'], list):
                self.flags = kwargs.pop('flags', '')
            else:
                raise TypeError('flags must be list')

        if ">" in self.command:
            raise ValueError("Command string provides stdout redirection"
                             ", please provide std_out_str instead")
        if "$INPUT" in self.command and self.input_string is None:
            raise ValueError("Command string references $INPUT but no "
                             "input_string provided")
        if "$OUTPUT" in self.command and self.output_string is None:
            raise ValueError("Command string references $OUTPUT but no "
                             "output_string provided")
        if "$ID" in self.command and self.identifier is None:
            raise ValueError("Command string references $ID but no "
                             "identifier provided")


    def _translate_command(self, command):
        '''
            takes the command string and substitutes the relevant files names
        '''
        self.params = command.split()
        self.command_token = self.params[0]
        command = [self.params[0], ]
        self.params = self.params[1:]
        # interpolate the file names if needed

        flags_str = ""
        if self.flags is not None:
            command.extend(self.flags)

        options_str = ""
        if self.options is not None:
            for key, value in sorted(self.options.items()):
                command.extend([key+" "+value])

        command.extend(self.params)
        self.ge_params = command[1:]
        if self.input_string is not None:
            command = [a.replace('$INPUT',  self.input_string) for a in command]
        if self.output_string is not None:
            command = [a.replace('$OUTPUT', self.output_string) for a in command]
        if self.identifier is not None:
            command = [a.replace('$ID', self.identifier) for a in command]

        self.ge_params = command[1:]
        if self.std_out_str is not None:
            command.extend([">", self.std_out_str])

        command_string = ' '.join(command)
        return(command_string)

    def prepare(self):
        '''
            Makes a directory and then moves the input data file there
        '''
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if self.input_data is not None:
            for key in self.input_data.keys():
                file_path = self.path+key
                fh = open(file_path, 'w')
                fh.write(self.input_data[key])
                fh.close()

    def run_cmd(self):
        '''
            run the command we constructed when the object was initialised.
            If exit is 0 then pass back if not decide what to do next. (try
            again?)
        '''
        raise NotImplementedError

    def tidy(self):
        '''
            Delete everything in the tmp dir and then remove the temp dir
        '''
        for this_file in os.listdir(self.path):
            file_path = os.path.join(self.path, this_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        if os.path.exists(self.path):
            os.rmdir(self.path)
