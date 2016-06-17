#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2016 Bruno PLANCHER (bruno.plancher@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################

import xmlrpclib
import time


class OdooITRPC(object):
    def __init__(self, env, db, user, pwd, debug=False, new_api=False):
        self.env = env
        self.db = db
        self.user = user
        self.pwd = pwd
        self.debug = debug
        self.model = False
        self.host = self.sock_common = self.sock_db = self.sock = self.uid = None
        self.get_connection_infos(new_api=new_api)

    def get_wkf_state(self, model, ids):
        ids = ids if isinstance(ids, list) else [ids]
        ret_ids = self.load('workflow.workitem').search([('inst_id.res_id', 'in', ids),
                                                    ('inst_id.res_type', '=', model)])
        ret = self.read(ret_ids, [])
        for item in ret:
            print item
        return ret

    def get_email_preview(self, record_id, template_id):
        self.load('email_template.preview')
        ret = self.on_change_res_id(False, record_id, {'template_id': template_id})
        return ret['value']['body_html']

    def get_connection_infos(self, new_api=False):
        self.host = self.env
        url = self.host + '/xmlrpc/'
        if new_api:
            url += '2/'
        self.sock_common = xmlrpclib.ServerProxy(url + 'common')
        self.sock_db = xmlrpclib.ServerProxy(url + 'db')
        self.uid = self.sock_common.login(self.db, self.user, self.pwd)
        self.sock = xmlrpclib.ServerProxy(url + 'object')

    def load(self, model):
        self.model = model
        return self

    def ping_db(self):
        dbnames = self.sock_db.list()
        for db in dbnames:
            print 'ping db %s on %s' % (db, self.host)
            self.sock_common.login(self.db, 'ping', 'ping')

    def execute(self, model, method, *args, **kwargs):
        current_time = time.time()
        if self.debug:
            args_str = ','.join([str(x) for x in args]) if args else ''
            kwargs_str = ','.join(['%s= %s' % (x, kwargs.get(x)) for x in kwargs.keys()]) if kwargs else ''
            print '[%s] executing "%s(%s,%s)"' % (model, method, args_str, kwargs_str)
        ret = self.sock.execute_kw(self.db, self.uid, self.pwd, model, method, args, kwargs)
        if self.debug:
            print 'Done in %s sec' % str(time.time() - current_time)
        return ret

    def call(self, method, *args, **kwargs):
        assert self.model, 'Error: You have not loaded any model, use load() method before calling call()'
        return self.execute(self.model, method, *args, **kwargs)

    # if calls unidentified attribute, we suppose an xmlrpc call is expected
    def __getattr__(self, name):
        if name not in self.__dict__.keys():
            def func_proxy(*args, **kwargs):
                return self.call(name, *args, **kwargs)
            return func_proxy
        return self.__dict__.get(name)
