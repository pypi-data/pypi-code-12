import functools
import pkg_resources

from pip.req import parse_requirements as parse_reqs

# Compatibility with older versions of pip
pip_dist = pkg_resources.get_distribution('pip')
pip_version = tuple(map(int, pip_dist.version.split('.')))

# Use a base partial that will be updated depending on the version of pip
parse_partial = functools.partial(parse_reqs, options=None)

if pip_version < (1, 2):
    # pip versions before 1.2 require an options keyword for using it outside
    # of invoking a pip shell command
    from pip.baseparser import parser
    parse_partial.keywords['options'] = parser.parse_args()[0]

if pip_version >= (1, 5):
    # pip 1.5 introduced a session kwarg that is required in later versions
    from pip.download import PipSession
    parse_partial.keywords['session'] = PipSession()


def parse_requirements(requirements_path='requirements.txt'):
    return [str(req.req) for req in parse_partial(requirements_path)]
