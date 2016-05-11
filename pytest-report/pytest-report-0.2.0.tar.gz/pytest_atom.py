import reporters.dump
import reporters.atom


def pytest_configure(config):
    fname = config.getoption('atom')

    if fname:
        config._reporter = reporters.atom.Reporter(fname)

    elif config.getoption('dump'):
        config._reporter = reporters.dump.Reporter('reports.json')

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
