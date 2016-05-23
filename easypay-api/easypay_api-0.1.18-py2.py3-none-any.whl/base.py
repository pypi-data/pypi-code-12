#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Easypay API
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Easypay API.
#
# Hive Easypay API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Easypay API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Easypay API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import time
import uuid
import shelve
import threading
import traceback

import xml.dom.minidom
import xml.etree.ElementTree

import appier

from . import mb
from . import errors

LOOP_TIMEOUT = 60.0
""" The timeout to be used between tick intervals for
the scheduler to process the various pending documents
and requests for detailed information """

BASE_URL = "https://www.easypay.pt/_s/"
""" The default base url to be used for a production
based environment, should be used carefully """

BASE_URL_TEST = "http://test.easypay.pt/_s/"
""" The base url for the sandbox endpoint, this is used
for testing purposes only and the password is sent using
a non encrypted model (no protection provided) """

class Scheduler(threading.Thread):
    """
    Scheduler thread that is used to poll the remote easypay
    server for the detailed information on the document and
    then notify the final api client about the new information.
    """

    def __init__(self, api):
        threading.Thread.__init__(self)
        self.api = api
        self.daemon = True

    def run(self):
        self.running = True
        while self.running:
            try:
                self.tick()
            except BaseException as exception:
                self.api.logger.critical("Unhandled easypay exception raised")
                self.api.logger.error(exception)
                lines = traceback.format_exc().splitlines()
                for line in lines: self.api.logger.warning(line)
            time.sleep(LOOP_TIMEOUT)

    def stop(self):
        self.running = False

    def tick(self):
        """
        Runs one tick operation, meaning that all the pending
        documents will be retrieved and a try will be made to
        retrieve the detailed information on them.
        """

        docs = self.api.list_docs()
        for doc in docs:
            identifier = doc["identifier"]
            details = self.api.details_mb(identifier)
            self.api.mark_mb(details)

class Api(
    appier.Api,
    mb.MBApi
):
    """
    Top level entry point for the easypay api services,
    should provide the abstract implementations for the
    services offered by easypay.

    Concrete implementations of this api should provide
    other storage options that should include persistence.
    """

    def __init__(self, *args, **kwargs):
        appier.Api.__init__(self, *args, **kwargs)
        self.production = appier.conf("EASYPAY_PRODUCTION", False, cast = bool)
        self.username = appier.conf("EASYPAY_USERNAME", None)
        self.password = appier.conf("EASYPAY_PASSWORD", None)
        self.cin = appier.conf("EASYPAY_CIN", None)
        self.entity = appier.conf("EASYPAY_ENTITY", None)
        self.production = kwargs.get("production", self.production)
        self.username = kwargs.get("username", self.username)
        self.password = kwargs.get("password", self.password)
        self.cin = kwargs.get("cin", self.cin)
        self.entity = kwargs.get("entity", self.entity)
        self.base_url = BASE_URL if self.production else BASE_URL_TEST
        self.counter = 0
        self.references = dict()
        self.docs = dict()
        self.lock = threading.RLock()
        self.scheduler = Scheduler(self)

    def start_scheduler(self):
        if self.scheduler.is_alive(): return
        self.scheduler.start()

    def stop_scheduler(self):
        if not self.scheduler.is_alive(): return
        self.scheduler.stop()

    def request(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        result = self.loads(result)
        status = result.get("ep_status", "err1")
        message = result.get("ep_message", "no message defined")
        if not status == "ok0": raise errors.ApiError(message)
        return result

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        appier.Api.build(self, method, url, headers, kwargs)
        if self.cin: kwargs["ep_cin"] = self.cin
        if self.username: kwargs["ep_user"] = self.username

    def diagnostics(self):
        return dict(
            references = self.list_references(),
            docs = self.list_docs()
        )

    def gen_reference(self, data):
        cin = data["ep_cin"]
        username = data["ep_user"]
        entity = data["ep_entity"]
        reference = data["ep_reference"]
        value = data["ep_value"]
        identifier = data["t_key"]
        reference = dict(
            cin = cin,
            username = username,
            entity = entity,
            reference = reference,
            value = value,
            identifier = identifier,
            status = "pending"
        )
        self.new_reference(reference)
        return reference

    def gen_doc(self, identifier, key):
        doc = dict(
            cin = self.cin,
            username = self.username,
            identifier = identifier,
            key = key
        )
        self.new_doc(doc)
        return doc

    def new_reference(self, reference):
        identifier = reference["identifier"]
        self.references[identifier] = reference

    def del_reference(self, identifier):
        del self.references[identifier]

    def list_references(self):
        references = self.references.values()
        return appier.legacy.eager(references)

    def get_reference(self, identifier):
        return self.references.get(identifier, None)

    def new_doc(self, doc):
        identifier = doc["identifier"]
        self.docs[identifier] = doc

    def del_doc(self, identifier):
        del self.docs[identifier]

    def list_docs(self):
        docs = self.docs.values()
        return appier.legacy.eager(docs)

    def get_doc(self, identifier):
        return self.docs.get(identifier, None)

    def next(self):
        self.lock.acquire()
        try: self.counter += 1; next = self.counter
        finally: self.lock.release()
        return next

    def generate(self):
        identifier = str(uuid.uuid4())
        return identifier

    def validate(self, cin = None, username = None):
        if cin and not cin == self.cin:
            raise errors.SecurityError("invalid cin")
        if username and not username == self.username:
            raise errors.SecurityError("invalid username")

    def loads(self, data):
        result = dict()
        document = xml.dom.minidom.parseString(data)
        base = document.childNodes[0]
        for node in base.childNodes:
            name = node.nodeName
            value = self._text(node)
            if value == None: continue
            result[name] = value
        return result

    def dumps(self, map, root = "getautoMB_detail", encoding = "utf-8"):
        root = xml.etree.ElementTree.Element(root)
        for name, value in map.items():
            value = value if type(value) in appier.legacy.STRINGS else str(value)
            child = xml.etree.ElementTree.SubElement(root, name)
            child.text = value
        result = xml.etree.ElementTree.tostring(
            root,
            encoding = encoding,
            method = "xml"
        )
        header = appier.legacy.bytes("<?xml version=\"1.0\" encoding=\"%s\"?>" % encoding)
        result = header + result
        return result

    def _text(self, node):
        if not node.childNodes: return None
        return node.childNodes[0].nodeValue

class ShelveApi(Api):
    """
    Shelve api based infra-structure, that provides a storage
    engine based for secondary storage persistence. This class
    should be used only as a fallback storage as the performance
    is considered poor, due to large overhead in persistence.
    """

    def __init__(self, *args, **kwargs):
        Api.__init__(self, *args, **kwargs)
        self.path = appier.conf("EASYPAY_PATH", "easypay.shelve")
        self.path = kwargs.get("path", self.path)
        base_path = os.path.dirname(self.path)
        exists = not base_path or os.path.exists(base_path)
        if not exists: os.makedirs(base_path)
        self.shelve = shelve.open(
            self.path,
            protocol = 2,
            writeback = True
        )

    def new_reference(self, reference):
        identifier = reference["identifier"]
        self.lock.acquire()
        try:
            references = self.shelve.get("references", {})
            references[identifier] = reference
            self.shelve["references"] = references
            self.shelve.sync()
        finally:
            self.lock.release()

    def del_reference(self, identifier):
        self.lock.acquire()
        try:
            references = self.shelve.get("references", {})
            del references[identifier]
            self.shelve["references"] = references
            self.shelve.sync()
        finally:
            self.lock.release()

    def list_references(self):
        self.lock.acquire()
        try:
            references = self.shelve.get("references", {})
            references = references.values()
            references = appier.legacy.eager(references)
        finally:
            self.lock.release()
        return references

    def get_reference(self, identifier):
        self.lock.acquire()
        try:
            references = self.shelve.get("references", {})
            reference = references.get(identifier, None)
        finally:
            self.lock.release()
        return reference

    def new_doc(self, doc):
        identifier = doc["identifier"]
        self.lock.acquire()
        try:
            docs = self.shelve.get("docs", {})
            docs[identifier] = doc
            self.shelve["docs"] = docs
            self.shelve.sync()
        finally:
            self.lock.release()

    def del_doc(self, identifier):
        self.lock.acquire()
        try:
            docs = self.shelve.get("docs", {})
            del docs[identifier]
            self.shelve["docs"] = docs
            self.shelve.sync()
        finally:
            self.lock.release()

    def list_docs(self):
        self.lock.acquire()
        try:
            docs = self.shelve.get("docs", {})
            docs = docs.values()
            docs = appier.legacy.eager(docs)
        finally:
            self.lock.release()
        return docs

    def get_doc(self, identifier):
        self.lock.acquire()
        try:
            docs = self.shelve.get("docs", {})
            doc = docs.get(identifier, None)
        finally:
            self.lock.release()
        return doc

    def next(self):
        self.lock.acquire()
        try:
            counter = self.shelve.get("counter", 0)
            counter += 1
            next = counter
            self.shelve["counter"] = counter
            self.shelve.sync()
        finally:
            self.lock.release()
        return next
