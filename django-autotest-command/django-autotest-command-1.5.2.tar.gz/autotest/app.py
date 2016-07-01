
from django.apps import AppConfig

try:
    from coverage import Coverage
    coverage = Coverage()
    coverage.start()
except ImportError:
    coverage = None

class AutotestConfig(AppConfig):
    name = 'autotest'

    def __init__(self, *args, **kwargs):
        super(AutotestConfig, self).__init__(*args, **kwargs)
        self.coverage = None

    def coverage_start(self):
        if coverage and not self.coverage:
            self.coverage = Coverage()
            self.coverage.start()
            return self.coverage

    def coverage_report(self):
        if coverage and self.coverage:
            self.coverage.stop()
            coverage.stop()
            self.coverage.get_data().update(coverage.get_data())
            self.coverage.html_report()

