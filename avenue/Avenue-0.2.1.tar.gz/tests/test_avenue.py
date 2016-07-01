# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from avenue import Avenue
from avenue import MethodProcessor
from avenue import NotFound
from avenue import Skip
from pytest import raises


class TestAvenue(object):
    def test_basics(self):
        router = Avenue()

        @router.attach(path='/', method='GET')
        @router.attach(path='/welcome')
        def route_1():
            return 'Route 1'

        @router.attach(path='/', method='POST')
        def route_2():
            return 'Route 2'

        @router.attach(path='/post/<id|int>')
        def route_3(id):
            return 'Route 3 - for {:s}'.format(repr(id))

        @router.attach(path='/post/new')
        def route_4():
            return 'Route 4'

        @router.attach(path='/<page|greedy>')
        def route_5(page):
            return 'Route 5 - fallback - {:s}'.format(page)

        routing = [
            [{'path': '/', 'method': 'GET'},
             'Route 1'],
            [{'path': '/', 'method': 'POST'},
             'Route 2'],
            [{'path': '/post/12', 'method': 'GET'},
             'Route 3 - for 12'],
            [{'path': '/post/new-article-here', 'method': 'GET'},
             'Route 5 - fallback - post/new-article-here'],
            [{'path': '/post/new', 'method': 'GET'},
             'Route 4'],
            [{'path': '/any/other/page', 'method': 'GET'},
             'Route 5 - fallback - any/other/page'],
        ]

        for route, result in routing:
            assert router.solve(**route) == result

    def test_ordering(self):
        router = Avenue()

        @router.attach(path='/')
        def route_1():
            return 'Route 1'

        @router.attach(path='/', method='GET')
        def route_2():
            return 'Route 2'

        assert router.solve(path='/') == 'Route 1'
        assert router.solve(path='/', method='GET') == 'Route 2'

    def test_wrap(self):
        def wrap(func):
            def inner(**kwargs):
                return 'Wrapped: ' + func(**kwargs)

            return inner

        router = Avenue()

        @router.attach(path='/')
        def route():
            return 'Route 1'

        assert router.solve(path='/', wrap=wrap) == 'Wrapped: Route 1'

    def test_skipping(self):
        router = Avenue()
        toggle = 0

        @router.attach(path='/')
        def route_1():
            if toggle == 0:
                return 'Route 1'
            raise Skip()

        @router.attach(path='/')
        def route_2():
            return 'Route 2'

        assert router.solve(path='/') == 'Route 1'

        toggle = 1
        assert router.solve(path='/') == 'Route 2'

    def test_missing(self):
        router = Avenue()

        @router.attach(path='/', method='GET')
        @router.attach(path='/welcome')
        def route_1():
            return 'Route 1'

        with raises(NotFound):
            router.solve(path='/does/not/exist', method='GET')

        with raises(NotFound):
            router.solve()

        router = Avenue([MethodProcessor('method', optional=True)])

        @router.attach()
        def route_2():
            return 'Route 2'

        assert router.solve() == 'Route 2'
