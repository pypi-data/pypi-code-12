#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
from utils.json_encoder import JsonEncoder
{%for x in obj.fields-%}
{% if x.cls_file-%}
from core.adapter.{{top_obj_name}} import {{x.cls_file}}_adapter
from core.info.{{top_obj_name}} import {{x.cls_file}}_info
{%endif%}
{%-endfor%}
from core.info.{{top_obj_name}} import {{obj.name}}_info
class {{obj.name_cap}}Adapter(object):

    # region info
    def get_info(self):
        return self._info
    def set_info(self, info):
        self._info = info
    info = property(fget = get_info,fset = set_info)
    # endregion
    def __init__(self,info = None):
        if info is not None:
            # self.set_info(info)
            self.set_info(info)
        else:
            self.set_info({{obj.name}}_info.{{obj.name_cap}}Info())
    # region arr
    def dump_arr(self):
        res={}
        {%for x in obj.fields%}
        if {{obj.name}}_info.{{obj.name_cap}}Info.{{x.name_field_name}} in self._info.changed_fields:
            res[{{obj.name}}_info.{{obj.name_cap}}Info.{{x.name_field_name}}]={{x.dump_arr_stm}}
        {%-endfor%}
        return res
    def load_arr(self, arr):
        {%for x in obj.fields-%}
        {{x.load_arr_stm2}}
        {%endfor%}
        return self
    arr = property(fget = dump_arr)
    # endregion
    # region json
    def dump_json(self):
        return json.dumps(self.dump_arr(), ensure_ascii = False, cls=JsonEncoder)
    def load_json(self,str):
        try:
            arr = json.loads(str)
            self.load_arr(arr)
            return self
        except ValueError,e:
            raise ValueError("json字符串格式错误,%s,json str : %s " % (e,str))
    json = property(fget = dump_json)
    # endregion
    # region mysql_data
    def dump_mysql_data(self):
        res={}
        {%for x in obj.fields%}
        if {{obj.name}}_info.{{obj.name_cap}}Info.{{x.name_field_name}} in self._info.changed_fields:
            res[{{obj.name}}_info.{{obj.name_cap}}Info.{{x.name_field_name}}]={{x.dump_mysql_data_stm}}
        {%-endfor%}
        return res

    def load_mysql_data(self,arr):
        {%for x in obj.fields-%}

        {{x.load_mysql_data_stm2}}
        {%endfor%}
        return self
    mysql_data = property(fget = dump_mysql_data)
    # endregion
    # region mongodb_data
    def dump_mongodb_data(self):
        return self.arr
    def load_mongodb_data(self, arr):
        self.load_arr(arr)
        return self

    mongodb_data = property(fget = dump_mongodb_data)
    # endregion
    # region file_data
    def dump_to_file(self, filename):
        with open(filename,"wb") as f:
            f.write(self.json)
    def load_from_file(self, filename):
        with open(filename, "r") as f:
            self.load_json(f.read())
        return self
    # endregion
    # region mysql struct
    def get_mysql_struct(self):
        return '''{{obj.mysql_create_sql}}'''
    mysql_struct = property(fget = get_mysql_struct)
    # endregion


