from pylib.misc import search
from pylib.misc.search import Engine

import re

name = re.compile(r'^[a-zA-z]+$')


def setup():
    return Engine()


def simple_search(qeury):
    return [qeury, qeury]


def real_search(*args, **kwargs):
    return ['Arewa']


def test_engine():
    engine = setup()
    assert len(engine) == 0


def test_search_with():
    engine = setup()
    f = search.search_with(engine, lambda x: bool(name.match(x)))(simple_search)
    assert f == simple_search
    assert len(engine) == 1


def test_search():
    engine = setup()
    search.search_with(engine, lambda x: bool(name.search(x)))(simple_search)
    assert len(search.search(engine, 'Arewa')) == 2
    assert len(search.search(engine, '122-AR')) == 0


def test_regex_criteria():
    test = search.regex_criteria(r'^[a-zA-z]+$')
    assert test('Arewa')
    assert not test('122-AR')


def test_query_format():
    engine = setup()
    search.search_with(engine, search.regex_criteria(r'^[a-zA-z]+$'))(simple_search)
    assert len(search.search(engine, 'Arewa   ')) == 2
    assert len(search.search(engine, '   Arewa')) == 2
    assert len(search.search(engine, '  Arewa  ')) == 2
    assert len(search.search(engine, 'Arewa')) == 2
    assert len(search.search(engine, '')) == 0
    len(search.search(engine, None)) == 0


def test_empty_query():
    engine = setup()
    engine2 = setup()
    search.search_all(engine)(real_search)
    assert len(search.search(engine, None)) == 1
    assert len(search.search(engine2, None)) == 0
