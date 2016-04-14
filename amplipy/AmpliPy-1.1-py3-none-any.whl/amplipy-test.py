from . import *
import astor
import ast


def test_RewriteShorthandLambda():
    tests_and_results = [("{x | x + 2}", "(lambda x: \n(x + 2))"),
                         ("{_ | foo()}", "(lambda : \nfoo())"),
                         ("{(x, y) | x + y}", "(lambda x, y: \n(x + y))"),
                         ("{2 | 4, 2}", "{(2 | 4), 2}")]
    for test, result in tests_and_results:
        assert(astor.to_source(amplipy.RewriteShorthandLambda()
                               .visit(ast.parse(test))) == result)


def test_RewriteMultiassign():
    tests_and_results = [("a = ...", "a = ..."),
                         ("a, b = [], ...", "(a, b) = ([], [])"),
                         ("a, b, c = [], ...", "(a, b, c) = ([], [], [])")]
    for test, result in tests_and_results:
        assert(astor.to_source(amplipy.RewriteMultiassign()
                               .visit(ast.parse(test))) == result)
