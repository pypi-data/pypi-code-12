
raise Exception("this module requires rework")
# TODO: this module requires deprications and deletions

import copy
import urllib
import re


def paths_by_path(path, last_el_type=None, path_is_absolute=None):
    '''
    Returns dict with three values:

       - path_str: path string
       - path_lst: list of path components
       - last_el_type: last element type: 'dir' or 'file'
       - path_is_absolute: True if path_str begins with '/'

    Input value can either be URI path part string ether list with path
    parts. If input type is list, then second parameter determines
    returning last_el_type.

    If input type is string, then last element type will be 'dir' if
    last char in string is '/', but it can be forced by last_el_type
    parameter.

    If input is list and second parameter is None, then returning
    last_el_type will be 'dir'. In both cases,

    if resulting last_el_type == 'dir', then path_str[-1:] == '/'.

    Parameter path_is_absolute can be used for manipulating '/' in
    begining of output path_str.

    examples:

    >>> urltools.paths_by_path('a/b/c/d')
    {'path_lst': ['a', 'b', 'c', 'd'],
     'path_str': '/a/b/c/d', 'last_el_type': 'file'}

    >>> urltools.paths_by_path('a/b/c/d/')
    {'path_lst': ['a', 'b', 'c', 'd'],
     'path_str': '/a/b/c/d/', 'last_el_type': 'dir'}

    >>> urltools.paths_by_path(['1','2','3','4'])
    {'path_lst': ['1', '2', '3', '4'],
     'path_str': '/1/2/3/4/', 'last_el_type': 'dir'}

    >>> urltools.paths_by_path(['1','2','3','4'], 'file')
    {'path_lst': ['1', '2', '3', '4'],
     'path_str': '/1/2/3/4', 'last_el_type': 'file'}

    '''
    if isinstance(path, list):
        path_str = '/'.join(path)
        path_lst = copy.copy(path)

        if last_el_type is None:
            last_el_type = 'dir'

    if isinstance(path, str):

        if last_el_type is None:
            if path[-1:] == '/':
                last_el_type = 'dir'
            else:
                last_el_type = 'file'

        if path_is_absolute is None:
            path_is_absolute = (path[0] == '/')

        t_path = path.strip('/')

        t_lst = t_path.split('/')

        path_str = '/' + t_path
        path_lst = []
        for i in t_lst:
            if i != '':
                path_lst.append(i)

    if last_el_type == 'dir':
        if path_str[-1:] != '/':
            path_str += '/'

    if path_is_absolute is None and path_str[0] != '/':
        path_str = '/' + path_str

    return {'path_str': path_str,
            'path_lst': copy.copy(path_lst),
            'last_el_type': last_el_type,
            'path_is_absolute': path_is_absolute}


def ischild(path1, path2):
    """
    Compairs two paths and returns True if path2 is child for path1
    """

    p1 = paths_by_path(path1)['path_lst']
    p2 = paths_by_path(path2)['path_lst']

    l1 = len(p1)
    l2 = len(p2)

    ret = True

    if l2 != (l1 + 1):
        ret = False

    if ret:
        for i in range(l1):
            if urllib.parse.unquote(p1[i]) != urllib.parse.unquote(p2[i]):
                ret = False
                break

    return ret

is_child = ischild


def parse_scheme_and_data(uri, ret_data=['scheme', 'data']):
    '''
    Parses URI and returns requested data.

    dici is returned if all ok. It will contain data relected by
    ret_data parameter.

    example:

       >>> parse_scheme_and_data('http://home.org:21/path')
       {'scheme': 'http', 'data': '//home.org:21/path'}
    '''

    ret = dict()

    re_res = re.match(r'(.*?):(.*)', uri)

    if re_res is not None:

        for i in ['scheme', 'data']:
            if i in ret_data:
                ret[i] = eval(i)

    else:
        ret = None

    return ret


def _parse_r(uri, part):
    s = parse_scheme_and_data(uri, [part])
    if s is None or s[part] is None:
        ret = None
    else:
        ret = s[part]
    return ret


def parse_scheme(uri):
    """Returns URI scheme part"""
    return _parse_r(uri, 'scheme')


def parse_data(uri):
    """Returns URI data part"""
    return _parse_r(uri, 'data')


def parse(
        url='http://login:password@example.net:80/some/path?with=parameters&an=d#anchor'
        ):
    """
    Parse URI and return None if error or dict structure accordingly
    to scheme name.

    This function, does not works with relative paths -- cases when
    there is no scheme present in URI -- None is returned.

    Currently, only http, https and ftp are allowed, and ftp treated
    as http.
    """
    scheme = parse_scheme(url)

    ret = None

    if scheme is None:
        ret = None
    else:
        re_res = re.match(r'(.*?):(.*)', url)

        if re_res is not None:
            scheme = re_res.group(1)
            data = re_res.group(2)

            if scheme in ['http', 'https', 'ftp']:
                ret = parse_all_data(data)
                ret['scheme'] = scheme
            else:
                ret = None

    return ret


def is_same_host(uri1, uri2):
    return is_same_site(uri1, uri2, False, False)


def is_same_site(
        uri1,
        uri2,
        not_if_scheme_not_eql=True,
        not_if_port_not_eql=True
        ):

    ret = True

    u1 = parse(uri1)
    u2 = parse(uri2)

    lst = ['host']

    if not_if_scheme_not_eql:
        lst.append('scheme')

    if not_if_port_not_eql:
        lst.append('port')

    for i in lst:
        if u1[i] != u2[i]:
            ret = False
            break

    return ret


def del_not_same_hosts(uri, lst):
    ret = list()

    for i in lst:
        if is_same_host(uri, i):
            ret.append(i)

    return ret


def del_not_same_sites(
        uri,
        lst,
        not_if_scheme_not_eql=True,
        not_if_port_not_eql=True
        ):
    """
    Takes URI. Takes URI list. And then, compares lst items to uri,
    forming new list to return.

    If host not same, lst item not goes to returning list.

    Additional parameters adds filtering by scheme and post: usualy,
    if scheme is not same - site assumed not same, but not all
    software thinking this way. E.g. noscript, assumes http://s.s and
    https://s.s the same site, but Apache httpd - does not.
    """

    ret = list()

    for i in lst:
        if is_same_site(uri, i, not_if_scheme_not_eql, not_if_port_not_eql):
            ret.append(i)

    return ret


def is_child_uri(
        uri1,
        uri2,
        not_if_scheme_not_eql=True,
        not_if_port_not_eql=True
        ):
    """
    Check is uri2 chiled to uri1
    """

    u1 = parse(uri1)
    u2 = parse(uri2)

    ret = True

    if u1 is None or u2 is None:
        ret = None

    else:
        if not is_same_site(
                uri1,
                uri2,
                not_if_scheme_not_eql,
                not_if_port_not_eql
                ):
            ret = None

        if not is_child(u1['path_lst'], u2['path_lst']):
            ret = False

    return ret


def del_not_child_uris(uri, lst):
    """
    Takes uri list, compares with uri and return list with uri childs
    """

    ret = list()

    for i in lst:
        if is_child_uri(uri, i):
            ret.append(i)

    return ret


def parse_parameters(data):
    """
    Parse URI parameter string to list and returns it

    Parameters can repeat

    examples:

       >>> parse_parameters('?a=1&b=2')
       [['a', '1'], ['b', '2']]

       >>> parse_parameters('a=1&b=2&a=3')
       [['a', '1'], ['b', '2'], ['a', '3']]

    """
    t_data = data.lstrip('?')

    data_splitted = t_data.split('&')

    para_list = []

    for i in data_splitted:
        para_splitted = i.split('=')
        if len(para_splitted) == 1:
            para_splitted.append(None)
        para_list.append(para_splitted)

    return copy.copy(para_list)


def parse_auth(data):
    """
    Parses URI authentication string to parts.

    Returns None if data == None or data == ''

    Else, returns dict with two values:

       - login: login part
       - password: password part

    examples:

       >>> parse_auth('123123@')
       {'login': '123123', 'password': None}

       >>> parse_auth('123123:@')
       {'login': '123123', 'password': ''}

       >>> parse_auth('123123:123@')
       {'login': '123123', 'password': '123'}

       >>> parse_auth(':123@')
       {'login': '', 'password': '123'}

       >>> parse_auth(':@')
       {'login': '', 'password': ''}

       >>> parse_auth(':')
       {'login': '', 'password': ''}

       >>> parse_auth('')
       None

       >>> parse_auth(None)
       None

    """
    if data is None or data == '':
        return None

    re_res = re.match(r'^(.*?)(:.*?)?@?$', data)

    if re_res is not None:
        login = re_res.group(1)
        password = None
        if re_res.group(2) is not None:
            password = re_res.group(2)[1:]
        else:
            password = None

        return {'login': login, 'password': password}
    else:
        return None


def parse_all_data(data):
    '''
    Can be deployed to strings like C{//agu:@wayround.org:21/1/2/3/4/?a#3}

    Such a string then will be parsed on several parts. Then thous
    parts will be worked out to dict like:

       >>> repr()
       {'anchor': '3',
        'auth': {'login': 'agu', 'password': ''},
        'host': 'wayround.org',
        'param_lst': [['a', None]],
        'path_lst': ['1', '2', '3', '4'],
        'path_str': '/1/2/3/4',
        'path_is_absolute': True,
        'last_el_type': 'file',
        'port': '21'}

    '''
    ret = dict(
        auth=None,  # or dict {'login':'', 'password':
        # ''}, where login must be string, and
        # password can be None
        host=None,
        port=None,
        path_str=None,
        path_lst=None,
        last_el_type=None,
        path_is_absolute=None,
        param_lst=None,
        anchor=None
        )

    re_res = re.match(r'^//(.*@)?(.*?)(:\d*)?(/.*?)?(\?.*?)?(\#.*)?$', data)

    if re_res is not None:
        # print 'auth: '+ repr(re_res.group(1))
        # print 'host: '+ repr(re_res.group(2))
        # print 'port: '+ repr(re_res.group(3))
        # print 'path: '+ repr(re_res.group(4))
        # print 'para: '+ repr(re_res.group(5))
        # print '  id: '+ repr(re_res.group(6))
        # print

        ret['auth'] = parse_auth(re_res.group(1))

        if re_res.group(2) is not None:
            ret['host'] = re_res.group(2)

        if re_res.group(3) is not None:
            ret['port'] = re_res.group(3)[1:]

        if re_res.group(4) is not None:
            t_p = paths_by_path(re_res.group(4))
            if t_p is None:
                ret['path_str'] = None
                ret['path_lst'] = None
                ret['last_el_type'] = None
                ret['path_is_absolute'] = None
            else:
                ret['path_str'] = t_p['path_str']
                ret['path_lst'] = t_p['path_lst']
                ret['last_el_type'] = t_p['last_el_type']
                ret['path_is_absolute'] = t_p['path_is_absolute']

        if re_res.group(5) is not None:
            ret['param_lst'] = parse_parameters(re_res.group(5))

        if re_res.group(6) is not None:
            ret['anchor'] = re_res.group(6)[1:]

        return ret
    return None


def combine_data(scheme='http',
                 auth={'login': 'anonymous',
                       'password': 'myemail'},
                 host='example.net',
                 port=80,
                 path='/',
                 parameters={},
                 anchor=''):
    '''
    Constructs URI string from parameters

    auth tuple can be complitly None or password can be None. auth
    login must allways be string or unicode, password too.

    port automaticly set to 80 or 443 if http or https scheme
    accordingly.

    parameters can be None or dicrionary like {'name':'value'}
    '''

    auth_str = ''
    port_str = ''
    use_port = False
    param_str = ''
    use_param = False
    anchor_str = ''
    use_anchor = False

    if auth is not None:
        auth_str = auth[0]
        if auth[1] is not None:
            auth_str += ':' + auth[1]
        auth_str += '@'

    if scheme == 'http' and port != 80:
        use_port = True

    if scheme == 'https' and port != 443:
        use_port = True

    if use_port:
        port_str = ':' + str(port)

    if parameters is not None and len(parameters.keys()) > 0:
        use_param = True

    if isinstance(path, list):
        path = '/'.join(path)

    if use_param:
        param_str = '?'
        param_lst = []
        for i in parameters.keys():
            p2 = parameters[i]

            if isinstance(p2, (int, float)):
                p2 = str(p2)

            if isinstance(p2, bytes):
                p2.decode('utf-8')

            param_lst.append(str(i) + '=' + p2)

        param_str += '&'.join(param_lst)

    if anchor is not None and anchor != '':
        use_anchor = True

    if use_anchor:
        anchor_str = '#' + anchor

    res = \
        scheme \
        + '://' \
        + auth_str \
        + host \
        + port_str \
        + path \
        + param_str \
        + anchor_str
    return res
