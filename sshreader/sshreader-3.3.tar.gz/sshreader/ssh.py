#!/usr/bin/env python
# coding=utf-8
"""A wrapper for Paramiko that attempts to make ssh sessions easier to work with.  It also contains the
shell_command function for running local shell scripts!
"""
# Copyright (C) 2015 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function
import logging
import os
import paramiko
import warnings
from collections import namedtuple
from getpass import getuser
from subprocess import Popen, PIPE, STDOUT

__author__ = 'Jesse Almanrode (jesse@almanrode.com)'

# Using namedtuple because... why not?
ShellCommand = namedtuple('ShellCommand', ['cmd', 'stdout', 'stderr', 'return_code'])
ShellCommandCombined = namedtuple('ShellCommandCombined', ['cmd', 'stdout', 'return_code'])
EnvVars = namedtuple('EnvVars', ['username', 'rsa_key', 'dsa_key'])


def envvars():
    """ Attempt to determine the current username and location of any ssh keys.  If any value is unable to be determined
    it is returned as 'None'.

    :return: NamedTuple of (username, rsa_key, dsa_key)
    """
    user = None
    rsa_key = None
    dsa_key = None
    if os.getlogin() == getuser():
        user = getuser()
    userhome = os.path.expanduser('~')
    if os.path.exists(userhome + "/.ssh"):
        keyfiles = os.listdir(userhome + "/.ssh")
        if "id_rsa" in keyfiles:
            rsa_key = userhome + "/.ssh/id_rsa"
        if "id_dsa" in keyfiles:
            dsa_key = userhome + "/.ssh/id_dsa"
    return EnvVars(user, rsa_key, dsa_key)


def shell_command(command, combine=False, decodebytes=True):
    """Run a command in the shell on localhost and return the output

    :param command: String containing the shell script to run
    :param combine: Direct stderr to stdout
    :param decodebytes: Decode bytes objects to unicode strings
    :return: NamedTuple for (cmd, stdout, stderr) or (cmd, stdout)
    """
    if combine:
        pipeout = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        stdout, stderr = pipeout.communicate()
        assert stderr is None
        if decodebytes:
            result = ShellCommandCombined(cmd=command, stdout=stdout.decode().strip(),
                                          return_code=pipeout.returncode)
        else:
            result = ShellCommandCombined(cmd=command, stdout=stdout.strip(), return_code=pipeout.returncode)
    else:
        pipeout = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = pipeout.communicate()
        if decodebytes:
            result = ShellCommand(cmd=command, stdout=stdout.decode().strip(),
                                  stderr=stderr.decode().strip(), return_code=pipeout.returncode)
        else:
            result = ShellCommand(cmd=command, stdout=stdout.strip(), stderr=stderr.strip(),
                                  return_code=pipeout.returncode)
    return result


def do_shell_script(command, combine=False):
    """ Alias to shell_command.

    .. warning::

        This call will be deprecated in v4.0

    :param command: String containing the shell script to run
    :param combine: Combine stderr and stdout in output
    :return: NamedTuple for (cmd, stdout, stderr) or (cmd, stdout)
    """
    warnings.warn('<do_shell_script> will be replaced by <shell_command> in v4.0')
    return shell_command(command, combine=combine)


class SSH(object):
    """SSH Session object

    :param fqdn: Fully qualified domain name or IP address
    :param username: SSH username
    :param password: SSH password
    :param keyfile: SSH keyfile (can be used instead of password)
    :param port: SSH port
    :param timeout: SSH connection timeout in seconds
    :param connect: Initiate the connect
    :return: SSH connection object
    :raises: SSHException
    """
    def __init__(self, fqdn, username=None, password=None, keyfile=None, port=22, timeout=30, connect=True):
        if keyfile is None and username is None:
            raise paramiko.SSHException('You must specify a password or keyfile')
        self.host = fqdn
        self.username = username
        self.password = password
        if keyfile is not None:
            self.keyfile = os.path.abspath(os.path.expanduser(keyfile))
        else:
            self.keyfile = keyfile
        self.port = port
        self.timeout = timeout
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if connect:
            self.connect()

    def __enter__(self):
        if self.is_alive() is False:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def ssh_command(self, command, timeout=30, combine=False, decodebytes=True):
        """Run a command over an ssh connection

        :param command: The command to run
        :param timeout: Timeout for the command
        :param combine: Combine stderr and stdout
        :param decodebytes: Decode bytes objects to unicode strings
        :return: Namedtuple of (cmd, stdout, stderr, return_code) or (cmd, stdout, return_code)
        :raises: SSHException
        """
        if self.is_alive() is False:
            raise paramiko.SSHException("Connection is not established")
        if combine:
            # http://stackoverflow.com/questions/3823862/paramiko-combine-stdout-and-stderr
            chan = self.connection.get_transport().open_session()
            chan.settimeout(timeout)
            chan.get_pty()
            stdout_file = chan.makefile()
            chan.exec_command(command)
            stdout = stdout_file.read()
            stdout_file.close()
            if decodebytes:
                result = ShellCommandCombined(cmd=command, stdout=stdout.decode().strip(),
                                              return_code=chan.recv_exit_status())
            else:
                result = ShellCommandCombined(cmd=command, stdout=stdout.strip(), return_code=chan.recv_exit_status())
        else:
            stdin, stdout, stderr = self.connection.exec_command(command, timeout=timeout)
            if decodebytes:
                result = ShellCommand(cmd=command, stdout=stdout.read().decode().strip(),
                                      stderr=stderr.read().decode().strip(),
                                      return_code=stdout.channel.recv_exit_status())
            else:
                result = ShellCommand(cmd=command, stdout=stdout.read().strip(), stderr=stderr.read().strip(),
                                      return_code=stdout.channel.recv_exit_status())
        return result

    def close(self):
        """Closes an established ssh connection

        :return: None
        """
        self.connection.close()
        return None

    def is_alive(self):
        """Is an SSH connection alive

        :return: True or False
        :raises: SSHException
        """
        if self.connection.get_transport() is None:
            return False
        else:
            if self.connection.get_transport().is_alive():
                return True
            else:
                raise paramiko.SSHException("Unable to determine state of ssh session")

    def reconnect(self):
        """Alias to connect
        """
        return self.connect()

    def connect(self):
        """Opens an SSH Connection

        :return: True
        :raises: SSHException
        """
        logging.basicConfig()  # http://stackoverflow.com/questions/26659772/
        if self.is_alive():
            raise paramiko.SSHException("Connection is already established")
        if self.keyfile is not None:
            if self.username is not None:  # Key file with a custom username!
                self.connection.connect(self.host, port=self.port, username=self.username,
                                        key_filename=self.keyfile, timeout=self.timeout, look_for_keys=False)
            else:
                self.connection.connect(self.host, port=self.port, key_filename=self.keyfile,
                                        timeout=self.timeout, look_for_keys=False)
        else:  # Username and password combo
            if self.username is None or self.password is None:
                raise paramiko.SSHException("You must provide a username and password or supply an SSH key")
            else:
                self.connection.connect(self.host, port=self.port, username=self.username,
                                        password=self.password, timeout=self.timeout, look_for_keys=False)
        return True