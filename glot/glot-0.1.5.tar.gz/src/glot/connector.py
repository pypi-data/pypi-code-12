# This file is part of the Go-Smart Simulation Architecture (GSSA).
# Go-Smart is an EU-FP7 project, funded by the European Commission.
#
# Copyright (C) 2013-  NUMA Engineering Ltd. (see AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.asyncio.wamp import ApplicationRunner
import asyncio
import logging
import traceback
from functools import partial

logger = logging.getLogger(__name__)


def execute(action, actor, server, router, port, debug=False, **kwargs):
    responses = []
    if debug:
        logger.info("DEBUG ON")
        logging.getLogger('autobahn').setLevel(logging.DEBUG)

    runner = ApplicationRunner(url="ws://%s:%d/ws" % (router, port), realm="realm1")
    logger.debug("Starting connection")
    runner.run(partial(GlotConnector, responses=responses, action=action, actor=actor, debug=debug, server=server, **kwargs))
    return responses.pop() if responses else None


# This should be adjusted when this issue resolution hits PIP: https://github.com/tavendo/AutobahnPython/issues/332
# http://stackoverflow.com/questions/28293198/calling-a-remote-procedure-from-a-subscriber-and-resolving-the-asyncio-promise
def wrapped_coroutine(f):
    def wrapper(*args, **kwargs):
        coro = f(*args, **kwargs)
        asyncio.async(coro)
    return wrapper
# endSO


# This is the application object for the shell GSSA client
class GlotConnector(ApplicationSession):

    # Accept arguments from the command line
    def __init__(self, x, responses, action, actor, debug, server=None, **kwargs):
        ApplicationSession.__init__(self, x)
        self._kwargs = kwargs
        self._action = action
        self._server = server
        self._responses = responses

        self._actor = actor
        self._actor.set_make_call(self.execute_call)
        self._actor.set_log(self.log)

        self._apis = {}

        if debug:
            # Seemingly the start_logging call is insufficient
            self.log._set_level('trace')
        if server or debug:
            logger.info("Targeting server [%s]" % (server))

    def make_call(self, suffix):
        # If we have a specific server, address it, otherwise we call whichever
        # one got the full namespace
        if self._server:
            return "com.gosmartsimulation.%s.%s" % (self._server, suffix)
        else:
            return "com.gosmartsimulation.%s" % suffix

    @wrapped_coroutine
    @asyncio.coroutine
    def onJoin(self, details):
        logger.debug("Session ready - executing action")

        try:
            self.result = yield from self._action(self._actor, **self._kwargs)
        except Exception as e:
            logging.exception("Problem executing action")
            traceback.print_exc()
            raise e
        finally:
            self.leave()

        logger.debug("Executed")

    @asyncio.coroutine
    def execute_call(self, suffix, *args, minapi='A0.0'):
        if minapi:
            if suffix in self._apis:
                api = self._apis[suffix]
            else:
                try:
                    api = yield from self.call(self.make_call('api'))
                    api = str(api)
                except:
                    api = 'A0.0'
                self._apis[suffix] = api

            isapi, api = api[0], api[1:]

            if isapi != 'A':
                raise RuntimeError('Remote API unknown - %s%s' % (isapi, api))

            api = float(api)
            minapi = float(minapi[1:])
            if api < minapi:
                raise NotImplementedError('The API version of the remote server is too low for this operation (%.1lf < %.1lf)' % (api, minapi))

        try:
            result = yield from self.call(self.make_call(suffix), *args)
            self._responses.append(result)
        except:
            logger.exception("Could not complete call")

        return result

    def onDisconnect(self):
        asyncio.get_event_loop().stop()
