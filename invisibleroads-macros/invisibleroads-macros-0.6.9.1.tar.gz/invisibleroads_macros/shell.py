import shlex
import subprocess
from six import string_types

from .exceptions import InvisibleRoadsError


def run_command(command, exception_by_error=None):
    if not isinstance(command, string_types):
        command = ' '.join(command)
    command = command.split(';', 1)[0]
    return run_raw_command(command, exception_by_error)


def run_raw_command(command, exception_by_error=None):
    if isinstance(command, string_types):
        command = shlex.split(command)
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        o = e.output
        for error_text, exception in (exception_by_error or {}).items():
            if error_text in o:
                raise exception
        else:
            raise InvisibleRoadsError(o)
    except OSError as e:
        raise InvisibleRoadsError(e.strerror)
    return output.strip()
