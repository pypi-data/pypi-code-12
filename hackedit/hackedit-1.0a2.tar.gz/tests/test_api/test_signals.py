import pytest

import pytest_hackedit
from hackedit.api import signals

from .test_window import PROJ_PATH


@pytest.mark.parametrize('signal', signals.SIGNALS)
def test_connect_slot(signal):
    def slot():
        pass
    with pytest_hackedit.MainWindow(PROJ_PATH):
        signals.connect_slot(signal, slot)
        signals.disconnect_slot(signal, slot)


def test_invalid_signal():
    def slot():
        pass
    with pytest.raises(ValueError):
        signals.connect_slot('invalid_signal', slot)
    with pytest.raises(ValueError):
        signals.disconnect_slot('invalid_signal', slot)
