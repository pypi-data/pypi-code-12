import event
from dez import io
from dez.buffer import Buffer
from dez.logging import default_get_logger
from dez.http.server.router import Router
from dez.http.server.response import HTTPResponse
from dez.http.server.request import HTTPRequest

class HTTPDaemon(object):
    def __init__(self, host, port, get_logger=default_get_logger):
        self.log = get_logger("HTTPDaemon")
        self.get_logger = get_logger
        self.host = host
        self.port = port
        self.log.info("Listening on %s:%s" % (host, port))
        self.sock = io.server_socket(self.port)
        self.listen = event.read(self.sock, self.accept_connection, None, self.sock, None)
        self.router = Router(self.default_cb)

    def register_prefix(self, prefix, cb, args=[]):
        self.router.register_prefix(prefix, cb, args)

    def register_cb(self, signature, cb, args=[]):
        self.log.info("Registering callback: %s"%(signature,))
        self.router.register_cb(signature, cb, args)

    def respond(self, request, data=None, status="200 OK"):
        self.log.access("response (%s): '%s', '%s'"%(request.url, status, data))
        r = HTTPResponse(request)
        r.status = status
        if data:
            r.write(data)
        r.dispatch()

    def default_404_cb(self, request):
        self.log.access("404: %s"%(request.url,))
        self.respond(request, "The requested document %s was not found" % (request.url,), "404 Not Found")

    def default_200_cb(self, request):
        self.log.access("200: %s"%(request.url,))
        self.respond(request)

    def default_cb(self, request):
        return self.default_404_cb(request)

    def accept_connection(self, ev, sock, event_type, *arg):
        sock, addr = sock.accept()
        HTTPConnection(sock, addr, self.router, self.get_logger)
        return True

class HTTPConnection(object):
    id = 0
    def __init__(self, sock, addr, router, get_logger):
        HTTPConnection.id += 1
        self.id = HTTPConnection.id
        self.log = get_logger("HTTPConnection(%s)"%(self.id,))
        self.get_logger = get_logger
        self.sock = sock
        self.addr, self.local_port = addr
        self.router = router
        self.response_queue = []
        self.request = None
        self.current_cb = None
        self.current_args = None
        self.current_eb = None
        self.current_ebargs = None
        self.wevent = None
        self.revent = None
        self.__close_cb = None
        self.buffer = Buffer()
        self.write_buffer = Buffer()
        self.start_request()

    def set_close_cb(self, cb, args):
        self.__close_cb = (cb, args)

    def start_request(self):
        self.log.debug("start_request", self.buffer, self.request and self.request.state or "no request")
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
        if self.revent:
            self.revent.delete()
            self.revent = None
        self.revent = event.read(self.sock, self.read_ready)
        self.request = HTTPRequest(self)
        self.state = "read"
        if len(self.buffer):
            self.request.process()

    def close(self, reason=""):
        self.log.debug("close")
        if self.__close_cb:
            cb, args = self.__close_cb
            self.__close_cb = None
            cb(*args)
        if self.revent:
            self.revent.delete()
            self.revent = None
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
        self.sock.close()
        if self.current_eb:
            self.current_eb(*self.current_ebargs)
            self.current_eb = None
            self.current_ebargs = None
        while self.response_queue:
            tmp = self.response_queue.pop(0)
            data, self.current_cb, self.current_args, self.current_eb, self.current_ebargs = tmp
            if self.current_eb:
                self.current_eb(*self.current_ebargs)
            self.current_eb = None
            self.current_ebargs = None

    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
            if not data:
                self.close()
                return None
            return self.read(data)
        except io.socket.error, e:
            self.log.debug("read_ready", "io.socket.error", e)
            self.close()
            return None

    def read_body(self):
        self.log.debug("read_body")
        if self.revent:
            self.log.debug("revent exists?")
        self.revent = event.read(self.sock, self.read_ready)

    def route(self, request):
        self.log.debug("route", request.id)
        self.log.debug(" - deleting revent")
        self.revent.delete()
        self.revent = None
        self.log.debug(" - dispatching router")
        dispatch_cb, args = self.router(request.url)
        dispatch_cb(request, *args)

    def read(self, data):
        self.log.debug("read", self.state)
        if self.state != "read":
            self.log.error("Invalid additional data: %s" % data)
            self.close()
        self.buffer += data
        self.request.process()
        if self.request.state == "completed":
            self.log.debug("request completed (%s) -- deleting revent"%(self.request.id,))
            self.revent.delete()
            self.revent = None
            return None
        return self.request.state != "waiting"

    def write(self, data, cb, args, eb=None, ebargs=[]):
        self.log.debug("write", len(data))
        self.response_queue.append((data, cb, args, eb, ebargs))
        if not self.wevent:
            self.wevent = event.write(self.sock, self.write_ready)

    def write_ready(self):
        self.log.debug("write_ready")
        if self.write_buffer.empty():
            if self.current_cb:
                cb = self.current_cb
                args = self.current_args
                cb(*args)
                self.current_cb = None
            if not self.response_queue:
                self.current_cb = None
                self.wevent = None
                return None
            data, self.current_cb, self.current_args, self.current_eb, self.current_ebargs = self.response_queue.pop(0)
            self.write_buffer.reset(data)
            # call conn.write("", cb) to signify request complete
            if data == "":
                self.log.debug("ending request")
                self.wevent = None
                self.current_cb(*self.current_args)
                self.current_cb = None
                self.current_args = None
                self.current_eb = None
                self.current_ebargs = None
                return None
        try:
            self.log.debug("buffer", len(self.write_buffer.get_value()))
            self.log.debug("queue", len(self.response_queue))
            bsent = self.sock.send(self.write_buffer.get_value())
            self.write_buffer.move(bsent)
            return True
        except io.socket.error, msg:
            self.log.debug('io.socket.error: %s' % msg)
            self.close(reason=str(msg))
            return None