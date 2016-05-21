from django.core.management import call_command
from django.test.runner import DiscoverRunner


class TestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        super(TestRunner, self).setup_databases(**kwargs)
        call_command('migrate_shards')

    def run_tests(self, test_labels=None, extra_tests=None, **kwargs):
        result = super(TestRunner, self).run_tests(['django_autoshard.tests'], extra_tests=None, **kwargs)
        return result

    def teardown_databases(self, old_config, **kwargs):
        try:
            super(TestRunner, self).teardown_databases(old_config, **kwargs)
        except TypeError:
            pass
