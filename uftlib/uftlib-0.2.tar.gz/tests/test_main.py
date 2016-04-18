# -*- coding: utf-8 -*-

import traceback
from uftlib import UFTemplate


class TestMain(object):
    def test_simple_functionality(self):
        t = UFTemplate("x=0", "x+=1", "${x}")
        assert t.render() == '1'

    def test_render_many(self):
        t = UFTemplate('s = "x"', 's += "y"', "${s}")
        assert t.render_many(howmany=3) == ['xy', 'xyy', 'xyyy']

    def test_reset(self):
        t = UFTemplate("x=0", "x+=1", "${x}")
        assert t.render_many(howmany=4) == ['1', '2', '3', '4']
        assert t.render() == '5'
        t.reset()
        assert t.render_many(howmany=4) == ['1', '2', '3', '4']

    def test_exception_initial(self):
        code_initial = """
s = "something"
s = s + 1234
"""
        _exc = True
        try:
            t = UFTemplate(initial=code_initial, template="${s}")
        except:
            _exc = traceback.format_exc()
            assert "TypeError: cannot concatenate 'str' and 'int' objects" in _exc

        if not _exc:
            raise

    def test_exception_cycle(self):
        code_initial = """
s = "something"
"""
        code_cycle = """s += 1"""
        _exc = True
        try:
            t = UFTemplate(initial=code_initial, oncycle=code_cycle, template="${s}")
        except:
            _exc = traceback.format_exc()
            assert "TypeError: cannot concatenate 'str' and 'int' objects" in _exc

        if not _exc:
            raise
