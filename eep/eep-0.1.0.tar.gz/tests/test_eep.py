"""
test_eep
----------------------------------
Tests for `eep` module.
"""

import eep


def test_string_output():
    assert "str" == eep.Searcher("str").text


def test_insert():
    es = eep.Searcher("test string")
    es.insert("four")
    assert es.point == 4


def test_replace():
    es = eep.Searcher("test string with extra words")
    es.replace("first words ")
    assert es.point == 12


def test_forward_search():
    es = eep.Searcher("test string with test word and another test word")
    es.search_forward("test")
    es.search_forward("test")

    assert (es.point == 21) and (es.mark == 17)


def test_backward_search():
    es = eep.Searcher("test string with test word and another test word")
    es.goto("end")
    es.search_backward("test")
    es.search_backward("test")

    assert (es.point == 17) and (es.mark == 21)
