"""
Some wrapper around flit's internals
"""


from pathlib import Path
from flit.inifile import _validate_config, _read_pkg_ini
from contextlib import contextmanager

@contextmanager
def modify_config(path):
    """
    Context manager to modify a flit config file.

    Will read the config file, validate the config, yield the config object,
    validate and write back the config to the file on exit
    """
    if isinstance(path, str):
        path = Path(path)
    config = _read_pkg_ini(path)
    _validate_config(config, path)

    # don't catch exception, we won't write the new config.
    yield config

    _validate_config(config, path)
    with path.open('w') as f:
        config.write(f)

def python_requires(version=None):
    path = Path('./flit.ini')
    if path.exists():
        with modify_config(path) as config:
            current_version = config['metadata'].get('requires-python')
            if current_version is None:
                if not version:
                    new_version = input("what's you Python version requirement ? [>=3.4]")
                else:
                    new_version = version
                if not new_version.strip():
                    new_version = '>=3.4'
                config['metadata']['requires-python'] = new_version


