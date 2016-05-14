"""
Replace the test framework with a service that can restart tests as needed
"""

import os
import sys
import json
import atexit

from django.apps import apps
from django.utils import autoreload
from django.test.utils import setup_test_environment, teardown_test_environment
from django.core.management.commands.test import Command as BaseCommand

SRV_ADDR = 'DJANGO_LIVE_TEST_SERVER_ADDRESS'

#
# Monkey patch to test django is still working before reloading
#
ORIG_HAS_CHANGED = autoreload.code_changed
def new_has_changed():
    """Catch critical errors before running the tests again"""
    ret = ORIG_HAS_CHANGED()
    #if ret:
    #    child = sp.Popen([sys.argv[0], 'check'], stdout=sp.PIPE)
    #    streamdata = child.communicate()[0]
        #print streamdata
    #    if child.returncode != 0:
    #        sys.stderr.write("Error detected! Pausing tests!")
    #        return False
    return ret
autoreload.code_changed = new_has_changed


class Command(BaseCommand):
    """Provide an autotest command that works like the normal test command"""
    config_file = '.autotest.conf'
    auto_module = ('/', 'tmp', 'autotest', 'at_lib')
    am_path = property(lambda self: os.path.join(*self.auto_module[:-1]))
    am_file = property(lambda self: os.path.join(*self.auto_module)+'.py')
    help = ('Discover and run tests in the specified modules or the current '
            'directory and restart when files change to re-run tests.')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.app = apps.get_app_config('autotest')
        self.config = {}

    def handle(self, *test_labels, **options):
        options['verbosity'] = int(options.get('verbosity'))
        if options.get('liveserver') is not None:
            os.environ[SRV_ADDR] = options['liveserver']
            del options['liveserver']

        if os.path.isfile(self.config_file):
            print "\n * Running tests!\n"
            from django.conf import settings
            with open(self.config_file, 'r') as fhl:
                self.config = json.loads(fhl.read())
            for (orig_name, test_name) in self.config.get('db', {}).items():
                for (_, conf) in settings.DATABASES.items():
                    if conf["NAME"] == orig_name:
                        conf["NAME"] = test_name

            settings.DEBUG = False
        else:
            set_title('setup')
            self.poke_module()

            self.config = self.setup_databases(**options)
            self.save_config()

            print "\n -= Testing Service Running; use [CTRL]+[C] to exit =-\n"

        sys.path.append(self.am_path)
        try:
            __import__(self.auto_module[-1])
        except ImportError:
            self.teardown_autotest((([]), []))
            sys.stdout.write("Config error, I've cleaned up, try again.\n")
            sys.exit(2)

        try:
            autoreload.main(self.inner_run, test_labels, options)
        except OSError:
            print "Exiting autorun."

    def poke_module(self):
        """Make a module we can import and use to re-run tests any time"""
        if not os.path.isdir(self.am_path):
            os.makedirs(self.am_path)
        with open(self.am_file, 'w') as fhl:
            fhl.write("# Force tests to reload with this file\n")

    def save_config(self):
        """Output our current state as a json file"""
        with open(self.config_file, 'w') as fhl:
            fhl.write(json.dumps(self.config))

    def setup_databases(self, **options):
        """Begin the process by creating the test database"""
        test_runner = get_test_runner(**options)
        old_config = test_runner.setup_databases()
        atexit.register(self.teardown_autotest, old_config, **options)

        config = {'db': {}}
        for conf in old_config[0]:
            config['db'][conf[1]] = conf[0].settings_dict['NAME']
        return config

    def teardown_autotest(self, old_config, **options):
        """Once all testing is complete, we tear down the database"""
        (amf, amp) = (self.am_file, self.am_path)
        for name in (self.config_file, amf, amf + 'c', amp):
            if os.path.isfile(name):
                os.unlink(name)
            elif os.path.isdir(name):
                os.rmdir(name)
        test_runner = get_test_runner(**options)
        test_runner.teardown_databases(old_config)
        print " +++ Test Service Finished"

    def inner_run(self, *test_labels, **options):
        """Inside the re-running test processes, this is a thread"""
        todo = self.config.get('todo', test_labels)
        if '*' in todo:
            todo = []

        if not todo:
            self.app.coverage_start()

        setup_test_environment()

        test_runner = get_test_runner(**options)

        try:
            suite = test_runner.build_suite(todo, None)
        except ImportError:
            print "Error, selected test module can't be found: %s" % str(todo)
            return self.ask_rerun()
        except AttributeError:
            print "Error, selected test function can't be found: %s" % str(todo)
            return self.ask_rerun()

        result = test_runner.run_suite(suite)

        teardown_test_environment()

        if not todo:
            self.app.coverage_report()

        failures = []
        for test, _ in result.errors + result.failures:
            (name, module) = str(test).rsplit(')', 1)[0].split(' (')
            if module == 'unittest.loader.ModuleImportFailure':
                (module, name) = name.rsplit('.', 1)
            failures.append('%s.%s' % (module, name))

        if not failures:
            if test_labels != todo:
                set_title('NOW PASS!')
                sys.stdout.write("\nFinally working!\n\n")

                if self.config.get('select', []):
                    # Set todo back to original selection
                    self.config['todo'] = self.config['select']
                else:
                    # Clear error todo (reset to test_labels)
                    del self.config['todo']

                self.save_config()
            else:
                set_title('PASS')
                print "\nStill working!\n"
            return self.ask_rerun()

        # Add all failues to next todo list (for re-run)
        self.config['todo'] = failures
        self.save_config()
        print_failures(failures)
        return self.ask_rerun(failures)

    def ask_rerun(self, failures=None):
        """Asks the user to type in what they would like to do"""
        while True:
            try:
                rerun = raw_input("Select failures to target "
                        "or press enter to re-run all: ").strip()

                self.config['select'] = list(get_selection(rerun, failures))
                self.config['todo'] = self.config['select']
            #pylint: disable=broad-except
            except Exception as error:
                sys.stdout.write(" ! Error in target: %s\n\n" % str(error))
                continue
            else:
                break
        self.save_config()
        if rerun != '-':
            self.poke_module()

def get_selection(rerun, failures):
    """Get's the selection from the user given response"""
    for failure in rerun.split(','):
        failure = failure.strip()
        if failure.isdigit() and failures:
            yield failures[int(failure)-1]
        elif failure:
            yield failure

def flush_database(db_name):
    """Remove all data that might be in a database left over"""
    from django.core.management import call_command
    call_command('flush', verbosity=0, interactive=False, database=db_name,
             skip_checks=True, reset_sequences=False, allow_cascade=True,
             inhibit_post_migrate=False)

def set_title(text):
    """Sets the title of the terminal windows"""
    sys.stdout.write("\x1b]2;@test %s\x07" % text)

def get_test_runner(**options):
    """Returns the currently used django test runner (configured)"""
    from django.conf import settings
    from django.test.utils import get_runner
    return get_runner(settings, options.get('testrunner'))()

def print_failures(failures):
    """Output a list of test failures"""
    set_title('FAIL [%d]' % len(failures))
    # Print options for user to select test target but
    # also set all failed tests as targets
    for enum, test in enumerate(failures):
        print "  %d. %s " % (enum + 1, test)

