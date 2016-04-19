# -*- coding: utf-8 -*-

"""osxstrap.output: Handle CLI output."""

import sys

import click

def error(message=''):
	'''Print error message.'''
	click.secho('Error: %s' % message, fg='red')

def abort(message=''):
	'''Print error message and exit script.'''
	error(message)
	click.secho('Task aborted.', fg='red')
	sys.exit(1)

def warning(message=''):
	'''Print warning message.'''
	click.secho('Warning: %s' % message, fg='yellow')

def running(message=''):
	'''Print standard feedback message.'''
	click.secho(message, fg='blue')

def debug(message=''):
	'''Print debugging message.'''
	click.secho(message, fg='green')