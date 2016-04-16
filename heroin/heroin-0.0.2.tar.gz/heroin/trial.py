import django
from django.conf import settings
from django.test import runner as django_runner
from django.test.utils import setup_test_environment, teardown_test_environment

from twisted.python import usage
from twisted.scripts import trial as utils
from twisted.trial import runner

import os
import runpy
import sys


class HeroinRunner(runner.TrialRunner):

    def __init__(
        self,
        verbosity=1,
        interactive=False,
        keepdb=False,
        reverse=False,
        debug_sql=False,
        *args, **kwargs
    ):

        self.verbosity = verbosity
        self.interactive = interactive
        self.keepdb = keepdb
        self.reverse = reverse
        self.debug_sql = debug_sql

        super(HeroinRunner, self).__init__(*args, **kwargs)

    def setup_databases(self):
        return django_runner.setup_databases(
            self.verbosity, self.interactive, self.keepdb, self.debug_sql
        )

    def teardown_databases(self, old_config):
        """
        Destroys all the non-mirror databases.
        """
        major, minor = django.VERSION[:2]
        if major == 1 and minor < 9:
            old_config, _ = old_config
        for connection, old_name, destroy in old_config:
            if destroy:
                connection.creation.destroy_test_db(
                    old_name, self.verbosity, self.keepdb
                )


    def _runWithoutDecoration(self, test, forceGarbageCollection=False):
        setup_test_environment()
        old_config = self.setup_databases()
        result = super(HeroinRunner, self)._runWithoutDecoration(
            test, forceGarbageCollection
        )
        self.teardown_databases(old_config)
        teardown_test_environment()
        return result

    @classmethod
    def parseConfig(cls, config):

        args = {'reporterFactory': config['reporter'],
                'tracebackFormat': config['tbformat'],
                'realTimeErrors': config['rterrors'],
                'uncleanWarnings': config['unclean-warnings'],
                'logfile': config['logfile'],
                'workingDirectory': config['temp-directory']}
        if config['dry-run']:
            args['mode'] = HeroinRunner.DRY_RUN

        elif config['jobs']:
            raise NotImplementedError
            # TODO: Figure out how to integrate jobs
            # from twisted.trial._dist.disttrial import DistTrialRunner
            # cls = DistTrialRunner
            # args['workerNumber'] = config['jobs']
            # args['workerArguments'] = config._getWorkerArguments()

        else:
            if config['debug']:
                args['mode'] = HeroinRunner.DEBUG
                debugger = config['debugger']

                if debugger != 'pdb':
                    try:
                        args['debugger'] = utils.reflect.namedAny(debugger)
                    except utils.reflect.ModuleNotFound:
                        raise utils._DebuggerNotFound(
                            '%r debugger could not be found.' % (debugger,))
                else:
                    args['debugger'] = utils._wrappedPdb()

            args['exitFirst'] = config['exitfirst']
            args['profile'] = config['profile']
            args['forceGarbageCollection'] = config['force-gc']

        return cls(**args)


def _getSuite(config):
    loader = utils._getLoader(config)
    loader.modulePrefix = 'test'
    recurse = not config['no-recurse']
    return loader.loadByNames(config['tests'], recurse=recurse)



class Options(utils.Options):

    optFlags = [["nomigrations", "nm"], ]

    optParameters = [
        [
            "settings", None, None,
            "the fully qualified name of the settings module to use"
        ],
        [
            "config", None, None,
            (
                "the fully qualified name of a configuration module to "
                "execute. Note that this should be a script to execute"
            )
        ],
    ]

    def opt_version(self):
        from heroin import __version__
        from twisted import copyright
        print "Twisted version:", copyright.version
        print 'Herion version:', __version__
        sys.exit(0)

    def opt_settings(self, value):
        if value is not None:
            os.environ['DJANGO_SETTINGS_MODULE'] = value
            self['settings'] = value

    def opt_config(self, value):
        if value is not None:
            runpy.run_module(value)


class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


def run():
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    config = Options()
    try:
        config.parseOptions()
    except usage.UsageError as uerr:
        raise SystemExit("%s: %s" % (sys.argv[0], uerr))
    utils._initialDebugSetup(config)

    try:
        _runner = HeroinRunner.parseConfig(config)
    except utils._DebuggerNotFound as exc:
        raise SystemExit('%s: %s' % (sys.argv[0], str(exc)))

    django.setup()
    settings.DEBUG = False

    suite = _getSuite(config)

    if config.get('nomigrations'):
        settings.MIGRATION_MODULES = DisableMigrations()

    if config['until-failure']:
        test_result = _runner.runUntilFailure(suite)
    else:
        test_result = _runner.run(suite)
    if config.tracer:
        sys.settrace(None)
        results = config.tracer.results()
        results.write_results(
            show_missing=1, summary=False, coverdir=config.coverdir().path
        )
    sys.exit(not test_result.wasSuccessful())
