# -*- coding: utf-8 -*-
from congo.utils.search import escape_mysql_query
from watson.backends import MySQLSearchBackend

class MySQLAndSearchBackend(MySQLSearchBackend):
    def _format_query(self, search_text):
        return escape_mysql_query(search_text)

class MySQLOrSearchBackend(MySQLSearchBackend):
    def _format_query(self, search_text):
        return escape_mysql_query(search_text, default_operator = "")
