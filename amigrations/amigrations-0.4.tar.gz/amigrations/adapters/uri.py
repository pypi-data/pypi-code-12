try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from .exceptions import URIError


class URI(object):

    username = None
    password = None
    host = None
    port = None
    database = None

    def __init__(self, uri_str):
        try:
            self.scheme, rest = uri_str.split(":", 1)
        except ValueError:
            raise URIError("URI has no scheme: %s" % repr(uri_str))

        self.options = {}

        if "?" in rest:
            rest, options = rest.split("?", 1)
            for pair in options.split("&"):
                key, value = pair.split("=", 1)
                self.options[unescape(key)] = unescape(value)
        if rest:
            if not rest.startswith("//"):
                self.database = unescape(rest)
            else:
                rest = rest[2:]
                if "/" in rest:
                    rest, database = rest.split("/", 1)
                    self.database = unescape(database)
                if "@" in rest:
                    userpass, hostport = rest.split("@", 1)
                else:
                    userpass = None
                    hostport = rest
                if hostport:
                    if ":" in hostport:
                        host, port = hostport.rsplit(":", 1)
                        self.host = unescape(host)
                        if port:
                            self.port = int(port)
                    else:
                        self.host = unescape(hostport)
                if userpass is not None:
                    if ":" in userpass:
                        username, password = userpass.rsplit(":", 1)
                        self.username = unescape(username)
                        self.password = unescape(password)
                    else:
                        self.username = unescape(userpass)

    def copy(self):
        uri = object.__new__(self.__class__)
        uri.__dict__.update(self.__dict__)
        uri.options = self.options.copy()
        return uri

    def __str__(self):
        tokens = [self.scheme, ":"]
        append = tokens.append
        if (self.username is not None or self.password is not None or
                self.host is not None or self.port is not None):
            append("//")
            if self.username is not None or self.password is not None:
                if self.username is not None:
                    append(escape(self.username))
                if self.password is not None:
                    append(":")
                    append(escape(self.password))
                append("@")
            if self.host is not None:
                append(escape(self.host))
            if self.port is not None:
                append(":")
                append(str(self.port))
            append("/")
        if self.database is not None:
            append(escape(self.database, "/"))
        if self.options:
            options = ["%s=%s" % (escape(key), escape(value))
                       for key, value in sorted(self.options.items())]
            append("?")
            append("&".join(options))
        return "".join(tokens)


def escape(s, safe=""):
    return quote(s, safe)


def unescape(s):
    if "%" not in s:
        return s
    i = 0
    j = s.find("%")
    r = []
    while j != -1:
        r.append(s[i:j])
        i = j + 3
        r.append(chr(int(s[j + 1:i], 16)))
        j = s.find("%", i)
    r.append(s[i:])
    return "".join(r)
