from hackedit.api import gettext


def test_get_translation():
    gettext.set_locale('fr')
    ret = gettext.get_translation()
    assert ret is not None

    ret = gettext.get_translation(package='hackedit-python')
    assert ret is not None

    # test with a locale that does not exists
    gettext.set_locale('martian')
    gettext.get_translation()

    gettext.set_locale('fr')


def test_get_available_locales():
    assert len(gettext.get_available_locales()) >= 2
