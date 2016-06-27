#!/usr/bin/env pythoni

import subprocess

def execute(command):
  """Executes a command on the system
  Input:
    command: string of the command
  Output:
    stdout(string), stderr(string)
  """
  callable_process =  subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, error = callable_process.communicate()
  returncode = callable_process.returncode
  return output, error, returncode
