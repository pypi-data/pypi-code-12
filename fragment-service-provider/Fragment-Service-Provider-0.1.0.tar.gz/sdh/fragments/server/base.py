"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at 

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

__author__ = 'Fernando Serena'

from flask import Flask, jsonify, request, make_response
from functools import wraps
from sdh.fragments.jobs.collect import collect_fragment
from sdh.fragments.jobs.query import execute_queries
from threading import Thread, Event
import traceback
import pytz
import logging

_triggers = []
_finishers = []
log = logging.getLogger('sdh.fragments.provider')

def get_accept():
    return str(request.accept_mimetypes).split(',')


class APIError(Exception):
    """
    Exception class to raise when an API request is not valid
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class NotFound(APIError):
    """
    404 response class
    """

    def __init__(self, message, payload=None):
        super(NotFound, self).__init__(message, 404, payload)


class Conflict(APIError):
    """
    409 response class
    """

    def __init__(self, message, payload=None):
        super(Conflict, self).__init__(message, 409, payload)


def _handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

class FragmentApp(Flask):
    """
    Provider base class for the Fragment-based services
    """

    def __init__(self, name, config_class):
        """
        :param name: App name
        :param config_class: String that represents the config class to be used
        :return:
        """
        super(FragmentApp, self).__init__(name)
        self.__handlers = {}
        self.__rdfizers = {}
        self.config.from_object(config_class)
        self._stop_event = Event()
        self.__refresh_rate = int(self.config.get('PARAMS', {}).get('rate', 3600))
        self.errorhandler(APIError)(_handle_invalid_usage)

    def batch_work(self):
        """
        Method to be executed in batch mode for collecting the required fragment (composite)
        and then other custom tasks.
        :return:
        """

        try:
            while True:
                gen = execute_queries(self._stop_event, **self.config['PROVIDER'])
                for listener, result in gen:
                    for task in _triggers:
                        task(listener, result, self._stop_event)
                gen = collect_fragment(self._stop_event, **self.config['PROVIDER'])
                for collector, (t, s, p, o) in gen:
                    for task in _triggers:
                        task(collector, (t, s, p, o), self._stop_event)
                for task in _finishers:
                    task(self._stop_event)
                self._stop_event.wait(self.__refresh_rate)
        except Exception, e:
            traceback.print_exc()
            log.error(e.message)

    def run(self, host=None, port=None, debug=None, **options):
        """
        Start the AgoraApp expecting the provided config to have at least REDIS and PORT fields.
        """

        tasks = options.get('triggers', [])
        for task in tasks:
            if task is not None and hasattr(task, '__call__'):
                _triggers.append(task)

        finishers = options.get('finishers', [])
        for task in finishers:
            if task is not None and hasattr(task, '__call__'):
                _finishers.append(task)

        thread = Thread(target=self.batch_work)
        thread.start()

        try:
            super(FragmentApp, self).run(host='0.0.0.0', port=self.config['PORT'], debug=False, use_reloader=False,
                                         threaded=True)
        except Exception, e:
            print e.message
        self._stop_event.set()
        if thread.isAlive():
            thread.join()

    def __execute(self, f):
        @wraps(f)
        def wrapper():
            mimes = get_accept()
            if 'application/json' in mimes:
                args, kwargs = self.__handlers[f.func_name](request)
                context, data = f(*args, **kwargs)
                response_dict = {'context': context, 'result': data}
                return jsonify(response_dict)
            else:
                graph = self.__rdfizers[f.func_name](f.func_name)
                if graph:
                    response = make_response(graph.serialize(format='turtle'))
                    response.headers['Content-Type'] = 'text-turtle'
                    return response
                raise APIError('Cannot return a graph')
        return wrapper

    def __register(self, handler, rdfizer):
        def decorator(f):
            self.__handlers[f.func_name] = handler
            self.__rdfizers[f.func_name] = rdfizer
            return f

        return decorator

    def register(self, path, handler, rdfizer):
        def decorator(f):
            for dec in [self.__execute, self.__register(handler, rdfizer), self.route(path)]:
                f = dec(f)
            return f

        return decorator
