# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import itertools

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.config import CONFIGURATION
import os
from tcell_agent.sensor_events import HttpTxSensorEvent, FingerprintSensorEvent, LoginSuccessfulSensorEvent, LoginFailureSensorEvent
from tcell_agent.sensor_events import RedirectSensorEvent
from tcell_agent.sensor_events import ServerAgentDetailsEvent
from .settings import send_django_setting_events
import uuid
import re

from tcell_agent.sanitize import SanitizeUtils

from future.backports.urllib.parse import urlsplit
from future.backports.urllib.parse import urlunsplit
from future.backports.urllib.parse import parse_qs
_started = False
from .routes import make_route_table
from tcell_agent.instrumentation.django.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation import BaseWrapper
from tcell_agent.instrumentation.manager import InstrumentationManager

from tcell_agent.appsensor.django import django_meta
from tcell_agent.policies.appsensor.sensor import sendEvent


from logging import Logger
try:
    from django.db.models.expressions import Col
    col_supported = True
except:
    col_supported = False
from collections import defaultdict

from .. import safe_wrap_function

import logging
logger = logging.getLogger('tcell_agent').getChild(__name__)

def check_max_database_rows_reached(request, total_records):
    if total_records > CONFIGURATION.max_data_ex_db_records_per_request:
        appsensor_meta = django_meta(request)
        sendEvent(appsensor_meta, "dbmaxrows", None, {"rows": total_records})


def singlecallback(row, track_idxes, request, count):
    if count < CONFIGURATION.max_data_ex_db_records_per_request:
        if track_idxes is not None:
            for track_idx in track_idxes:
                actions, db_identifier,schema_identifier,table, column = track_idxes[track_idx]
                for action in actions:
                    try:
                        request._tcell_context.add_response_db_filter(row[track_idx], action, db_identifier, schema_identifier, table, column)
                    except Exception as e:
                        print(e)
                        pass

    return row

def multicallback2(rows, track_idxes, request, i):
    number_of_rows = len(rows)
    j = i * number_of_rows - 1
    for row in rows:
        j += 1
        singlecallback(row, track_idxes, request, j)

    return number_of_rows

def multicallback(results, track_idxes, request):
    results, results2 = itertools.tee(results)
    total_records = 0
    for counter, rows in enumerate(results):
        total_records += multicallback2(rows, track_idxes, request, counter)

    safe_wrap_function(
        "Check max number of DB records",
        check_max_database_rows_reached,
        request,
        total_records
    )

    return results2

# class CursorTCellWrapper(BaseWrapper):
#     def __init__(self, instance):
#         self.cursor = instance.cursor
#         self.db = instance.db
#         super(CursorTCellWrapper,self).__init__(instance)

#     WRAP_ERROR_ATTRS = frozenset(['fetchone', 'fetchmany', 'fetchall', 'nextset'])

#     def __getattr__(self, attr):
#         print("AXY")
#         print(attr)

#         cursor_attr = getattr(self.cursor, attr)
#         if attr in CursorTCellWrapper.WRAP_ERROR_ATTRS:
#             results = self.db.wrap_database_errors(cursor_attr)
#         else:
#             results = cursor_attr
#         print(results)
#         return results

#     def __iter__(self):
#         with self.db.wrap_database_errors:
#             for item in self.cursor:
#                 yield item

#     def __enter__(self):
#         return self

#     def __exit__(self, type, value, traceback):
#         # Ticket #17671 - Close instead of passing thru to avoid backend
#         # specific behavior. Catch errors liberally because errors in cleanup
#         # code aren't useful.
#         try:
#             self.close()
#         except self.db.Database.Error:
#             pass

#     # The following methods cannot be implemented in __getattr__, because the
#     # code must run when the method is invoked, not just when it is accessed.

#     def callproc(self, procname, params=None):
#         print("proc")
#         self.db.validate_no_broken_transaction()
#         with self.db.wrap_database_errors:
#             if params is None:
#                 return self.cursor.callproc(procname)
#             else:
#                 return self.cursor.callproc(procname, params)

#     def execute(self, sql, params=None):
#         print("EONE")
#         print(type(sql).__name__)
#         self.db.validate_no_broken_transaction()
#         with self.db.wrap_database_errors:
#             if params is None:
#                 results = self.cursor.execute(sql)
#             else:
#                 results = self.cursor.execute(sql, params)
#             print(results)
#             print(self.cursor.description)
#             return results

#     def executemany(self, sql, param_list):
#         print("EMANY")
#         print(sql)
#         self.db.validate_no_broken_transaction()
#         with self.db.wrap_database_errors:
#             results = self.cursor.executemany(sql, param_list)
#             return results

    # def fetchmany(self, *args):
    #     print("EXECUTE")
    #     results = self._instance.fetchmany(*args)
    #     print("--")
    #     print(self._instance.description)
    #     print("**")
    #     print(results)
    #     return results

    #def __iter__(self):
    #    print("ITER")
    #    print(self._instance.description)
    #    for item in self._instance.__iter__():
    #        print(item)
    #       yield item

def dlp_instrumentation():

    from django.db.models.sql.compiler import SQLCompiler
    from django.db.models.sql.constants import (
        CURSOR, GET_ITERATOR_CHUNK_SIZE, MULTI, NO_RESULTS, ORDER_DIR, SINGLE,
    )

    # from django.db.backends.base.base import BaseDatabaseWrapper
    # orig_get_cursor = BaseDatabaseWrapper.cursor
    # def get_cursor(self):
    #     print("Get Cursor")
    #     print(self)
    #     #return orig_get_cursor(self)
    #     return CursorTCellWrapper(orig_get_cursor(self))
    # BaseDatabaseWrapper.cursor = get_cursor

    # def _tcell_get_columns(self, with_aliases=False):
    #     print("yy")
    #     aliases = set(self.query.extra_select.keys())
    #     print(aliases)
    #     if with_aliases:
    #         col_aliases = aliases.copy()
    #     else:
    #         col_aliases = set()
    #     print(self.query)
    #     if self.query.select:
    #         print(self.query.select)
    #         only_load = self.deferred_to_columns()
    #         for col, _ in self.query.select:
    #             if isinstance(col, (list, tuple)):
    #                 alias, column = col
    #                 print(alias)
    #                 print(column)
    #                 table = self.query.alias_map[alias].table_name
    #                 print(table)
    #                 print("---")
    #                 if table in only_load and column not in only_load[table]:
    #                     continue
    #     elif self.query.default_cols:
    #         cols, new_aliases = self.get_default_columns(with_aliases,
    #                 col_aliases)
    #         print(cols)


    def _tcell_execute_sql(_tcell_original, self, result_type=MULTI):
        results = _tcell_original(self, result_type)
        try:
            #description = self.connection.cursor().description
            request = GlobalRequestMiddleware.get_current_request()
            dataloss_policy = TCellAgent.get_policy(PolicyTypes.DATALOSS)
            #db = self.connection.get_connection_params().get("db")
            #db_user = self.connection.get_connection_params().get("user","_")
            #db_host = self.connection.get_connection_params().get("hosta","_")
            #db_port = self.connection.get_connection_params().get("port","_")

            if hasattr(self.connection,"vendor"):
                db_vendor = self.connection.vendor
            else:
                db_vendor = "n/a"
            try:
                db_name = self.connection.get_connection_params().get("db","n/a")
            except:
                db_name = "n/a"

            db_identifier = db_vendor
            schema_identifier = db_name

            route_id = None
            if request:
                try:
                    route_id = request._tcell_context.route_id
                except:
                    pass

            if dataloss_policy:
                if col_supported:
                    if self.select:
                        try:
                            track_idxes = {}
                            tables_track = defaultdict(set)
                            for idx, select in enumerate(self.select):
                                try:
                                    if isinstance(select[0],Col):
                                       table = select[0].alias
                                       column = select[0].target.column
                                       tables_track[table].add(column)
                                       if results and request:
                                           actions = dataloss_policy.get_actions_for_db_field(db_identifier,schema_identifier,table,column, route_id)
                                           if (actions):
                                                track_idxes[idx] = (actions, db_identifier,schema_identifier,table, column)
                                except Exception as selectException:
                                    logger.debug(selectException)
                                    pass
                            for table in tables_track:
                                TCellAgent.discover_database_fields(db_identifier, schema_identifier, table, list(tables_track[table]), route_id)
                            if results and request and len(track_idxes.keys()) > 0:
                                if result_type == MULTI:
                                    return multicallback(results, track_idxes, request)
                                elif (result_type == SINGLE):
                                    return singlecallback(results, track_idxes, request, 0)
                        except Exception as b:
                            logger.error("error in data-exposure mapping.")
                            logger.debug(b)
                elif self.query.select:
                    try:
                        track_idxes = {}
                        only_load = self.deferred_to_columns()
                        idx = 0
                        tables_track = defaultdict(set)
                        for col, _ in self.query.select:
                            try:
                                if isinstance(col, (list, tuple)):
                                    table, column = col
                                    tables_track[table].add(column)
                                    if results and request:
                                        actions = dataloss_policy.get_actions_for_db_field(db_identifier,schema_identifier,table,column, route_id)
                                        if (actions):
                                            track_idxes[idx] = (actions, db_identifier,schema_identifier,table, column)
                            except Exception as selectException:
                                logger.debug(selectException)
                            finally:
                                idx = idx + 1
                        for table in tables_track:
                            TCellAgent.discover_database_fields(db_identifier, schema_identifier, table, list(tables_track[table]), route_id)
                        if results and request and len(track_idxes.keys()) > 0:
                            if result_type == MULTI:
                                return multicallback(results, track_idxes, request)
                            elif (result_type == SINGLE):
                                return singlecallback(results, track_idxes, request, 0)
                    except Exception as b:
                        logger.debug("error in data-exposure mapping.")
                        logger.debug(b)
                elif self.query.default_cols:
                    try:
                        track_idxes = {}
                        opts = self.query.get_meta()
                        start_alias = self.query.get_initial_alias()
                        seen_models = {None: start_alias}
                        idx = 0
                        tables_track = defaultdict(set)
                        for field, model in opts.get_concrete_fields_with_model():
                            try:
                                table = self.query.join_parent_model(opts, model, start_alias,
                                                                     seen_models)
                                column = field.column
                                tables_track[table].add(column)
                                if results and request:
                                    actions = dataloss_policy.get_actions_for_db_field(db_identifier,schema_identifier,table,column, route_id)
                                    if (actions):
                                        track_idxes[idx] = (actions, db_identifier,schema_identifier,table, column)
                            except Exception as selectException:
                                logger.debug(selectException)
                                pass
                            finally:
                                idx = idx + 1
                        for table in tables_track:
                            TCellAgent.discover_database_fields(db_identifier, schema_identifier, table, list(tables_track[table]), route_id)
                        if results and request and len(track_idxes.keys()) > 0:
                            if result_type == MULTI:
                                return multicallback(results, track_idxes, request)
                            elif (result_type == SINGLE):
                                return singlecallback(results, track_idxes, request, 0)
                    except Exception as b:
                        logger.debug("error in data-exposure mapping.")
                        logger.debug(b)
        except Exception as wrapping_exception:
            logger.debug(wrapping_exception)
            logger.debug("Could not complete data-exposure mapping.")
        return results
    InstrumentationManager.instrument(SQLCompiler, "execute_sql", _tcell_execute_sql)

    def _tcell_log(_tcell_original, self, level, msg, args, exc_info=None, extra=None):
        # Skip us...
        if (self.name and self.name.startswith("tcell_agent")):
            return _tcell_original(self, level, msg, args, exc_info, extra)
        request = GlobalRequestMiddleware.get_current_request()
        if request:
            msg = request._tcell_context.filter_log_message(msg)
        return _tcell_original(self, level, msg, args, exc_info, extra)
    InstrumentationManager.instrument(Logger, "_log", _tcell_log)
