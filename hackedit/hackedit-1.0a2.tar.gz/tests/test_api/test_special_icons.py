from PyQt5 import QtGui
import pytest
from hackedit.app import settings
from hackedit.api.special_icons import *
from hackedit.app.forms import hackedit_rc
assert hackedit_rc


@pytest.mark.parametrize('fct', [
    configure_icon,
    run_icon,
    run_debug_icon,
    class_icon,
    variable_icon,
    function_icon,
    namespace_icon,
    object_locked,
    object_unlocked
])
def test_icon_functions(qtbot, fct):
    for dark in [True, False]:
        settings.set_dark_theme(dark)
        icon = fct()
        assert isinstance(icon, QtGui.QIcon)
