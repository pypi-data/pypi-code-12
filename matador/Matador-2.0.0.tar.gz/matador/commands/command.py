#!/usr/bin/env python
import logging
import argparse
from matador.session import Session


class Command(object):

    def __init__(self, init_session=True, **kwargs):
        if kwargs:
            # If kwargs have been supplied, use these in same way argsparse
            # would.
            # Mainly used for testing, but could be used to run commands from
            # within python scripts.

            # We can't add attributes to instances of Object, so we need create
            # a new class.
            class Args(object):
                pass

            self.args = Args()
            for key, value in kwargs.items():
                setattr(self.args, key, value)
        else:
            # If the command is created from the command line, we'll have
            # arguments to parse.
            parser = argparse.ArgumentParser(
                description="Taming the bull: Change management for Agresso systems")
            self._add_arguments(parser)
            self.args, unknown = parser.parse_known_args()

        self._logger = logging.getLogger(__name__)
        if init_session:
            Session.initialise()
        self._execute()

    def _add_arguments(self, parser):
        pass

    def _execute(self):
        raise NotImplementedError
