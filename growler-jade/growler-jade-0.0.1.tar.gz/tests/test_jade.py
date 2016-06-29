#
# tests/test_jade.py
#


import pytest

import growler_jade
import growler_jade.jade_renderer
from growler_jade.jade_renderer import JadeRenderer


@pytest.fixture
def renderer(tmpdir):
    return JadeRenderer(str(tmpdir))


def test_renderer(renderer):
    assert isinstance(renderer, growler_jade.jade_renderer.JadeRenderer)


def test_imports():
    growler_ext = pytest.importorskip('growler.ext')

    assert growler_ext.JadeRenderer is JadeRenderer
    assert growler_ext.jade_renderer is growler_jade


def xtest_render_html(renderer, tmpdir):
    fname = tmpdir + "/file"
    print(fname)
    with open(fname, 'w') as f:
        f.write("""#vid\n  color blue""")
    m = mock.Mock()
    renderer.render_html(fname, m)

    assert None
