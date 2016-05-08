# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.envcmd : A collection of implementation of commands used for exe-
    cuting os commands and http methods.
"""

import email.utils
import functools
import httplib
import os
import re

from edsd import __version__, DEBUG
from edsd.common import today_in_str, EDAS_DIRECTORY

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"


class Status(object):
    OK = 0
    FAIL = -1
    PONG = 2
    PANG = -2


def syscmd(cmd, readstd=True, readerr=False):
    """Execute an os command and return the sys out/err string, this method will
    ignore the sys err message during the execution.

    :param readerr: read from stderr if this flag is marked.
    :param cmd: command string for executing.
    :return: sys out/err string, empty string('') will be returned if any
    exception raised.
    """
    try:
        _, stdout, stderr = os.popen3('%s' % cmd)
        if readstd and readerr:
            return stdout.read().strip(), \
                   stderr.read().strip()
        elif readstd:
            return stdout.read().strip()
        elif readerr:
            return stderr.read().strip()
    except:
        # return empty string when any exception raised.
        return ''


def test_http(url):
    """Test if the http url is connectable, this method will execute a HEAD method
    against the destination url

    :param url: testing url.
    :return: True if get successfully get a response returned, else False.
    """
    res = _get(url, 'HEAD')

    return res.status in (200, 301, 302) if res else False


def test_socket(host, port):
    """Test the socket is connectable

    :param host: the destination host ip
    :param port: the destination port
    :return: True if the socket is open, False if any timeout happened
    """
    import socket
    socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    r = True

    try:
        s = socket.create_connection((host, port), 1000)
        s.send('GET / HTTP/1.1\r\n\r\n')
    except socket.timeout as _:
        r = False

    try:
        if r:
            s.settimeout(2)
            s.recv(1)
            s.close()
    except socket.timeout as _:
        # ignore timeout error
        pass

    try:
        s.close()
    except Exception as _:
        pass

    return r


def getheaders(url):
    """Executing the HEAD method against url and return the header list

    :param url: URL used to head
    :return: List of headers, return None if any exception raised or status is
    not between 200 and 400
    """
    res = _get(url, 'HEAD')
    if res is None or res.status < 200 or res.status >= 400:
        return None

    return res.getheaders()


def get_server_datetime(url):
    """Get server datetime through an http HEAD method, and parse it from the
    http header 'HEAD', e.g:

    >>> get_server_datetime('http://www.taobao.com/')
    1461848925

    :param url: server url to fetch header 'date'
    :return: timestamp in seconds represents in the header('date'), return 0 if
    the url is fetch failed.
    """
    res = _get(url, 'HEAD')
    if res is None:
        return 0

    dt = res.getheader('date', 0)
    if not dt:
        return 0

    tzdate = email.utils.parsedate_tz(dt)
    return email.utils.mktime_tz(tzdate)

re_host = re.compile('https?://([^/]+)(/.*)')


def _get(url, method='GET'):
    """Execute and http get/head command against a url.

    :param url: The url wanted to connect
    :return: None if url is invalid, otherwise return the http body be default
    """
    if not url:
        return None

    m = re_host.match(url)
    host, url = m.group(1), m.group(2)

    use_ssl = url.startswith('https')
    con_clz = httplib.HTTPSConnection if use_ssl else httplib.HTTPConnection

    try:
        conn = con_clz(host)
        conn.request(method, url)
        return conn.getresponse()
    except Exception as _:
        return None


def get(url):
    try:
        res = _get(url)
        return res.read()
    except:
        return None


def notify_console_alive():
    api = '/v1/heartbeat/alive'
    data = dict(ecuId=ecu_id())
    res = post_console(data, api)
    return res.code == 200


def post_console(data, api):
    """Post json data to console.

    :param data: data to post
    :param api: api to connect
    :return: HttpResponse
    """
    import urllib2
    import json
    import types

    if isinstance(data, types.DictionaryType):
        data = json.dumps(data)

    spas = spas_info()
    if spas is None:
        raise "Spas info not found."

    ak = spas['accessKey']
    sk = spas['secretKey']

    url = 'http://edas-internal.console.aliyun.com/rest%s' % api
    sig = hmacsha1(sk, data)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-EDAS-AccessKey": ak,
        "X-EDAS-Signature": sig
    }

    req = urllib2.Request(url, data, headers)
    return urllib2.urlopen(req)


def pid_uptime_ts(pid):
    """return the process uptime in timestamp, e.g:

    >>> pid_uptime_ts(21269)
    1461848925

    :param pid: process identifier
    :return: timestamp of the process's uptime in seconds
    """
    return int(syscmd("stat -c %Y /proc/%s" % pid))


def tomcat_info():
    th = tomcat_home()
    return syscmd('%s/bin/version.sh | egrep (CATALINA_HOME|Server version)' % th)


def read_setenv_info():
    r = re.compile('CATALINA_OPTS="([^"]+)"')
    th = tomcat_home()
    se = "%s/bin/setenv.sh" % th
    args = None

    with open(se) as f:
        for line in f.readlines():
            m = r.search(line)
            if not m:
                continue
            args = m.group(1)

    if args is None:
        return None

    return dict([tuple(x[2:].split('=')) for x in args.split(" ")
                 if x and x.startswith('-D')])


def tomcat_pid():
    try:
        return syscmd("pgrep -u admin "
                      "-f 'Dtenant.id.*org.apache.catalina.startup.Bootstrap'")\
            .strip()
    except:
        return ''


def cai_server_host_port():
    default_cai = ('jmenv.tbsite.net', 8080)
    th = tomcat_home()
    if not th:
        return default_cai

    env_info = read_setenv_info()
    if not env_info:
        return default_cai

    host = env_info.get('address.server.domain', 'jmenv.tbsite.net')
    port = env_info.get('address.server.port', 8080)

    return host, port


def config_server_host_port():
    env_info = read_setenv_info() or {}
    ch, cp = cai_server_host_port()

    host = env_info.get('configserver.client.host', None)
    if host is None:
        host = get('http://%s:%s/configserver/serverlist' % (ch, cp))

    if not host:
        return None

    host = host.split('\n')[0]
    port = env_info.get('configserver.client.port', 9600)
    return host, port


def diamond_server_host():
    ch, cp = cai_server_host_port()
    host = get('http://%s:%s/diamond-server/diamond' % (ch, cp))

    if not host:
        return None

    return host.split('\n')[0]


def dauth_diamond_host():
    ch, cp = cai_server_host_port()
    host = get('http://%s:%s/diamond-server/diamond-unit-spas?nofix=1' % (ch, cp))

    if not host:
        return None

    return host.split('\n')[0]


def tomcatxml_has(keyword, *_):
    th = tomcat_home()
    if not th:
        return False

    r = syscmd("find %s/deploy/ -name '*.xml' -exec "
               "grep '%s' {} \;" % (th, keyword))

    return r.strip() != '' if r else False


hasconsumer = functools.partial(tomcatxml_has, 'consumer')
hasprovider = functools.partial(tomcatxml_has, 'provider')


def findhsf_xmlfile(keyword):
    th = tomcat_home()
    if not th:
        return []

    r = syscmd('find %s/deploy/ -name "*.xml" -exec grep "%s" -l {} \;' %
               (th, keyword))
    fnames = r.split('\n')

    return [os.path.join(th, x[2:]) for x in fnames if x.startswith('./')] + \
           [x for x in fnames if os.path.isfile(x)]


consumerxml_files = functools.partial(findhsf_xmlfile, 'consumer')
providerxml_files = functools.partial(findhsf_xmlfile, 'provider')


def collect_path():
    localhost = syscmd('hostname -i')
    return '%s/collect_%s_%s' % (EDAS_DIRECTORY, localhost, today_in_str())


def configclient_logpath():
    p = '/home/admin/configclient/logs/config.client.log'
    if os.path.isfile(p):
        return p

    return None


def configclient_snapshot_path():
    p = '/home/admin/configclient/snapshot'
    if os.path.isdir(p):
        return p

    return None


def tomcat_process_createtime():
    pid = tomcat_pid()
    if not pid:
        return 0

    ts = syscmd('stat -c %%Z /proc/%s' % pid)
    if not ts:
        return 0

    return float(ts)


def tomcat_home():
    tpid = tomcat_pid()
    # ensure only one tomcat is started and we can parse that from the command
    # line, otherwise, we need to fallback the procedure from config files
    if tpid and len(tpid.strip().split('\n')) == 1:
        return parse_from_cmdline(tpid)

    return enum_and_guess_home()


def parse_from_cmdline(tpid):
    home = syscmd('cat /proc/%s/cmdline '
                  '| xargs -i -0 -exec echo {} '
                  '| grep catalina.home' % tpid)\
        .strip()

    try:
        return home.split('=')[1]
    except:
        return None


def spas_info():
    env_info = read_setenv_info() or {}

    spas_file = env_info.get('spas.identity',
                             '/home/admin/.spas_key/default')
    spas = load_properties(spas_file)
    if spas is None:
        return None

    spas.update(env_info)
    return spas


def ecu_id():
    fname = '/home/admin/edas-agent/conf/ecs.conf'
    d = load_properties(fname)
    return d.get('UUID', None) if d else None


def localhost_logpath(log_path):
    f = '%s/localhost.log.%s' % (log_path, today_in_str())
    if os.path.isfile(f):
        return f

    f = '%s/localhost.log.%s.txt' % (log_path, today_in_str())
    if os.path.isfile(f):
        return f

    return None


def load_properties(fname):
    with open(fname) as f:
        kvs = [l.strip().split('=', 1) for l in f.readlines()
               if l and l.strip()]
        return dict(kvs)

    return {}


def hmacsha1(key, data):
    from hashlib import sha1
    import hmac
    import base64

    m = hmac.new(key, data, sha1).digest()
    return base64.b64encode(m)


def edas_agent_home():
    home = '/home/admin/edas-agent/'
    if os.path.isdir(home):
        return home

    home = '/home/admin/agent/'
    if os.path.isdir(home):
        return home

    return None


def enum_and_guess_home():
    import tarfile

    tmp_home = '%s/temp' % edas_agent_home()

    files = os.listdir(tmp_home)
    files = filter(lambda f: 'tomcat' in f or 'edas-container' in f, files)
    if len(files) != 1:
        return None

    fp = files[0]
    try:
        tf = tarfile.open(os.path.join(tmp_home, fp))
        tf = tf.getnames()[0]
        if tf.startswith('./'):
            path = tf[2:]
        else:
            path = os.path.split(tf)[0] if '/' in tf else tf

        maybe = '/home/admin/%s' % path
        if os.path.isdir(maybe):
            return maybe
    except:
        if DEBUG:
            import traceback
            traceback.print_exc()

    return None


def resolve_name(host):
    import socket
    try:
        return socket.gethostbyname(host)
    except:
        return None