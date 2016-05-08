# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.parser : Parse hsf xml files to get consumer and provider
"""


import os
import re
import shutil

import edsd.envcmd
import edsd.common
import edsd.logpeeker
import edsd.err

from xml.etree import ElementTree
from edsd import __version__, DEBUG

__license__ = "GNU License"
__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"


class HSF(object):
    """Represents an HSF object inside xml definitions.
    """
    id = None
    interface = None
    group = None

    def __init__(self, _id, interface, group):
        self.id = _id
        self.interface = interface
        self.group = group

    def check(self): pass

    def collect(self, path): pass

    @classmethod
    def parsed_from_xml(cls, xml):
        """An mapper method, parsed an xml dom into an HSF Object, details should
        see the implementations.
        """
        raise "Not Supported"


class Consumer(HSF):
    """An HSF Provider object defined inside xml."""

    def __init__(self, _id, interface, group):
        super(Consumer, self).__init__(_id, interface, group)
        self.ok_pattern = re.compile('\[Register-ok\].*?%s' % self.interface)

    def check(self):
        with open(HSFactory.instance().cc_logpath) as f:
            for l in f.xreadlines():
                if self.ok_pattern.search(l):
                    return
        edsd.err.report_fail("subscriber '%s' registered failed." % self.interface)

    def collect(self, path):
        sp = edsd.envcmd.configclient_snapshot_path()
        if sp is None:
            return

        srcs = [os.path.join(sp, x, '%s.dat' % self.group)
                for x in os.listdir(sp) if self.interface in x]

        if len(srcs) == 0:
            return

        dst = '%s/configclient/%s/' % (path, self.interface)
        edsd.common.ensure_dir(dst)

        for src in srcs:
            if not os.path.isfile(src):
                continue
            shutil.copy(src, dst)

    @classmethod
    def parsed_from_xml(cls, xml):
        if xml is None:
            return

        return Consumer(xml.get('id'),
                        xml.get('interface'),
                        xml.get('group'))

    def __eq__(self, other):
        if other is None or not isinstance(other, Provider):
            return False

        return self.interface == other.interface \
               and self.group == other.group


class Provider(HSF):
    """An HSF Consumer object defined inside xml."""
    version = None

    def __init__(self, _id, interface, group, version):
        super(Provider, self).__init__(_id, interface, group)
        self.version = version
        self.ok_pattern = re.compile('\[Publish-ok\].*?%s' % self.interface)

    def check(self):
        with open(HSFactory.instance().cc_logpath) as f:
            for l in f.xreadlines():
                if self.ok_pattern.search(l):
                    return
        edsd.err.report_fail("service '%s' publish failed." % self.interface)

    def collect(self, path):
        src = HSFactory.instance().cc_logpath
        shutil.copy(src, path)

    @classmethod
    def parsed_from_xml(cls, xml):
        if xml is None:
            return

        return Provider(xml.get('id'),
                        xml.get('interface'),
                        xml.get('group'),
                        xml.get('version'))

    def __eq__(self, other):
        if other is None or not isinstance(other, Consumer):
            return False

        return self.interface == other.interface \
               and self.version == other.version \
               and self.group == other.group


class HSFactory(object):
    """An HSF Factory class for loading and parsing HSF object based on the
    configured xml files.
    """

    _consumers = set()
    _providers = set()

    consumers = property(lambda self: HSFactory._consumers)
    providers = property(lambda self: HSFactory._providers)

    # config client log path.
    _cc_logpath = None

    @property
    def cc_logpath(self):
        if self._cc_logpath is not None:
            return self._cc_logpath

        created = edsd.envcmd.tomcat_process_createtime()
        log_path = edsd.envcmd.configclient_logpath()

        if log_path is None:
            edsd.err.report_fail('Config client log path is not found')

        self._cc_logpath = edsd.logpeeker.move_patial_log(
            log_path, created)

        return self._cc_logpath

    @classmethod
    def instance(cls):
        inst = getattr(cls, '_instance', None)
        if inst:
            return inst

        inst = HSFactory()
        if not cls._consumers and not cls._providers:
            cls.parse_hsf_object()

        setattr(cls, '_instance', inst)
        return inst

    @classmethod
    def parse_hsf_object(cls):
        providerfiles = edsd.envcmd.providerxml_files()
        consumerfiles = edsd.envcmd.consumerxml_files()

        parsed = providerfiles + consumerfiles
        for f in set(parsed):
            cls.feed_file(f)

    def check(self):
        for p in self.providers:
            p.check()

        for c in self.consumers:
            c.check()

    def collect(self, path):
        clc_path = edsd.envcmd.collect_path()
        path = os.path.join(path, clc_path)
        edsd.common.ensure_dir(path)

        for p in self.providers:
            p.collect(path)

        for c in self.consumers:
            c.collect(path)

    @classmethod
    def feed_file(cls, f):
        if not os.path.isfile((f)):
            return

        try:
            xml = ElementTree.parse(f)
            root = xml.getroot()
            consumers = root.findall('{http://www.taobao.com/hsf}consumer')
            providers = root.findall('{http://www.taobao.com/hsf}provider')

            consumers = filter(bool, map(Consumer.parsed_from_xml, consumers))
            providers = filter(bool, map(Provider.parsed_from_xml, providers))

            cls._providers.update(providers)
            cls._consumers.update(consumers)
        except Exception as _:
            if DEBUG:
                import traceback
                traceback.print_exc()

