# coding: utf-8

# Asynchronous Music Player Daemon client library for Python

# Copyright (C) 2015 Itaï BEN YAACOV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging

from . import _parser, errors


_logger = logging.getLogger(__name__.split('.')[0])


class DictNamespace(dict):
    def __getattr__(self, name):
        return self[name]


class Condition(object):
    def __repr__(self):
        return self.name.upper()

    def test(self, event):
        return [self] if self in event else []

    @staticmethod
    def setup(request):
        return False

    @staticmethod
    def cleanup():
        pass


class ConditionSubsystem(Condition):
    def __init__(self, name):
        self.name = name


class ConditionAny(Condition):
    name = 'any'

    @staticmethod
    def test(event):
        return list(filter(lambda c: c.name in subsystem_names, event))


class ConditionConnect(Condition):
    name = 'connect'

    @staticmethod
    def setup(request):
        return request.client.is_connected


class ConditionIdle(Condition):
    name = 'idle'

    @staticmethod
    def setup(request):
        return request.client.is_connected and request.client._is_idle and not request.client._execute_queue


class ConditionFactory(Condition):
    def __init__(self, class_):
        self.class_ = class_
        self.name = class_.name

    @staticmethod
    def setup(request):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.class_(self, *args, **kwargs)


class ConditionTimeout(Condition):
    name = 'timeout'

    def __init__(self, factory, timeout):
        self.factory = factory
        self.timeout = int(timeout)
        self.timeout_handler = None

    def __del__(self):
        if self.timeout_handler:
            _logger.error("Unclean timeout handler")

    def __repr__(self):
        return '{}({})'.format(self.name.upper(), self.timeout)

    def setup(self, request):
        self.request = request
        self.timeout_handler = self.request.client._scheduler.add_timeout(self.timeout, self.timeout_cb)
        return False

    def cleanup(self):
        if self.timeout_handler:
            self.request.client._scheduler.remove_timeout(self.timeout_handler)
        self.timeout_handler = self.request = None

    def timeout_cb(self):
        self.timeout_handler = None
        self.request._execute([self.factory])


class ConditionWorker(Condition):
    name = 'worker'

    def __init__(self, factory, worker):
        self.factory = factory
        try:
            self.wait = list(worker)
        except:
            self.wait = [worker]

    def __repr__(self):
        return '{}({})'.format(self.name.upper(), self.wait)

    def setup(self, request):
        self.n = 0
        for worker in self.wait:
            if worker._gen:
                self.n += 1
                worker.add_atexit(self.worker_exit_cb)
        if not self.n:
            return True
        self.request = request
        return False

    def cleanup(self):
        self.request = None
        for worker in self.wait:
            try:
                worker._atexit.remove(self.worker_exit_cb)
            except:
                pass

    def worker_exit_cb(self):
        self.n -= 1
        if not self.n:
            self.request._execute([self.factory] + [self.wait])


subsystem_names = [
    'database',
    'update',
    'stored_playlist',
    'playlist',
    'player',
    'mixer',
    'output',
    'options',
    'sticker',
    'subscription',
    'message',
]

subsystems = {name.upper(): ConditionSubsystem(name) for name in subsystem_names}
conditions = DictNamespace(subsystems)
for condition in (ConditionAny(), ConditionConnect(), ConditionIdle(), ConditionFactory(ConditionTimeout), ConditionFactory(ConditionWorker)):
    conditions[condition.name.upper()] = condition


class Request(object):
    def _setup(self, worker, client):
        self.worker = worker
        self.client = client

    def _execute(self, reply):
        _logger.debug("Got reply {} for request {} of {}".format(reply, self, self.worker))
        if self.worker._gen:
            self.client._execute(self.worker, reply)

    @staticmethod
    def new(request):
        if isinstance(request, Request):
            return request
        if isinstance(request, Condition):
            return RequestPassive(request)
        try:
            request = tuple(request)
        except:
            raise errors.CommandError(request)
        if all(isinstance(x, Condition) for x in request):
            return RequestPassive(*request)
        if all(isinstance(x, RequestCommand) for x in request):
            return RequestCommandList(request)
        return RequestList(*request)


class RequestActive(Request):
    def __init__(self):
        self.parser = self._parser_class()

    def __repr__(self):
        return self._commandline

    def _setup(self, worker, client):
        super(RequestActive, self)._setup(worker, client)
        if client.is_connected:
            _commandline = self._commandline + '\n'
            if client._coding:
                _commandline = _commandline.decode(client._coding)
            if client._is_idle:
                _commandline = 'noidle\n' + _commandline
                client._is_idle = False
            client._buff_out += _commandline.encode(client._coding_server)
            client._poller.start_writing()
            client._active_queue.append(self)
        else:
            self._execute(errors.ConnectionError())

    def _process_line(self, line):
        reply = self.parser.process_line(line)
        if reply is not None:
            del self.client._active_queue[0]
            self._execute(reply)


class RequestWelcome(RequestActive):
    _parser_class = _parser.ParserWelcome

    def __init__(self):
        super(RequestWelcome, self).__init__()

    def __repr__(self):
        return 'WELCOME'

    def _setup(self, worker, client):
        Request._setup(self, worker, client)
        client._active_queue.append(self)


class RequestCommand(RequestActive):
    def __init__(self, *args):
        self._commandline = self.name + ''.join(' "{}"'.format(str(arg).replace('"', '\\"')) for arg in args)
        super(RequestCommand, self).__init__()


class RequestCommandList(RequestActive):
    def __init__(self, commands):
        commands = tuple(commands)
        if not all(isinstance(command, RequestCommand) for command in commands):
            raise errors.CommandError
        self._commandline = '\n'.join(['command_list_ok_begin'] + [command._commandline for command in commands] + ['command_list_end'])
        self._parser_class = lambda: _parser.ParserCommandList(command.parser for command in commands)
        super(RequestCommandList, self).__init__()


class RequestCommandRaw(RequestActive):
    _parser_class = _parser.ParserRaw

    def __init__(self, _commandline):
        self._commandline = _commandline
        super(RequestCommandRaw, self).__init__()


class RequestCommandIdle(RequestActive):
    _commandline = 'idle'
    _parser_class = _parser.ParserList

    def _setup(self, worker, client):
        super(RequestCommandIdle, self)._setup(worker, client)
        client._is_idle = True

    def _execute(self, reply):
        self.client._is_idle = False
        super(RequestCommandIdle, self)._execute(reply)


class RequestPassive(Request):
    """
    Emulates MPD's 'idle' command, with some improvements.
    Returns as soon as one of the conditions is satisfied, with a list of the satisfied conditions:

        reply = yield idle(condition, ... | iterable)
        reply = yield condition, ... | iterable

    Conditions can be:

    - An MPD SUBSYSTEM name (in uppercase).
    - ANY - match any subsystem.
    - TIMEOUT(ms) - satisfied after 'ms' milliseconds.
    - CONNECT - client is connected to server.
    - IDLE - client is idle.
    - WORKER(worker, ... | iterable) - all workers are done.
    """
    def __init__(self, *conditions):
        self._conditions = conditions

    def __repr__(self):
        return 'IDLE({})'.format(', '.join(repr(condition) for condition in self._conditions))

    def _setup(self, worker, client):
        super(RequestPassive, self)._setup(worker, client)
        client._passive_list.append(self)
        reply = [condition for condition in self._conditions if condition.setup(self)]
        if reply:
            self._execute(reply)

    def _execute(self, reply):
        for condition in self._conditions:
            condition.cleanup()
        self.client._passive_list.remove(self)
        super(RequestPassive, self)._execute(reply)

    def _test(self, event):
        reply = sum(map(lambda c: c.test(event), self._conditions), [])
        if reply:
            self._execute(reply)
            return True
        else:
            return False


class RequestSelf(Request):
    """
    Returns the Worker object associated with the executing worker:

        reply = yield _self()
    """
    def _setup(self, worker, client):
        super(RequestSelf, self)._setup(worker, client)
        self._execute(worker)


class RequestList(Request):
    """
    Emulates MPD's command list, returns a list of replies.
    Waits for each request's reply before issuing the next,
    so can be slow.

        reply = yield request, ... | iterable
    """
    def __init__(self, *requests):
        self._requests = tuple(map(self.new, requests))
        self._replies = []

    def _setup(self, worker, client):
        super(RequestList, self)._setup(worker, client)
        self._worker_gen = self.worker._gen
        self.worker._gen = self._gen()
        self.client._execute(worker)

    def _execute(self, reply):
        self.worker._gen = self._worker_gen
        super(RequestList, self)._execute(reply)

    def _gen(self):
        for request in self._requests:
            try:
                reply = yield request
            except Exception as reply:
                self._execute(reply)
                return
            self._replies.append(reply)
        self._execute(self._replies)
        yield Request()

    def __repr__(self):
        return repr(self._requests)


command_parser = [
    ('add',                _parser.ParserOK),
    ('addid',              _parser.ParserItem),
    ('addtagid',           _parser.ParserRaw),
    ('channels',           _parser.ParserList),
    ('clear',              _parser.ParserOK),
    ('clearerror',         _parser.ParserOK),
    ('cleartagid',         _parser.ParserRaw),
    ('close',              lambda: None),
    ('commands',           _parser.ParserList),
    ('config',             _parser.ParserDict),
    ('consume',            _parser.ParserOK),
    ('count',              _parser.ParserDict),
    ('crossfade',          _parser.ParserOK),
    ('currentsong',        _parser.ParserDict),
    ('decoders',           _parser.ParserLists),
    ('delete',             _parser.ParserOK),
    ('deleteid',           _parser.ParserOK),
    ('disableoutput',      _parser.ParserOK),
    ('enableoutput',       _parser.ParserOK),
    ('find',               _parser.ParserFieldDict('file')),
    ('findadd',            _parser.ParserOK),
    ('kill',               lambda: None),
    ('list',               _parser.ParserList),
    ('listall',            _parser.ParserLists),
    ('listallinfo',        _parser.ParserDicts),
    ('listfiles',          _parser.ParserDicts),
    ('listmounts',         _parser.ParserFieldDict('mount')),
    ('listneighbors',      _parser.ParserFieldDict('neighbor')),
    ('listplaylist',       _parser.ParserList),
    ('listplaylistinfo',   _parser.ParserFieldDict('file')),
    ('listplaylists',      _parser.ParserFieldDict('playlist')),
    ('load',               _parser.ParserOK),
    ('lsinfo',             _parser.ParserDicts),
    ('mixrampdb',          _parser.ParserOK),
    ('mixrampdelay',       _parser.ParserOK),
    ('mount',              _parser.ParserRaw),
    ('move',               _parser.ParserOK),
    ('moveid',             _parser.ParserOK),
    ('next',               _parser.ParserOK),
    ('notcommands',        _parser.ParserList),
    ('outputs',            _parser.ParserFieldDict('outputid')),
    ('password',           _parser.ParserOK),
    ('pause',              _parser.ParserOK),
    ('ping',               _parser.ParserOK),
    ('play',               _parser.ParserOK),
    ('playid',             _parser.ParserOK),
    ('playlist',           _parser.ParserList),
    ('playlistadd',        _parser.ParserOK),
    ('playlistclear',      _parser.ParserOK),
    ('playlistdelete',     _parser.ParserOK),
    ('playlistfind',       _parser.ParserFieldDict('file')),
    ('playlistid',         _parser.ParserFieldDict('file')),
    ('playlistinfo',       _parser.ParserFieldDict('file')),
    ('playlistmove',       _parser.ParserOK),
    ('playlistsearch',     _parser.ParserFieldDict('file')),
    ('plchanges',          _parser.ParserFieldDict('file')),
    ('plchangesposid',     _parser.ParserFieldDict('cpos')),
    ('previous',           _parser.ParserOK),
    ('prio',               _parser.ParserOK),
    ('prioid',             _parser.ParserOK),
    ('random',             _parser.ParserOK),
    ('rangeid',            _parser.ParserOK),
    ('readcomments',       _parser.ParserDict),
    ('readmessages',       _parser.ParserFieldDict('channel')),
    ('rename',             _parser.ParserOK),
    ('repeat',             _parser.ParserOK),
    ('replay_gain_mode',   _parser.ParserOK),
    ('replay_gain_status', _parser.ParserItem),
    ('rescan',             _parser.ParserItem),
    ('rm',                 _parser.ParserOK),
    ('save',               _parser.ParserOK),
    ('search',             _parser.ParserFieldDict('file')),
    ('searchadd',          _parser.ParserOK),
    ('searchaddpl',        _parser.ParserOK),
    ('seek',               _parser.ParserOK),
    ('seekcur',            _parser.ParserOK),
    ('seekid',             _parser.ParserOK),
    ('sendmessage',        _parser.ParserOK),
    ('setvol',             _parser.ParserOK),
    ('shuffle',            _parser.ParserOK),
    ('single',             _parser.ParserOK),
    ('stats',              _parser.ParserDict),
    ('status',             _parser.ParserDict),
    ('sticker_get',        _parser.ParserStickerItem),
    ('sticker_set',        _parser.ParserOK),
    ('sticker_delete',     _parser.ParserOK),
    ('sticker_list',       _parser.ParserStickerList),
    ('sticker_find',       _parser.ParserStickerDict),
    ('stop',               _parser.ParserOK),
    ('subscribe',          _parser.ParserOK),
    ('swap',               _parser.ParserOK),
    ('swapid',             _parser.ParserOK),
    ('tagtypes',           _parser.ParserList),
    ('toggleoutput',       _parser.ParserOK),
    ('unmount',            _parser.ParserRaw),
    ('unsubscribe',        _parser.ParserOK),
    ('update',             _parser.ParserItem),
    ('urlhandlers',        _parser.ParserList),
    ('volume',             _parser.deprecate(_parser.ParserOK)),
]

commands_ = DictNamespace({command: type('RequestCommand' + command.capitalize(), (RequestCommand,), {'name': command, '_parser_class': staticmethod(parser_class)}) for command, parser_class in command_parser})
commands_['command_list'] = RequestCommandList
commands_['_self'] = RequestSelf
commands_['_raw'] = RequestCommandRaw
