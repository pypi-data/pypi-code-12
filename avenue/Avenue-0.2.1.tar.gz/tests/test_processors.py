# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from avenue import Avenue
from avenue import MatchError
from avenue import MethodProcessor
from avenue import PathProcessor
from avenue import Processor
from avenue.processors import Match
from pytest import raises


class TestProcessors(object):
    def test_match(self):
        match = Match()
        match.update(2)
        match.update(1)

        assert repr(match) == '<Match (score=[2, 1])>'

    def test_path_processor(self):
        avenue = Avenue([
            PathProcessor('path_1'),
            PathProcessor('path_2', optional=True),
        ])

        @avenue.attach(path_1='/welcome', path_2='/nl')
        def nl_welcome():
            return 'Welkom.'

        @avenue.attach(path_1='/welcome', path_2='/de-DE')
        def de_welcome():
            return 'Willkommen.'

        @avenue.attach(path_1='/welcome')
        def welcome():
            return 'Welcome.'

        assert avenue.solve(path_1='/welcome',
                            path_2='/de-DE') == 'Willkommen.'

        assert avenue.solve(path_1='/welcome') == 'Welcome.'

    def test_exceptions(self):
        avenue = Avenue()

        @avenue.attach()
        def will_never_run():
            pass

        with raises(RuntimeError):
            avenue.solve()

    def test_custom_processor(self):
        class RoleProcessor(Processor):
            def __call__(self, value, route):
                # prepare takes care of the `optional` part automaticly
                argument, value = self.prepare(value, route)

                # argument is the parameter with which the route was defined
                # value is the parameter which `solve` was called with

                print(value, 'in', argument)
                if not argument:
                    # processor is optional
                    return 0
                elif value in argument:
                    # value is one of the allowed roles
                    return -1
                else:
                    # you could also raise some other error and return
                    # a 403 to your users, this simply marks the route
                    # as not runnable if the role does not match
                    error = 'Role does not match, `{:s}` not in `{:s}`'.format(
                        value, ', '.join(argument))
                    raise MatchError(error)

        # create a router with the RoleProcessor
        router = Avenue([
            PathProcessor('path'),
            MethodProcessor('method', optional=True),
            RoleProcessor('role', optional=True),
        ])

        # define a route without a role
        @router.attach(path='/', method='GET')
        def hello_world():
            return 'Hallo world!'

        # define a route and use the role parameter
        @router.attach(path='/', method='GET', role=['user', 'administrator'])
        def hello_world_for_authenticated_people():
            return 'Hallo world, for users and administrators!'

        # define a route that matches the path, but accepts other roles
        @router.attach(path='/', method='GET', role=['spy'])
        def hello_world_for_spies():
            return 'Hallo world, nothing to see here!'

        # solve without a role
        route = {'path': '/', 'method': 'GET'}
        assert router.solve(**route) == 'Hallo world!'

        # solve with a role
        route = {'path': '/', 'method': 'GET', 'role': 'user'}
        assert router.solve(
            **route) == 'Hallo world, for users and administrators!'

        # solve with the spy role
        route = {'path': '/', 'method': 'GET', 'role': 'spy'}
        assert router.solve(
            **route) == 'Hallo world, nothing to see here!', router.solve(
            **route)
