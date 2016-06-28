from hackedit.api import versions


def test_get_versions():
    versions_dic = versions.get_versions()
    assert 'HackEdit' in versions_dic.keys()
    assert 'PyQt5' in versions_dic.keys()
    assert 'Python' in versions_dic.keys()
    assert 'pyQode' in versions_dic.keys()


def test_get_versions_str():
    versions_str = versions.versions_str()
    assert 'HackEdit' in versions_str
    assert 'PyQt5' in versions_str
    assert 'Python' in versions_str
    assert 'pyQode' in versions_str
