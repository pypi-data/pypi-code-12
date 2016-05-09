#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import io

from .testcase import TestCase
from pdml2flow.conf import Conf

class TestConf(TestCase):

    def test_get_real_paths(self):
        p = Conf.get_real_paths([
            'this{}is{}a{}path'.format(*[Conf.FLOW_DEF_NESTCHAR]*3)
        ], Conf.FLOW_DEF_NESTCHAR)
        self.assertEqual(p , [['this', 'is', 'a', 'path', 'raw']])

    def test_set(self):
        """Check
            * Setting a value actually sets it in Conf (case independant)
            * Setting a value does not change on other value
            * None values are rejected
            * False values are accepted
        """
        d = Conf.DEBUG
        m = Conf.DATA_MAXLEN
        e = Conf.EXTRACT_SHOW
        t = Conf.FLOW_BUFFER_TIME
        newConf = dict()
        newConf['debug'] = not d
        newConf['DATA_MAXLEN'] = m + 1
        newConf['FLOW_BUFFER_TIME'] = None
        newConf['A_NEW_FALSE'] = False
        Conf.set(newConf)
        self.assertEqual(Conf.DEBUG, not d)
        self.assertEqual(Conf.DATA_MAXLEN, m + 1)
        self.assertEqual(Conf.EXTRACT_SHOW, e)
        self.assertEqual(Conf.FLOW_BUFFER_TIME, t)
        self.assertEqual(Conf.A_NEW_FALSE, False)

    def test_get(self):
        """Check if
            * no functions returned
            * not private
            * not protected
            * uppercase
        """
        for name, value in Conf.get().items():
            with self.subTest(test=name):
                self.assertFalse(callable(value))
                self.assertFalse(name.startswith("_"))
                self.assertFalse(name.startswith("__"))
                self.assertTrue(name.isupper())

if __name__ == '__main__':
    unittest.main()
