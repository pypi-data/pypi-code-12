# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.collect : Collect all running information
"""

import shutil
import edsd.hsf

from edsd import DEBUG, __version__
from edsd.common import EDAS_DIRECTORY, ensure_dir
from edsd.envcmd import *
from facade import log_info, log_done


__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"

collects = []


def do_collect(f):

    def _(*args, **kwargs):
        try:
            name = f.func_name.replace('_', ' ')
            log_info(name, end=False)
            f(*args, **kwargs)
        except:
            if DEBUG:
                import traceback
                traceback.print_exc()

    collects.append(_)
    return _


def collect():
    log_info('Start collecting ')
    clc_path = collect_path()

    if os.path.isdir(clc_path):
        shutil.rmtree(clc_path)

    ensure_dir(clc_path)

    for f in collects:
        f(clc_path)

    log_info('Packaging all the information   ', end=False)
    d, f = os.path.dirname(clc_path), os.path.basename(clc_path)
    syscmd('cd %s && tar zcvf %s.tar.gz %s' % (d, f, f))
    log_done('\r\nInformation saved in: %s.tar.gz' % clc_path)


@do_collect
def collect_agent_info(path):
    p = os.path.join(path, 'edas-agent')
    ensure_dir(p)
    h = edas_agent_home()
    shutil.copy('%s/logs/agent.log' % h, p)
    shutil.copy('%s/conf/agent.conf' % h, p)
    shutil.copy('%s/conf/ecs.conf' % h, p)


@do_collect
def address_servers(path):
    info = "=" * 20 + "Address Server Information" + "=" * 20 + "\r\n"
    try:
        h, p = cai_server_host_port()
        info += "\r\n\taddress host:port=%s:%s" % (h, p)
        address_server_ip = resolve_name(h)
        info += "\r\n\taddress host resolved ip= %s" % address_server_ip
        addr = 'http://%s:%s' % (h, p)
        diamond = diamond_server_host()
        info += "\r\n\tdiamond server address= %s" % diamond
        ch, cp = config_server_host_port()
        info += "\r\n\tconfig server host:port= %s:%s" % (ch, cp)
        ddh = dauth_diamond_host()
        info += "\r\n\tdauth diamond host= %s" % ddh
        spec_url = 'http://%s:8080/diamond-server/config.do?group=spas_info&' \
                   'dataId=spas_authentication_url' % ddh
        spas_spec = get(spec_url)
        spas_ok = test_http(spas_spec)
        info += "\r\n\tdauth spec url= %s\tconnection status %s\r\n" % \
                (spas_spec, "OK" if spas_ok else "Failed")
    except Exception as e:
        info += "\r\n\r\n some address server resolved failed: %s" % str(e)

    f = os.path.join(path, 'address-info.log')
    with open(f, 'wa') as f:
        f.writelines(info)


@do_collect
def copy_tomcat_files(path):
    pid = tomcat_pid()
    if pid:
        syscmd('kill -3 %s' % pid)

    th = tomcat_home()
    if not th:
        return

    dst = os.path.join(path, 'tomcat')
    syscmd("find %s/deploy -name '*.xml' -exec cp {} %s \;" % (th, dst))

    ensure_dir(dst)
    shutil.copy('%s/logs/catalina.out' % th, dst)
    lp = localhost_logpath('%s/logs' % th)

    if not lp:
        return

    shutil.copy(lp, dst)



@do_collect
def collect_system_info(path):
    import json, time

    info = '=' * 20 + "System Information" + '=' * 20 + '\r\n'
    jversion = syscmd('java -version', readerr=True, readstd=False)
    info += '\r\n\r\n======= JAVA VERSION ===== \r\n' + jversion

    jvms = syscmd('ps aux|grep jav[a]')
    info += '\r\n\r\n======= JVM Instances ===== \r\n' + jvms

    ulimit = syscmd('ulimit -a')
    info += '\r\n\r\n======= ULIMIT VERSION ===== \r\n' + ulimit

    server_time = get_server_datetime('http://www.taobao.com/')
    now = time.time()
    delta = 'server time(%s) - local time(%s) = %s' % \
            (server_time, now, (server_time - now))
    info += '\r\n\r\n======= Time Date ===== \r\n' + delta

    ipaddrs = syscmd("ifconfig|grep 'inet addr'")
    info += '\r\n\r\n======= IP Addresses ===== \r\n' + ipaddrs

    hostnamei = syscmd('hostname -i')
    info += '\r\n\r\n======= hostname -i ===== \r\n' + hostnamei

    mem = syscmd("free -m")
    info += '\r\n\r\n======= Memory Status ===== \r\n' + mem

    disk = syscmd("df -h")
    info += '\r\n\r\n======= Disk Status ===== \r\n' + disk

    env = read_setenv_info()
    if env:
        j = json.dumps(env, indent=4)
        info += '\r\n\r\n======= Application args ===== \r\n' + j

    th = tomcat_home()
    if th:
        tversion = syscmd('%s/bin/version.sh' % th)
        info += '\r\n======= Tomcat Information ======== \r\n' + tversion

    sysinfo = os.path.join(path, 'sysinfo.log')
    with open(sysinfo, 'wa') as f:
        f.writelines(info)


@do_collect
def copy_hsf_log(path):
    dst = os.path.join(path, 'hsf')
    src = '/home/admin/logs/hsf'
    shutil.copytree(src, dst)


@do_collect
def copy_spas_info(path):
    dst = os.path.join(path, 'spas')
    ensure_dir(dst)
    ei = read_setenv_info()
    if not ei:
        return

    si = ei.get('spas.identity', '/home/admin/.spas_key/default')
    if os.path.isfile(si):
        shutil.copy(si, dst)

    pn = ei.get('project.name', None)
    if pn is None:
        return

    src = '/home/admin/%s/logs/spas_sdk.log' % pn
    shutil.copy(src, dst)


@do_collect
def copy_diamond_client_log(path):
    src = '/home/admin/logs/diamond-client/diamond-client.log'
    shutil.copy(src, path)


@do_collect
def copy_configclient_log(path):
    src = '/home/admin/configclient/logs/config.client.log'
    shutil.copy(src, path)


@do_collect
def collect_hsf_files(path):
    edsd.hsf.HSFactory.instance().collect(path)
