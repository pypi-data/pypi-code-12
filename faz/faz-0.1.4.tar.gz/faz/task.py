# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import glob
import logging
import re
import subprocess
import tempfile
from datetime import datetime as dt
from string import Template


class TaskFailedException(Exception):
    pass


class TempDirIsFileException(Exception):
    pass


class Task(object):

    __dirname = ".faz"
    __variable_pattern = re.compile(r"\$\[([a-zA-Z0-9_]+)\]")

    def __init__(self, inputs, outputs, code, options, environment):
        self.inputs = inputs
        self.outputs = outputs
        self.original_outputs = outputs
        self.code = code
        self.options = options
        self.environment = environment
        self.order = 0
        self.force = False
        self.interpreter = None
        self.f = None
        self.check_options()

    def check_options(self):
        interpreter = "bash"
        for option in self.options:
            if "python" in option.lower():
                interpreter = "python"
            elif "ruby" in option.lower():
                interpreter = "ruby"
            elif "force" in option.lower():
                self.force = True
        self.interpreter = interpreter

    def check_inputs(self):
        """ Check for the existence of input files """
        self.inputs = self.expand_filenames(self.inputs)
        result = False
        if len(self.inputs) == 0 or self.files_exist(self.inputs):
            result = True
        else:
            print("Not executing task. Input file(s) do not exist.")
        return result

    def check_outputs(self):
        """ Check for the existence of output files """
        self.outputs = self.expand_filenames(self.outputs)
        result = False
        if self.files_exist(self.outputs):
            if self.dependencies_are_newer(self.outputs, self.inputs):
                result = True
                print("Dependencies are newer than outputs.")
                print("Running task.")
            elif self.force:
                print("Dependencies are older than inputs, but 'force' option present.")
                print("Running task.")
                result = True
            else:
                print("Dependencies are older than inputs.")
        else:
            print("No ouput file(s).")
            print("Running task.")
            result = True
        return result

    def expand_variables(self):
        """
        Expand variables in the task code.
        Only variables who use the $[<variable name>] format are expanded.
        Variables using the $<variable name> and ${<variable name>} formats
        are expanded by the shell (in the cases where bash is the interpreter.
        """
        for n, input_file in enumerate(self.inputs):
            self.environment["INPUT{}".format(n +1)] = input_file
        for n, output_file in enumerate(self.outputs):
            self.environment["OUTPUT{}".format(n +1)] = output_file
        for n, line in enumerate(self.code):
            match = self.__variable_pattern.findall(line)
            if len(match) > 0:
                for item in match:
                    value = self.environment.get(item)
                    if value is not None:
                        self.code[n] = line.replace("$[" + item + "]", value)

    def expand_filenames(self, filenames):
        """
        Expand a list of filenames using environment variables,
        followed by expansion of shell-style wildcards.
        """
        results = []
        for filename in filenames:
            result = filename
            if "$" in filename:
                template = Template(filename)
                result = template.substitute(**self.environment)
                logging.debug(
                    "Expanding {} to {}.".format(filename, result))
            if any([pattern in result for pattern in "*[]?"]):
                expanded = glob.glob(result)
                if len(expanded) > 0:
                    result = expanded
                else:
                    result = "NONEXISTENT"
            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)
        return sorted(list(set(results)))

    def files_exist(self, filenames):
        """ Check if all files in a given list exist. """
        return all([os.path.exists(filename) and os.path.isfile(filename)
                    for filename in filenames])

    def dependencies_are_newer(self, files, dependencies):
        """
        For two lists of files, check if any file in the
        second list is newer than any file of the first.
        """
        dependency_mtimes = [
            os.path.getmtime(filename) for filename in dependencies]
        file_mtimes = [os.path.getmtime(filename) for filename in files]
        result = False
        for file_mtime in file_mtimes:
            for dependency_mtime in dependency_mtimes:
                if dependency_mtime > file_mtime:
                    result = True
        return result

    def __call__(self):
        """ Invoque an interpreter to execute the task's code. """
        print("\n ********** Task {0}: {1}\n".format(self.order, self))
        if self.check_inputs() and self.check_outputs():
            self.expand_variables()
            self.mktemp_file()
            #os.write(self.f, "\n".join(self.code) + "\n")
            self.f.write("\n".join(self.code) + "\n")
            self.f.close()
            logging.debug("Environment before task:\n{}".format(self.environment))
            print("Task inputs: {}".format(self.inputs))
            print("Task outputs: {}".format(self.outputs))
            start = dt.now()
            try:
                out = subprocess.check_output([self.interpreter, self.f.name],
                                              stderr=subprocess.STDOUT,
                                              env=self.environment)
            except subprocess.CalledProcessError as e:
                print("Task {} failed with return code {}".format(self, e.returncode))
                print("Output from task:")
                print(e.output)
                raise TaskFailedException("Task {} failed.".format(self))
            end = dt.now()
            logging.debug("Environment after task:\n{}".format(self.environment))
            print("***** execution time {}".format(str(end - start)))
            print("***** Output:\n{}".format(out))
            #os.unlink(self.f.name)
            self.outputs = self.expand_filenames(self.original_outputs)
            if not(self.files_exist(self.outputs)):
                print("Output files:")
                for filename in self.outputs:
                    print("{}: {}".format(filename, os.path.exists(filename)))
                raise TaskFailedException("Output files not created for Task {}\n".format(self))

    def mktemp_file(self):
        """ Create a temporary file in the '.faz' directory for
            the code to feed to the interpreter. """
        if not(os.path.exists(self.__dirname)):
            logging.debug("Creating directory {}".format(self.__dirname))
            os.mkdir(self.__dirname)
        elif not(os.path.isdir(self.__dirname)):
            raise TempDirIsFileException(
                "There is a file called %s in this directory!!!" %
                self.__dirname)
        #self.fdesc, self.fname = tempfile.mkstemp(dir=self.__dirname, text=True)
        self.f = tempfile.NamedTemporaryFile(dir=self.__dirname, delete=False, mode="wt")
        logging.debug("Creating file {}".format(self.f.name))

    def __repr__(self):
        return "%s <- %s :%s" % (
            ", ".join(self.outputs),
            ", ".join(self.inputs),
            ", ".join(self.options))
