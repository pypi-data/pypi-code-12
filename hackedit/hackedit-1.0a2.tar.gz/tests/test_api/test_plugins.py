import pytest

from hackedit.api import plugins
import pytest_hackedit

from .test_window import PROJ_PATH


class MyWorkspacePlugin(plugins.WorkspacePlugin):
    def activate(self):
        print('plugin activated')


def test_workspace_plugin_interface():
    p = MyWorkspacePlugin(4)
    p.main_window == 4
    p.get_preferences_page()
    p.apply_preferences()
    p.close()
    assert p.ENTRYPOINT == plugins.WorkspacePlugin.ENTRYPOINT


def test_editor_plugin_interace():
    assert plugins.EditorPlugin.get_editor_class() is None
    assert plugins.EditorPlugin.get_specific_preferences_page() is None
    plugins.EditorPlugin.apply_specific_preferences(object())


def test_preference_page():
    assert plugins.PreferencePagePlugin.get_preferences_page() is None


def test_entry_points():
    assert plugins.EditorPlugin.ENTRYPOINT != \
        plugins.FileIconProviderPlugin.ENTRYPOINT != \
        plugins.PreferencePagePlugin.ENTRYPOINT != \
        plugins.WorkspacePlugin.ENTRYPOINT


def test_get_plugin_instance(qtbot):
    from hackedit.plugins.outline import DocumentOutline
    with pytest_hackedit.MainWindow(PROJ_PATH):
        p = plugins.get_plugin_instance(DocumentOutline)
        assert p is not None
        assert isinstance(p, DocumentOutline)
        with pytest.raises(TypeError):
            p = plugins.get_plugin_instance(qtbot)
