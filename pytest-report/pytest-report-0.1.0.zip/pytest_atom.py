import json


filename = 'report.json'
reports = []

def pytest_configure(config):
    fname = config.getoption('atom')
    if fname:
        config._reporter = AtomReporter(fname)
        print('pytest-atom: AtomReporter registered')

    elif config.getoption('dump'):
        config._reporter = ReportDumper('reports.json')
        print('pytest-atom: ReportDumper registered')

    if hasattr(config, '_reporter'):
        config.pluginmanager.register(config._reporter)
        print('pytest-atom: %s registered' % type(config._reporter))


def pytest_unconfigure(config):
    if not hasattr(config, '_reporter'):
        return
    reporter = config._reporter
    del config._reporter
    config.pluginmanager.unregister(reporter)
    reporter.save()
    print('pytest-atom: unconfigured')


class ReportDumper:
    def __init__(self, filename):
        self.filename = filename
        self.reports = []

    def pytest_runtest_logreport(self, report):
        self.reports.append(process(report))

    def save(self):
        with open(self.filename, 'w') as archive:
            json.dump(self.reports, archive)


class AtomReporter:
    def __init__(self, filename):
        self.filename = filename
        self.reports = []

    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return None

        # TODO: add support for skipped tests
        if report.outcome != 'failed':
            return None

        result = {
            'type': 'Error',
            # 'filePath': report.location[0],
            'range': [
                [report.location[1]-1, 0],
                [report.location[1]-1, 1000],
            ]
        }

        info = report.longrepr.reprcrash
        result['text'] = info.message
        result['range'] = location(info.lineno, 0, 1000)
        result['filePath'] = info.path

        traces = report.longrepr.reprtraceback.reprentries
        tmp = parse_trace(traces[0])
        if '.' in report.location[2]:
            tmp['range'][0][1] += 4
            tmp['range'][1][1] += 4
        result['range'] = tmp['range']
        result['filePath'] = tmp['filePath']

        if len(traces) > 1:
            result['trace'] = [parse_trace(trace, True) for trace in traces[1:-1]]
            result['trace'].append(parse_trace(traces[-1]))

        self.reports.append(result)

    def save(self):
        with open(self.filename, 'w') as archive:
            json.dump(self.reports, archive)


def parse_trace(trace, noArrow=False):
    result = {
        'type': 'Trace',
    }
    for line in trace.lines:
        if not noArrow:
            if not line.startswith('>'):
                continue

        print('failed &:', line)
        result['long'] = line
        result['text'] = line[1:].strip()
        x = 0
        line = line[4:]
        while line[0] == ' ':
            x += 1
            line = line[1:]
        result['range'] = location(trace.reprfileloc.lineno, x, x+len(line))
        result['filePath'] = trace.reprfileloc.path
    return result

def location(lineno, start, end):
    return [[lineno-1, start], [lineno-1, end]]

def marshall(obj):
    return dict(obj.__dict__)

def process(report):
    return dict(
        location=report.location,
        when=report.when,
        skipped=report.skipped,
        duration=report.duration,
        longrepr=unmarshal(report.longrepr),
        outcome=report.outcome,
        sections=report.sections,
        passed=report.passed,
    )

def unmarshal_traceback(entry):
    return {
        'lines': entry.lines,
        'line': entry.reprfileloc.lineno,
        'message': entry.reprfileloc.message,
        'path': entry.reprfileloc.path,
    }
def unmarshal(error):
    if not error:
        return None
    if 'FixtureLookup' in str(type(error)):
        return None
    return {
        'traces': {
            'style': error.reprtraceback.style,
            'extraline': error.reprtraceback.extraline,
            'reprentries': [unmarshal_traceback(e) for e in error.reprtraceback.reprentries],
        },
        'info': {
            'path': error.reprcrash.path,
            'lineno': error.reprcrash.lineno,
            'message': error.reprcrash.message,
        },
    }


def pytest_addoption(parser):
    group = parser.getgroup('atom')
    group.addoption(
        '--atom',
        action='store',
        dest='atom',
        default=None,
        help='output file for the json report.'
    )

    group.addoption(
        '--dump',
        action='store',
        dest='dump',
        default=None,
        help='output file for the json report.'
    )
