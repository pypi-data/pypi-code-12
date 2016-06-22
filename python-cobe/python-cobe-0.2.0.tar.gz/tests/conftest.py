import pathlib

import pytest


@pytest.fixture()
def directory(tmpdir):
    """A temporary directory as a :class:`pathlib.Path`."""
    return pathlib.Path(tmpdir.strpath)
