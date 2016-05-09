# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from glb.core.extensions import allocated_port
from .base import Model


class Balancer(Model):
    __prefix_key__ = 'balancers'
    __primary_key__ = 'name'
    __schema_default__ = {
        'name': '',
        'frontend': {},
        'backends': [],
        'entrypoints': []}

    def call_update_frontend(self, val):
        """update frontend (note: port readonly)"""
        if not val:
            val = {}
        if 'port' in val.keys():
            val.pop('port')
        self.frontend.update(val)
        return self.update(self.name, dict(frontend=self.frontend))

    def call_add_backends(self, val):
        """add backends"""
        for backend in val:
            if backend not in self.backends:
                self.backends.append(backend)
        return self.update(self.name, dict(backends=self.backends))

    def call_update_backends(self, val):
        """update all backends"""
        return self.update(self.name, dict(backends=val))

    def call_delete_backend_by_cid(self, val):
        """remove backend by container id"""
        for backend in self.backends:
            if backend.get('cid', None) == val:
                self.backends.remove(backend)
        return self.update(self.name, dict(backends=self.backends))

    def call_delete_backend_by_addr_port(self, addr, port):
        """remove backend by container id"""
        for backend in self.backends:
            if (backend.get('address', None) == addr and
                    backend.get('port', 0) == port):
                self.backends.remove(backend)
        return self.update(self.name, dict(backends=self.backends))

    def call_delete_backend_by_tag(self, val):
        """remove backend by container id"""
        for backend in self.backends:
            if backend.get('tag', None) == val:
                self.backends.remove(backend)
        return self.update(self.name, dict(backends=self.backends))

    def call_add_entrypoints(self, val):
        """add entrypoints"""
        for entrypoint in val:
            if entrypoint not in self.entrypoints:
                self.entrypoints.append(entrypoint)
        return self.update(self.name, dict(entrypoints=self.entrypoints))

    def call_update_entrypoints(self, val):
        """update all entrypoints"""
        return self.update(self.name, dict(entrypoints=val))

    def call_delete_one_entrypoint(self, domain, port, protocol):
        """remove backend by entrypoint domain, port, protocol"""
        for entrypoint in self.entrypoints:
            if (entrypoint.get('domain', None) == domain and
                    entrypoint.get('port', 0) == port and
                    protocol.get('protocol', None) == protocol):
                self.entrypoints.remove(entrypoint)
        return self.update(self.name, dict(entrypoints=self.entrypoints))

    def call_delete_all_entrypoints(self, val):
        """remove all entrypoints"""
        return self.update(self.name, dict(entrypoints=[]))

    def functions(self, func):
        __functions = {
            'update_frontend': self.call_update_frontend,
            'add_backends': self.call_add_backends,
            'update_backends': self.call_update_backends,
            'delete_backend_by_cid': self.call_delete_backend_by_cid,
            'delete_backend_by_addr_port': self.call_delete_backend_by_addr_port,
            'delete_backend_by_tag': self.call_delete_backend_by_tag,
            'add_entrypoints': self.call_add_entrypoints,
            'update_entrypoints': self.call_update_entrypoints,
            'delete_one_entrypoint': self.call_delete_one_entrypoint,
            'delete_all_entrypoints': self.call_delete_all_entrypoints,
        }
        return __functions[func]

    @classmethod
    def save_balancer(cls, val):
        val['frontend']['port'] = allocated_port()
        return cls.save(val)
