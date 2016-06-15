#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Administration Scripts
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Administration Scripts.
#
# Hive Administration Scripts is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Administration Scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Administration Scripts. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import sys
import subprocess

import admin_scripts.extra as extra

USAGE_MESSAGE = "cleanup path [extra_argument_1, extra_argument_2, ...]"
""" The usage message to be printed when an error occurs or
when help is requested by the end user """

SCRIPTS_LIST = [
    "stylesheets.py",
    "encoding.py",
    "join.py",
    "pydev.py",
    "pysource.py",
    "jssource.py",
    "trailing_spaces.py"
]
""" The list of scripts to be executed by the complete
cleanup operation, each of the scripts will be executed
as a separate process in a chained process """

SCRIPTS_CONFIGURATION_MAP = {
    "stylesheets.py" : "development/stylesheets.py",
    "encoding.py" : "development/encoding.py",
    "join.py" : "development/join.py",
    "pydev.py" : "development/pydev.py",
    "pysource.py" : "development/pysource.py",
    "jssource.py" : "development/jssource.py",
    "trailing_spaces.py" : "development/trailing_spaces.py"
}
""" The map associating the script name with the name
of the configuration file, so that during execution
the proper values are passed to each script """

CONFIGURATION_RELATIVE_PATH = "../config/"
""" The relative path to the configuration directory """

PYTHON_COMMAND = "python"
""" The python (execution) command """

CONFIGURATION_FLAG = "-c"
""" The flag name for the configuration control """

WINDOWS_PLATFORMS = ("nt", "ce", "dos")
""" The windows platform value, that contains the
series of constant values corresponding to the complete
valid platform values for windows """

def run():
    # retrieves the path to the "current" directory
    directory_path = os.path.dirname(__file__)

    # in case the number of arguments is not sufficient
    # must print an error message about the issue
    if len(sys.argv) < 2:
        # prints a series of message about the correct usage
        # of the command line for this command
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)

        # exits the system in error
        sys.exit(2)

    # retrieves the target path for execution and the
    # extra arguments to be used
    target_path = sys.argv[1]
    extra_arguments = sys.argv[2:]

    # retrieves the current os name and then using it
    # sets the shell value to be used in the process
    shell_value = os.name in WINDOWS_PLATFORMS and True or False

    # sets the initial value for the exit code that is
    # going to be used at the end of the cleanup operation
    exit_code = 0

    # iterates over all the scripts for execution, passing
    # the proper script values into each script for execution
    for script in SCRIPTS_LIST:
        # retrieves the script configuration file name in case
        # no configuration path is found no value is provided
        script_configuration_file_name = SCRIPTS_CONFIGURATION_MAP.get(script, None)

        # creates both the script and the configuration paths
        # note that there's a path normalization process
        script_path = os.path.join(directory_path, script)
        configuration_path = os.path.join(
            directory_path,
            os.path.join(CONFIGURATION_RELATIVE_PATH, script_configuration_file_name)
        ) if script_configuration_file_name else None

        # resolves both paths as absolute so that the proper value
        # is passed to the underlying command line execution
        if not script_path == None: script_path = os.path.abspath(script_path)
        if not configuration_path == None: configuration_path = os.path.abspath(configuration_path)

        # creates the arguments list from the various
        # processed arguments
        arguments = [PYTHON_COMMAND]
        arguments.append(script_path)
        arguments.append(target_path)
        if configuration_path:
            arguments.append(CONFIGURATION_FLAG)
            arguments.append(configuration_path)
        arguments.extend(extra_arguments)

        # prints a message and flushes the standard output
        extra.echo("------------------------------------------------------------------------")
        extra.echo("Executing script file: %s" % script)
        extra.echo("------------------------------------------------------------------------")
        sys.stdout.flush()

        # opens a sub-process for script execution (and waits for the end of it)
        process = subprocess.Popen(
            arguments,
            stdin = sys.stdin,
            stdout = sys.stdout,
            stderr = sys.stderr,
            shell = shell_value
        )
        process.wait()
        sys.stdout.flush()

        # in case the return code of the process is not the expected one (zero)
        # the final exit code to be returned by the process is changed to error
        if not process.returncode == 0: exit_code = 1

        # creates the proper prefix message using the return code from the process
        # note that the failed prefix is set for unwanted error codes
        prefix = "Finished" if process.returncode == 0 else "Finished (with errors)"

        # print a message and flushes the standard output
        extra.echo("------------------------------------------------------------------------")
        extra.echo("%s executing script file: %s" % (prefix, script))
        extra.echo("------------------------------------------------------------------------")
        sys.stdout.flush()

    # exits the current process with the code that has been calculated
    # from the execution of the various sub-scripts
    sys.exit(exit_code)

if __name__ == "__main__":
    run()
