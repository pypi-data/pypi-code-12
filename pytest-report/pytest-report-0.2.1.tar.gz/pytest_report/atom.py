import json


class Reporter:
    '''Atom Reporter
    Converts py.test reports into Atom's linter API message format.

    TODO: add example of atom's linter api message format
    '''

    def __init__(self, filename):
        self.filename = filename
        self.reports = []


    def save(self):
        with open(self.filename, 'w+') as archive:
            json.dump(self.reports, archive)

    def pytest_runtest_logreport(self, report):
        result = parse(report)
        if result:
            self.reports.append(result)

    # def pytest_assertrepr_compare(config, op, left, right):
    #     # return custom error
    #     return [str(left) + '!=' + str(right)]
    #     # use default error
    #     return None

def parse(report):
    if report.when != 'call':
        return None

    if report.outcome != 'failed':
        return None

    tracebacks = report.longrepr.reprtraceback.reprentries
    result = parse_trace(tracebacks[0])

    traces = [parse_trace(trace) for trace in tracebacks[1:]]

    extra = report.location[2].count('.')
    result['range'][0][1] += extra*4
    result['range'][1][1] += extra*4

    result['type'] = 'Error'
    result['trace'] = traces
    return result

def parse_trace(trace):
    # if no line starts with '>', default to the first line
    message = trace.lines[0]
    for line in trace.lines:
        # find the line with the right error in it
        if line.startswith('>'):
            # remove the first ">   " form the text
            message = line[4:]
            break

    # finding out the start and end of alphanumeric chars in the line
    start = len(message) - len(message.lstrip())
    end = start+len(message.strip())

    return {
        'type': 'Trace',
        'filePath': trace.reprfileloc.path,
        'text': message.strip(),
        'range':  [
            [trace.reprfileloc.lineno-1, start],
            [trace.reprfileloc.lineno-1, end],
        ]
    }
