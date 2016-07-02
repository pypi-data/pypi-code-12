# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from link.utils.grammar import codegenerator, adopt_children, find_ancestor
from grako.model import ModelBuilderSemantics, Node
from grako.exceptions import FailedToken
import sys


class TestGrammar(UTCase):
    def test_codegenerator(self):
        mod = codegenerator('mydsl', 'MyDSL', 'dsl = "DSL" ;')

        self.assertEqual(mod.__name__, 'mydsl')
        self.assertIn('mydsl', sys.modules)

        parser = mod.MyDSLParser()
        model = parser.parse('DSL', rule_name='dsl')

        self.assertEqual(model, 'DSL')

        with self.assertRaises(FailedToken):
            parser.parse('dsl', rule_name='dsl')

    def test_adopt_children(self):
        mod = codegenerator('mydsl', 'MyDSL', '''
        subnode::SubNode = v:"DSL" ;
        dsl::RootNode = sub:{ subnode }+ ;
        ''')

        parser = mod.MyDSLParser(semantics=ModelBuilderSemantics())
        model = parser.parse('DSL', rule_name='dsl')
        self.assertIsInstance(model, Node)

        adopt_children(model._ast, parent=model)
        self.assertIs(model.sub[0].parent, model)

    def test_find_ancestor(self):
        mod = codegenerator('mydsl', 'MyDSL', '''
        subsubnode::SubSubNode = v:"DSL" ;
        subnode::SubNode = sub:subsubnode ;
        dsl::RootNode = sub:subnode ;
        ''')

        parser = mod.MyDSLParser(semantics=ModelBuilderSemantics())
        model = parser.parse('DSL', rule_name='dsl')
        adopt_children(model._ast, parent=model)
        pnode = find_ancestor(model.sub.sub, 'RootNode')

        self.assertIs(pnode, model)


if __name__ == '__main__':
    main()
