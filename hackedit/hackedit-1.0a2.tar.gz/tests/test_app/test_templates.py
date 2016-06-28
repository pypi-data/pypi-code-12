import os
import tempfile
import shutil

from hackedit.app import templates


SOURCE_A = 'tests/data/templates/source_a'
SOURCE_B = 'tests/data/templates/source_b'
SOURCE_PYTHON = 'tests/data/templates/python'


def test_add_source():
    templates.clear_sources()
    templates.add_source('Test', '/a/path')
    templates.add_source('Test2', '/a/path2')
    assert len(templates.get_sources()) == 2


def test_rm_source():
    templates.clear_sources()
    templates.add_source('Test', '/a/path')
    templates.add_source('Test2', '/a/path2')
    templates.rm_source('Test2')
    assert len(templates.get_sources()) == 1


def test_clear_source():
    templates.clear_sources()
    templates.add_source('Test', '/a/path')
    templates.add_source('Test2', '/a/path2')
    assert len(templates.get_sources()) == 2
    templates.clear_sources()
    assert len(templates.get_sources()) == 0


def test_get_templates():
    templates.add_source('SOURCE_A', SOURCE_A)
    templates.add_source('SOURCE_B', SOURCE_B)

    assert len(list(templates.get_templates())) == 4
    assert len(list(templates.get_templates(category='Project'))) == 2
    assert len(list(templates.get_templates(category='File'))) == 2
    assert len(list(templates.get_templates(source_filter='SOURCE_A'))) == 2
    assert len(list(templates.get_templates(source_filter='SOURCE_B'))) == 2
    assert len(list(templates.get_templates(category='File', source_filter='SOURCE_A'))) == 1
    assert len(list(templates.get_templates(category='File', source_filter='SOURCE_B'))) == 1
    assert len(list(templates.get_templates(category='Project', source_filter='SOURCE_A'))) == 1
    assert len(list(templates.get_templates(category='Project', source_filter='SOURCE_B'))) == 1


def test_get_template():
    templates.add_source('SOURCE_A', SOURCE_A)
    templates.add_source('SOURCE_B', SOURCE_B)
    assert templates.get_template('SOURCE_A', 'foo') is None
    assert templates.get_template('SOURCE_A', 'COBOL file (FREE FORMAT)') is not None
    assert templates.get_template('SOURCE_B', 'COBOL file (FREE FORMAT)') is None


def test_create():
    templates.add_source('Python', SOURCE_PYTHON)
    tmpl = templates.get_template('Python', 'Python library')
    dest_dir = os.path.join(tempfile.gettempdir(), 'TestPythonLibTemplate')
    try:
        shutil.rmtree(dest_dir)
    except FileNotFoundError:
        pass
    files = templates.create(tmpl, dest_dir, {
        'project': 'MyProject',
        'package': 'my_project',
        'version': '1.0.0',
        'description': '',
        'creator': 'Colin Duquesnoy',
        'email': '',
        'license': 'GPL',
        'url': 'www.my_project.com'
    })
    assert len(files) == 8
    pth_setup = os.path.join(dest_dir, 'setup.py')
    assert os.path.exists(pth_setup)
    with open(pth_setup, 'r') as f:
        content = f.read()
        assert "@" not in content
