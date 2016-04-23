import functools
import signal
import os
import io


def _write(handle, message):
    if isinstance(handle, io.TextIOWrapper):
        handle.write(message)
    else:
        handle.write(message.encode('utf8'))
    handle.flush()

def log(message):
    """Output to stdout."""
    import sys
    _write(sys.stdout, message)

def warn(message):
    """Output to stderr."""
    import sys
    _write(sys.stderr, message)

def do_exit(signal, frame):
    """Just exit."""
    import sys
    sys.exit(1)

def signals_trigger_exit():
    """Make all signals cause a system exit."""
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGQUIT, do_exit)

def ignore_signals():
    """Ignore all signals (e.g. ctrl-C)."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)

def signal_pass_on_to_separate_process_group(pid):
    def pass_on_signal(pid, signum, frame):
        os.kill(pid, signum)

    signal.signal(signal.SIGINT, functools.partial(pass_on_signal, pid))
    signal.signal(signal.SIGTERM, functools.partial(pass_on_signal, pid))
    signal.signal(signal.SIGHUP, functools.partial(pass_on_signal, pid))
    signal.signal(signal.SIGQUIT, functools.partial(pass_on_signal, pid))

def extract_archive(filename, directory):
    patoolib.extract_archive(filename, outdir=directory)

def get_hitch_directory():
    """Get the hitch directory by working backwards from the virtualenv python."""
    import sys
    return os.path.abspath(
        os.path.join(os.path.dirname(sys.executable), "..", "..")
    )
