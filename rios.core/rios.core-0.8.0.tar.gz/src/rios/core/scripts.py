#
# Copyright (c) 2015, Prometheus Research, LLC
#


import argparse
import pkg_resources
import sys

from six import iteritems

from .validation import *


__all__ = (
    'ValidationScript',
    'validate',
)


VALIDATORS = {
    'instrument': lambda x, instrument: validate_instrument(x),
    'assessment': validate_assessment,
    'calculationset': validate_calculationset,
    'form': validate_form,
    'interaction': validate_interaction,
}


class ValidationScript(object):
    def __init__(self):
        self._stdout = None

        self.parser = argparse.ArgumentParser(
            description='A tool for validating the format of RIOS files.',
        )

        try:
            self_version = \
                pkg_resources.get_distribution('rios.core').version
        except pkg_resources.DistributionNotFound:  # pragma: no cover
            self_version = 'UNKNOWN'
        self.parser.add_argument(
            '-v',
            '--version',
            action='version',
            version='%(prog)s ' + self_version,
        )

        self.parser.add_argument(
            'spectype',
            choices=[
                'instrument',
                'assessment',
                'calculationset',
                'form',
                'interaction',
            ],
            help='The type of RIOS file to validate.',
        )

        self.parser.add_argument(
            'filename',
            type=argparse.FileType('r'),
            help='The file containing the structure to validate. To read from'
            ' standard input, specify a "-" here.',
        )

        self.parser.add_argument(
            '-i',
            '--instrument',
            type=argparse.FileType('r'),
            help='The file containing the Common Instrument Definition to'
            ' validate against. To read from standard input, specify a "-"'
            ' here.',
        )

    def __call__(self, argv=None, stdout=sys.stdout):
        args = self.parser.parse_args(argv)
        self._stdout = stdout

        try:
            VALIDATORS[args.spectype](
                args.filename,
                instrument=args.instrument,
            )
        except ValidationError as exc:
            self.out('FAILED validation.')
            for source, message in iteritems(exc.asdict()):
                self.out('%s: %s' % (
                    source,
                    message,
                ))
            return 1
        else:
            self.out('Successful validation.')
            return 0

    def out(self, message):
        self._stdout.write('%s\n' % (message,))


validate = ValidationScript()  # pylint: disable=invalid-name

