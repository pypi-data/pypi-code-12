settings = {
    'SCREENSHOTS_PATH': None,
    'PDIFF_PATH': None,
    'ALLOW_SCREENSHOT_CAPTURE': False
}


def pytest_addoption(parser):
    group = parser.getgroup('selenium-pdiff', 'selenium-pdiff')
    group._addoption('--allow-screenshot-capture',
                     help='Allow capturing of missing screenshots.',
                     metavar='bool')
    group._addoption('--screenshots-path',
                     help='Path for captured screenshots.',
                     metavar='str')
    group._addoption('--pdiff-path',
                     metavar='path',
                     help='path to pdiff output')


def pytest_configure(config):
    settings['SCREENSHOTS_PATH'] = config.getoption('screenshots_path')
    settings['PDIFF_PATH'] = config.getoption('pdiff_path')
    settings['ALLOW_SCREENSHOT_CAPTURE'] = config.getoption('allow_screenshot_capture')
