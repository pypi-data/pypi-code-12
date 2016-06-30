import tempfile
import os

from django.test.runner import DiscoverRunner
import django
from django.conf import settings

from ldb.django.test.testcases import DjangoAppTestCaseMixin


def get_apps(test_or_suite):
    apps = set()
    if isinstance(test_or_suite, DjangoAppTestCaseMixin):
        apps.update(set(test_or_suite.get_applications()))
    else:
        for sub_test_or_suite in test_or_suite:
            apps.update(get_apps(sub_test_or_suite))

    return apps


class DjangoTestRunner(DiscoverRunner):
    def run(self, test):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_filename = tmp_file.name
        tmp_file.close()

        installed_apps = list(get_apps(test))
        settings.configure(DEBUG=True,
                           DATABASES={
                               'default': {
                                   'ENGINE': 'django.db.backends.sqlite3',
                                   'NAME': tmp_filename,
                               }
                           },
                           INSTALLED_APPS=installed_apps,
                           )

        django.setup()

        self.setup_test_environment()
        old_config = self.setup_databases()

        results = self.run_suite(test)

        self.teardown_databases(old_config)
        self.teardown_test_environment()

        os.remove(tmp_filename)

        return results
