import json


class ReportEncoder(json.JSONEncoder):
    def default(self, obj):
        result = obj.__dict__
        result['_type'] = str(type(obj))
        if 'keywords' in result:
            del result['keywords']
        return result


class Reporter:
    def __init__(self, filename):
        self.filename = filename
        self.reports = []

    def save(self):
        with open(self.filename, 'w+') as archive:
            json.dump(self.reports, archive, cls=ReportEncoder)

    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return None

        if report.outcome != 'failed':
            return None

        self.reports.append(report)
