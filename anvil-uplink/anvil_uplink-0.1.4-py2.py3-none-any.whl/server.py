from __future__ import unicode_literals
import threading, time, json, random, string, sys, traceback

from ws4py.client.threadedclient import WebSocketClient

import anvil

__author__ = 'Meredydd Luff <meredydd@anvil.works>'

_url = 'wss://anvil.works/uplink'

def _gen_id():
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))


class StreamingMedia(anvil.Media):
    def __init__(self, content_type):
        self._content_type = content_type
        self._content = b''
        self._complete = False

    def add_content(self, data, last_chunk=False):
        self._content += data
        self._complete = last_chunk

    def is_complete(self):
        return self._complete

    def get_content_type(self):
        return self._content_type

    def get_content(self):
        return self._content

    def get_url(self):
        raise Exception('Not yet implemented: Cannot get URLs from Media objects on the server')

class LiveObjectProxy(anvil.LiveObject):

    def __getattr__(self, item):
        if item in self._spec["methods"]:
            def item_fn(*args, **kwargs):
                lo_call = dict(self._spec)
                lo_call["method"] = item
                return _do_call(args, kwargs, lo_call=lo_call)

            return item_fn
        else:
            raise AttributeError

    def __getitem__(self, item):
        getitem = self.__getattr__("__getitem__")
        return getitem(item)

    def __setitem__(self, key, value):
        setitem = self.__getattr__("__setitem__")
        return setitem(key, value)


def mk_live_object(spec):
    return _backends.get(spec["backend"], LiveObjectProxy)(spec)



class _IncomingReqResp:
    def __init__(self, json):
        self.json = json
        self.media = {}
        if 'media' in self.json:
            for m in self.json["media"]:
                sm = StreamingMedia(m['mime-type'])
                self.media[m['id']] = sm

                target = self.json
                target_key = None

                for k in m['path']:
                    if target_key is not None:
                        target = target[target_key]
                    target_key = k

                target[target_key] = sm

        if 'liveObjects' in self.json:
            for o in self.json["liveObjects"]:
                lo = mk_live_object(o['live-object'])

                target = self.json
                target_key = None

                for k in o['path']:
                    if target_key is not None:
                        target = target[target_key]
                    target_key = k

                target[target_key] = lo


        _incoming_requests[self.json["id"]] = self
        self.maybe_execute()

    def add_binary_data(self, json, data):
        self.media[json['mediaId']].add_content(data, json['lastChunk'])
        if json['lastChunk']:
            self.maybe_execute()

    def is_ready(self):
        for id in self.media:
            if not self.media[id].is_complete():
                return False
        return True

    def maybe_execute(self):
        if not self.is_ready():
            return

        del _incoming_requests[self.json["id"]]

        self.execute()


class AnvilWrappedError(Exception):
    def __init__(self, value):
        self.extra_data = value
        self.value = ""
        self.wrapped_python_stack = False
        if "message" in value:
            self.value = value["message"]
        if "type" in value and value["type"] == "exception":
            self.value = value["data"]["msg"]
            self.wrapped_python_stack = True

    def __str__(self):
        return repr(self.value)


def _report_exception(id):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)

    msg = str(exc_type.__name__) + ": " + str(exc_value)
    trace = [(filename.replace("\\","/"), lineno) for (filename, lineno, _, _) in tb]
    trace.reverse()
    p = trace.pop() # Remove the bottom stack frame from the traceback

    if isinstance(exc_value, AnvilWrappedError) and exc_value.wrapped_python_stack:
        msg = exc_value.extra_data["data"]["msg"]
        trace = exc_value.extra_data["data"]["trace"] + trace

    return {
        "error": {
            "type": "exception",
            "data": {
                "msg": msg,
                "trace": trace
            },
            "message": "Python error"
        },
        "id": id
    }


class _IncomingRequest(_IncomingReqResp):
    def execute(self):

        def make_call():
            _call_info.stack_id = self.json.get('call-stack-id', None)
            try:
                if 'liveObjectCall' in self.json:
                    loc = self.json['liveObjectCall']
                    spec = dict(loc)

                    if self.json["id"].startswith("server-"):
                        spec["source"] = "server"
                    elif self.json["id"].startswith("client-"):
                        spec["source"] = "client"
                    else:
                        spec["source"] = "UNKNOWN"

                    del spec["method"]
                    backend = loc['backend']
                    inst = _backends[backend](spec)
                    method = inst.__getattribute__(loc['method'])
                    r = method(*self.json['args'], **self.json['kwargs'])
                else:
                    r = _registrations[self.json['command']](*self.json["args"], **self.json["kwargs"])

                _get_connection().send_reqresp({"id": self.json["id"], "response": r})
            except:
                _get_connection().send_reqresp(_report_exception(self.json["id"]))

        threading.Thread(target=make_call).start()


class _IncomingResponse(_IncomingReqResp):
    def execute(self):
        id = self.json['id']
        if id in _call_responses:
            _call_responses[id] = self.json
            with _waiting_for_calls:
                _waiting_for_calls.notifyAll()
        else:
            print("Got a response for an unknown ID: " + repr(self.json))

# requestId->_IncomingRequest
_incoming_requests = {}


class LocalCallInfo(threading.local):
    def __init__(self):
        self.stack_id = None


_call_info = LocalCallInfo()

_connection = None
_connection_lock = threading.Lock()

_registrations = {}
_backends = {}


def reconnect(closed_connection):
    global _connection
    with _connection_lock:
        if _connection != closed_connection:
            return
        _connection = None

    def retry():
        time.sleep(1)
        print("Reconnecting...")
        _get_connection()

    try:
        for k in _call_responses.keys():
            if _call_responses[k] is None:
                _call_responses[k] = {'error': 'Connection to server lost'}

        with _waiting_for_calls:
            _waiting_for_calls.notifyAll()

    finally:
        threading.Thread(target=retry).start()


class _Connection(WebSocketClient):
    def __init__(self):
        print("Connecting to " + _url)
        WebSocketClient.__init__(self, _url)

        self._ready_notify = threading.Condition()
        self._ready = False
        self._next_chunk_header = None
        self._sending_lock = threading.RLock()

    def is_ready(self):
        return self._ready

    def wait_until_ready(self):
        with self._ready_notify:
            while not self._ready:
                self._ready_notify.wait()

    def _signal_ready(self):
        self._ready = True
        with self._ready_notify:
            self._ready_notify.notifyAll()

    def opened(self):
        print("Anvil websocket open")
        self.send(json.dumps({'key': _key}))
        for r in _registrations.keys():
            self.send(json.dumps({'type': 'REGISTER', 'name': r}))
        for b in _backends.keys():
            self.send(json.dumps({'type': 'REGISTER_LIVE_OBJECT_BACKEND', 'backend': b}))

    def closed(self, code, reason=None):
        print("Anvil websocket closed (code %s, reason=%s)" % (code, reason))
        self._signal_ready()
        reconnect(self)

    def received_message(self, message):

        if message.is_binary:
            hdr = self._next_chunk_header
            _incoming_requests[hdr['requestId']].add_binary_data(hdr, message.data)
            self._next_chunk_header = None

        else:
            data = json.loads(message.data.decode())

            type = data["type"] if 'type' in data else None

            if 'auth' in data:
                print("Authenticated OK")
                self._signal_ready()
            elif 'output' in data:
                print("Anvil server: " + data['output'].rstrip("\n"))
            elif type == "CALL":
                _IncomingRequest(data)
            elif type == "CHUNK_HEADER":
                self._next_chunk_header = data
            elif type is None:
                _IncomingResponse(data)
            else:
                print("Anvil websocket got unrecognised message: "+repr(data))

    def send(self, payload, binary=False):
        with self._sending_lock:
            return WebSocketClient.send(self, payload, binary)

    def send_reqresp(self, reqresp):
        if not self._ready:
            raise RuntimeError("Websocket connection not ready to send request")

        media = []
        live_objects = []

        def deconstruct(json, path):
            if isinstance(json, dict):
                for i in json:
                    path.append(i)
                    json[i] = deconstruct(json[i], path)
                    path.pop()
            elif isinstance(json, list) or isinstance(json, tuple):
                json = list(json)
                for i in range(len(json)):
                    path.append(i)
                    json[i] = deconstruct(json[i], path)
                    path.pop()
            elif isinstance(json, anvil.Media):
                id = _gen_id()
                media.append((id, list(path), json))
                json = None
            elif isinstance(json, anvil.LiveObject):
                live_objects.append((list(path), json))
                json = None

            return json

        reqresp = deconstruct(reqresp, [])

        reqresp['media'] = list({'path': p, 'id': i, 'mime-type': m.get_content_type()} for (i,p,m) in media)
        reqresp['liveObjects'] = list({'path': p, 'live-object': o._spec} for (p,o) in live_objects)

        self.send(json.dumps(reqresp))

        for (id,_,m) in media:
            data = m.get_content()
            l = len(data)
            i = 0
            n = 0
            while i < l:
                chunk_len = min(l - i, 10000)
                with self._sending_lock:
                    self.send(json.dumps({'type': 'CHUNK_HEADER', 'requestId': reqresp['id'], 'mediaId': id,
                                          'chunkIndex': n, 'lastChunk': (i + chunk_len == l)}))
                    self.send(data[i:(i+chunk_len)], True)
                i += chunk_len
                n += 1


_key = None


def _get_connection():
    global _connection

    if _key is None:
        raise Exception("You must use anvil.server.connect(key) before anvil.server.call()")

    with _connection_lock:
        if _connection is None:
            _connection = _Connection()
            _connection.connect()
            _connection.wait_until_ready()
    return _connection


def connect(key, url='wss://anvil.works/uplink'):
    global _key, _url
    _key = key
    _url = url
    _get_connection()


def run_forever():
    while True:
        time.sleep(1)


# can be used as a decorator too
def register(fn, name=None):
    if isinstance(fn, str):
        # Someone's using the old syntax. Our bad.
        (fn, name) = (name, fn)

    if name is None:
        name = fn.__name__

    _registrations[name] = fn

    if _connection is not None and _connection.is_ready():
        _connection.send_reqresp({'type': 'REGISTER', 'name': name})

    return fn

callable = register


def register_live_object_backend(cls):

    name = "uplink." + cls.__name__
    _backends[name] = cls

    if _connection is not None and _connection.is_ready():
        _connection.send_reqresp({'type': 'REGISTER_LIVE_OBJECT_BACKEND', 'backend': name})

    return cls

live_object_backend = register_live_object_backend


# A parameterised decorator
def callable_as(name):
    return lambda f: register(f, name)


_call_responses = {}
_waiting_for_calls = threading.Condition()

def _do_call(args, kwargs, fn_name=None, lo_call=None): # Yes, I do mean args and kwargs without *s
    c = _get_connection()

    id = _gen_id()

    _call_responses[id] = None

    with _waiting_for_calls:
        #print("Call stack ID = " + repr(_call_info.stack_id))
        req = {'type': 'CALL', 'id': id, 'args': args, 'kwargs': kwargs,
               'call-stack-id': _call_info.stack_id}

        if fn_name:
            req["command"] = fn_name
        elif lo_call:
            req["liveObjectCall"] = lo_call
        else:
            raise Exception("Expected one of fn_name or lo_call")

        c.send_reqresp(req)

        while _call_responses[id] == None:
            _waiting_for_calls.wait()

    r = _call_responses.pop(id)

    if 'response' in r:
        return r['response']
    if 'error' in r:
        raise AnvilWrappedError(r["error"])
    else:
        raise Exception("Bogus response from server: " + repr(r))



def call(fn_name, *args, **kwargs):
    return _do_call(args, kwargs, fn_name=fn_name)

def wait_forever():
    _get_connection()
    while True:
        time.sleep(30)
        try:
            call("anvil.private.echo", "keep-alive")
        except:
            # Give ourselves a chance to reconnect
            time.sleep(10)
            call("anvil.private.echo", "keep-alive")
