
import copy
import urllib.parse

import regex

import wayround_org.utils.types

URL_AUTHORITY_RE = r'^((?P<userinfo>.*)\@)?(?P<host>.*)(\:(?P<port>\d+))?$'
URL_AUTHORITY_RE_C = regex.compile(URL_AUTHORITY_RE)

URI_RE = (
    r'^('
    r'(?P<scheme>\p{L}\w*\:)'
    r'(?P<path>.*?)'
    r'(\?(?P<query>.*))?'
    r'(?P<fragment>\#.*)?'
    r')$'
    )

URI_RE_C = regex.compile(URI_RE)


class UserInfoLikeHttp:

    def __init__(self, value):

        if isinstance(value, AuthorityLikeHttp):
            value = value.userinfo

        if not isinstance(value, str):
            raise TypeError("`value' must be str")

        self.name = value
        self.password = None

        if ':' in self.name:
            self.name, self.password = self.name.split(':', 1)

        return

    def __str__(self):

        ret = self.name
        if self.password is not None:
            ret = '{}:{}'.format(ret, self.password)

        return ret


class AuthorityLikeHttp:

    @classmethod
    def new_from_string(cls, value):

        res = URL_AUTHORITY_RE_C.match(value)

        if res is None:
            raise ValueError("can't parse value as authority")

        userinfo = res.group('userinfo')
        host = res.group('host')
        port = res.group('port')

        return cls(userinfo, host, port)

    def __init__(self, userinfo, host, port):

        self._userinfo = None
        self._host = None
        self._port = None

        self.userinfo = userinfo
        self.host = host
        self.port = port
        return

    def render_str(self):

        ret = '//'

        if self.userinfo is not None:
            ret += '{}@'.format(self.userinfo)

        ret += self.host

        if self.port is not None:
            ret += ':{}'.format(self.port)

        return ret

    # don't do this. code should be more strict
    # render_string = render_str

    def __str__(self):
        return self.render_str()

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        if not isinstance(value, str):
            raise TypeError("`host' must be str")
        self._host = value.lower()
        return

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if isinstance(value, str):
            value = int(value)

        if value is not None and not isinstance(value, int):
            raise TypeError("`port' must be int")

        self._port = value
        return

    @property
    def userinfo(self):
        return self._userinfo

    @userinfo.setter
    def userinfo(self, value):

        if isinstance(value, str):
            value = UserInfoLikeHttp(value)

        if value is not None and not isinstance(value, UserInfoLikeHttp):
            raise TypeError("`userinfo' must be None or UserInfoLikeHttp")

        self._userinfo = value
        return


class QueryLikeHttp:

    def __init__(self, value, encoding=None, errors=None):
        self._value = None
        self.value = value

        if encoding is None:
            encoding = 'utf-8'

        self._encoding = encoding
        self._errors = errors
        return

    def render_str(self):

        if encoding is None:
            encoding = 'utf-8'

        ret = []

        for i in self.value:
            ret.append(
                '{}={}'.format(
                    urllib.parse.quote(
                        i[0],
                        encoding=self._encoding,
                        errors=self._errors
                        ),
                    urllib.parse.quote(
                        i[1],
                        encoding=self._encoding,
                        errors=self._errors
                        )
                    )
                )

        ret = '&'.join(ret)

        return ret

    def __str__(self):
        return self.render_str()

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):

        if isinstance(value, URI):
            value = value.query

        if isinstance(value, str):
            res_val = []
            for i in value.split('&'):
                k, v = i.split('=', 1)

                k = urllib.parse.unquote(
                    k,
                    encoding=self._encoding,
                    errors=self._errors
                    ),
                v = urllib.parse.unquote(
                    v,
                    encoding=self._encoding,
                    errors=self._errors
                    )

                res_val.append(tuple())

            value = res_val
            del res_val

        if not wayround_org.utils.types.struct_check(
                value,
                {'t': list,
                 'None': True,
                 '.': {
                     't': tuple,
                     '<': 2,
                     '>': 2,
                     '.': {
                         't': str
                         }
                     }
                 }
                ):
            raise TypeError("`query' must be list of 2-str-tuples")

        self._value = value
        return

    def keys(self):
        ret = []
        for i in self.value:
            ret.append(i[0])
        return ret

    def values(self):
        ret = []
        for i in self.value:
            ret.append(i[1])
        return ret

    def get(self, key, default=None):
        ret = default
        for i in self.value:
            if i[0] == key:
                ret = i[1]
        return ret

    def get_all(self, key):
        ret = []
        for i in self.value:
            if i[0] == key:
                ret.append(i[1])
        return ret

    def set(self, key, value):
        val = self.value
        for i in range(len(val) - 1, -1, -1):
            if val[i][0] == key:
                val[i] = tuple(key, value)
        return

    def remove(self, key):
        val = self.value
        for i in range(len(val) - 1, -1, -1):
            if val[i][0] == key:
                del val[i]
        return


def parse_uri(value):
    return URI_RE_C.match(value)


def isuri(value):
    return parse_uri(value) is not None


class URI:

    @classmethod
    def new_from_string(cls, value):

        res = parse_uri(value)

        if res is None:
            raise ValueError("can't parse value as URI string")

        scheme = res.group('scheme')
        authority = None
        # authority = res.group('authority')
        path = res.group('path')
        query = res.group('query')
        fragment = res.group('fragment')

        if path.startswith('//'):
            authority = None
            path_splitted = path[2:].split('/')
            authority = path_splitted[0]
            path = '/'.join(path_splitted[1:])

        return cls(scheme, authority, path, query, fragment)

    def __init__(self, scheme, authority, path, query, fragment):

        self._scheme = None
        self._authority = None
        self._path = None
        self._query = None
        self._fragment = None

        self.scheme = scheme
        self.authority = authority
        self.path = path
        self.query = query
        self.fragment = fragment

        return

    def render_str(self):
        ret = ''
        ret += str(self.scheme)
        ret += ':'
        if self.authority is not None:
            ret += str(self.authority)
        if self.path is not None:
            if len(self.path) == 0:
                ret += '/'
            else:
                ret += '/{}'.format('/'.join(self.path))
        if self.fragment is not None:
            ret += '#'
            ret += str(self.fragment)
        return ret

    def __str__(self):
        return self.render_str()

    def __repr__(self):
        ret = '{} {}'.format(
            repr(super()),
            ("scheme: `{}', authority: `{}', "
             "path: `{}', query: `{}', fragment: `{}'").format(
                self.scheme,
                self.authority,
                self.path,
                self.query,
                self.fragment
                )
            )
        return ret

    def __copy__(self):
        ret = URI(
            copy.copy(self.scheme),
            copy.copy(self.authority),
            copy.copy(self.path),
            copy.copy(self.query),
            copy.copy(self.fragment)
            )
        return ret

    def copy(self):
        return copy.copy(self)

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        if not isinstance(value, str):
            raise ValueError("`scheme' must be str")
        self._scheme = value.rstrip(':')
        # NOTE: scheme is case sensitive
        # self._scheme = self._scheme.lower()
        return

    @property
    def authority(self):
        return self._authority

    def gen_authority_like_http(self):
        return AuthorityLikeHttp(self.authority)

    @authority.setter
    def authority(self, value):
        if value is not None:
            a_t = type(value)

            if a_t == str:
                value = AuthorityLikeHttp.new_from_string(value)

            elif a_t == AuthorityLikeHttp:
                pass

            else:
                raise TypeError("invalid `authority' type")

        self._authority = value

        return

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):

        if value is None:
            value = []

        if isinstance(value, str):

            if self.scheme.lower() == 'urn':
                value = value.split(':')
            else:
                value = value.split('/')

        if not wayround_org.utils.types.struct_check(
                value,
                {'t': list,
                 'None': True,
                 '.': {
                     't': str
                     }
                 }
                ):
            raise TypeError("`path' must be list of strings")

        self._path = value

        return

    @property
    def query(self):
        return self._query

    def gen_query_like_http(self):
        return QueryLikeHttp(self.query)

    @query.setter
    def query(self, value):

        if not value is None and not isinstance(value, str):
            raise TypeError("`query' must be None or str")

        self._query = value

        return

    @property
    def fragment(self):
        return self._fragment

    @fragment.setter
    def fragment(self, value):

        if value is not None and not isinstance(value, str):
            raise ValueError("`fragment' must be str")

        self._fragment = value

        return


class HttpURI(URI):
    """
    This class is specially done for HTTP URIs handling, as it is very
    common case.

    .query and .authority are stored as objects, not as strings
    """

    def __copy__(self):
        ret = HttpURI(
            copy.copy(self.scheme),
            copy.copy(self.authority),
            copy.copy(self.path),
            copy.copy(self.query),
            copy.copy(self.fragment)
            )
        return ret

    def gen_authority_like_http(self):
        raise Exception("not in HttpURI")

    def gen_query_like_http(self):
        raise Exception("not in HttpURI")

    @property
    def authority(self):
        return super().authority

    @authority.setter
    def authority(self, value):

        if isinstance(value, str):
            value = AuthorityLikeHttp.new_from_string(value)

        if value is not None and not isinstance(value, AuthorityLikeHttp):
            raise ValueError(
                "`query' must be None or AuthorityLikeHttp inst"
                )

        self._authority = value

        return

    @property
    def query(self):
        return super().query

    @query.setter
    def query(self, value):

        if isinstance(value, str):
            value = QueryLikeHttp(value)

        if value is not None and not isinstance(value, QueryLikeHttp):
            raise ValueError("`query' must be None or QueryLikeHttp inst")

        self._query = value

        return

    def is_email(self):

        has_scheme = isinstance(self.scheme, str)

        has_user_info = False
        has_password = False
        has_domain = False
        has_port = False

        if self.authority is not None:
            a = self.authority
            has_domain = isinstance(a.host, str)
            has_port = isinstance(a.port, int)
            if a.userinfo is not None:
                a = a.userinfo
                has_user_info = True
                has_password = a.password is not None

        has_query = self.query is not None
        has_fragment = self.fragment is not None

        ret = (
            not has_scheme
            and has_user_info
            and not has_password
            and has_domain
            and not has_port
            and not has_query
            and not has_fragment
            )
        return ret


def run_examples():

    examples = [
        'ftp://ftp.is.co.za/rfc/rfc1808.txt',
        'http://www.ietf.org/rfc/rfc2396.txt',
        'ldap://[2001:db8::7]/c=GB?objectClass?one',
        'mailto:John.Doe@example.com',
        'news:comp.infosystems.www.servers.unix',
        'tel:+1-816-555-1212',
        'telnet://192.0.2.16:80/',
        'urn:oasis:names:specification:docbook:dtd:xml:4.1.2'
        ]

    for i in examples:
        print("{}\n\t{}\n".format(i, repr(URI.new_from_string(i))))
