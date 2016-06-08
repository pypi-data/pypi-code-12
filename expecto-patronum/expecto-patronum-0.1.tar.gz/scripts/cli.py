# encoding: UTF-8

import os, sys, click, config
from interpreter import Interpreter

def validate_playbook(ctx, param, value):
  if value is not None:
    if os.path.isfile(value):
      return value
  print("expecto: %s: No such file or directory" % value)
  sys.exit(1)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--playbook',
  callback=validate_playbook,
  help='path of config file written by YAML.')
@click.option('--bookmark',
  help = 'starting position.')
def expecto(playbook, bookmark):
  interpreter = Interpreter(config.from_file(playbook, bookmark))
  interpreter.interpret()
