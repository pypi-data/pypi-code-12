from subprocess import check_output, CalledProcessError, DEVNULL


def command(*args):
    out = check_output(['git'] + list(args), stderr=DEVNULL)
    return out.decode('utf-8').strip()


def count(tag=None):
    if tag:
        return command('rev-list', '--count', '{}..HEAD'.format(tag))
    else:
        return command('rev-list', '--count', 'HEAD')


def short():
    return command('rev-parse', '--short', 'HEAD')


def tag():
    try:
        return command('describe', '--abbrev=0')
    except CalledProcessError:
        pass
