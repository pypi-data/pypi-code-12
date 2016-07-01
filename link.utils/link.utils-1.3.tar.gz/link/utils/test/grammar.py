# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from link.utils.grammar import codegenerator
from grako.exceptions import FailedToken
import sys


class TestCodeGenerator(UTCase):
    def test_module(self):
        mod = codegenerator('mydsl', 'MyDSL', 'dsl = "DSL" ;')

        self.assertEqual(mod.__name__, 'mydsl')
        self.assertIn('mydsl', sys.modules)

        parser = mod.MyDSLParser()
        model = parser.parse('DSL', rule_name='dsl')

        self.assertEqual(model, 'DSL')

        with self.assertRaises(FailedToken):
            parser.parse('dsl', rule_name='dsl')


if __name__ == '__main__':
    main()
