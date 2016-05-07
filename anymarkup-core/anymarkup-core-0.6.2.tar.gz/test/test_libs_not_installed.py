from flexmock import flexmock
import pytest
import yaml

import anymarkup_core


class TestLibsNotInstalled(object):
    # json is always there, since we only support Python >= 2.7
    @pytest.mark.parametrize(('fmt', 'lib'), [
        ('ini', 'configobj'),
        ('xml', 'xmltodict'),
        ('yaml', 'yaml'),
    ])
    def test_raises_proper_error(self, fmt, lib):
        flexmock(anymarkup_core).should_receive(lib).and_return(None)
        flexmock(anymarkup_core).should_receive('fmt_to_lib').and_return({fmt: (None, lib)})

        with pytest.raises(anymarkup_core.AnyMarkupError):
            anymarkup_core.parse('', format=fmt)

        with pytest.raises(anymarkup_core.AnyMarkupError):
            anymarkup_core.serialize('', format=fmt)

    def test_uninstalled_dep_doesnt_make_parsing_fail_for_installed_deps(self):
        flexmock(anymarkup_core).should_receive('configobj').and_return(None)
        flexmock(anymarkup_core).should_receive('fmt_to_lib').\
            and_return({'ini': (None, ''), 'yaml': (yaml, '')})

        with pytest.raises(anymarkup_core.AnyMarkupError):
            anymarkup_core.parse('', format='ini')

        assert anymarkup_core.parse('foo: bar') == {'foo': 'bar'}

        with pytest.raises(anymarkup_core.AnyMarkupError):
            anymarkup_core.serialize('', format='ini')

        assert anymarkup_core.serialize({'foo': 'bar'}, format='yaml') == b'foo: bar\n'
