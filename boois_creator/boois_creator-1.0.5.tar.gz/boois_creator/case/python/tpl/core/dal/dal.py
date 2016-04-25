#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import uuid
from core.info.{{top_obj_name}}.{{obj.name}}_info import {{obj.name_cap}}Info
from core.info.{{top_obj_name}}.img_info import ImgInfo
from core.adapter.{{obj.name}}.{{obj.name}}_adapter import {{obj.name_cap}}Adapter
from utils.mysql_db_helper import DbHelper
from conf import DB_INFO


class {{obj.name_cap}}Dal(object):
    def __init__(self):
        pass

    @staticmethod
    def add({{obj.name}}_info):
        if not {{obj.name}}_info.app_key:
            raise ValueError(u"{{obj.name}}_info必须设定app_key,否则无法插入数据库!")
        if not {{obj.name}}_info.{{obj.name}}_id:
            {{obj.name}}_info.{{obj.name}}_id = uuid.uuid4().__str__().replace("-", "")
        if not {{obj.name}}_info.title:
            raise ValueError(u"{{obj.name}}_info必须设定title,否则无法插入数据库!")
        sql, mapping = {{obj.name_cap}}Dal.get_insert_sqlstr({{obj.name}}_info)
        DbHelper.execute_non_query(sql, mapping, db_info=DB_INFO)

    @staticmethod
    def reset({{obj.name}}_info):
        if not {{obj.name}}_info.{{obj.name}}_id:
            raise ValueError(u"{{obj.name}}_info必须设定{{obj.name}}_id,否则无法插入数据库!")
        if not {{obj.name}}_info.title:
            raise ValueError(u"{{obj.name}}_info必须设定title,否则无法插入数据库!")
        # {{obj.name}}_info.del_changed_field({{obj.name_cap}}nfo.F_APP_KEY_NAME)
        sql, mapping = {{obj.name_cap}}Dal.get_update_sqlstr({{obj.name}}_info)
        DbHelper.execute_non_query(sql, mapping, db_info=DB_INFO)

    @staticmethod
    def get_list(where_str="",mapping=(), page=1, page_size=10, is_asc=True, sort_field="",except_field_list=[]):
        list = []
        adapter = {{obj.name_cap}}Adapter()

        def each_fn(data):
            adapter.info = {{obj.name_cap}}nfo()
            adapter.load_mysql_data(data)
            for field in except_field_list:
                adapter.info.__setattr__(field,None)
                adapter.info.del_changed_field(field)

            list.append(adapter.info)

        if sort_field:
            sort_str = "%s %s" %(sort_field,"ASC" if is_asc else "DESC")
        else:
            sort_str = ""

        return list, DbHelper.paging(where_str=where_str,mapping=mapping, tab_name="{{obj.name}}", page_size=page_size, current_page=page,
                                     each_fn=each_fn, sort_str=sort_str, db_info=DB_INFO)


    @staticmethod
    def del_by_{{obj.name}}_id_list({{obj.name}}_id_list):
        if not isinstance({{obj.name}}_id_list,type(list)):
            raise ValueError("{{obj.name}}_id_list必须是一个数组")
        if len({{obj.name}}_id_list) == 0:
            return True
        return DbHelper.execute_non_query("DELETE FROM {{obj.name}} Where "+ " OR ".join(["{{obj.name}}_id=%s" for x in {{obj.name}}_id_list]),tuple({{obj.name}}_id_list),db_info=DB_INFO)


    @staticmethod
    def get_by_{{obj.name}}_id({{obj.name}}_id):
        if not {{obj.name}}_id:
            raise ValueError("调用get_by_{{obj.name}}_id方法必须指定{{obj.name}}_id")
        list,count = {{obj.name_cap}}Dal.get_list("{{obj.name}}_id=%s",({{obj.name}}_id,),1,1)
        if len(list)!=0:
            return list[0]
        else:
            return None

    @staticmethod
    def get_insert_sqlstr({{obj.name}}_info):
        adapter = {{obj.name_cap}}Adapter({{obj.name}}_info)
        return "INSERT INTO {{obj.name}} (" + ",".join(adapter.mysql_data.keys()) + ") VALUES (" + ",".join(
                ["%s" for x in range(len(adapter.mysql_data))]) + ")", tuple(adapter.mysql_data.values())

    @staticmethod
    def get_update_sqlstr({{obj.name}}_info):
        if not {{obj.name}}_info.{{obj.name}}_id:
            raise ValueError(u"{{obj.name}}_info必须设定{{obj.name}}_id,否则无法更新数据库!")
        adapter = {{obj.name_cap}}Adapter({{obj.name}}_info)
        return "UPDATE {{obj.name}} SET " + ",".join(
                [k + "=%s" for k in adapter.mysql_data.keys()]) + " WHERE {{obj.name}}_id=%s", tuple(
            adapter.mysql_data.values() + [{{obj.name}}_info.{{obj.name}}_id])

    @staticmethod
    def create_db():
        adapter = {{obj.name_cap}}Adapter()
        DbHelper.execute_non_query(adapter.mysql_struct, (), db_info=DB_INFO)


if __name__ == "__main__":
    {{obj.name}}_info = {{obj.name_cap}}nfo()
    {{obj.name}}_info.app_key = "16813cf26074409c9ef73349b5ddd7af"
    {{obj.name}}_info.{{obj.name}}_id = "1d8f88c5295449339f3cb08a1a8eb754"
    {{obj.name}}_info.title = "title1"
    {{obj.name}}_info.img_list = [ImgInfo(title="图1"), ImgInfo(title="图2"), ImgInfo(title="图3")]
    # {{obj.name_cap}}Bll.reset({{obj.name}}_info)
    list, cnt = {{obj.name_cap}}Dal.get_list("app_key=%s",('tttc7f2a68ed4c319419333fb7a3c39d',))
    print [x.{{obj.name}}_id for x in list]
    print {{obj.name_cap}}Dal.get_by_{{obj.name}}_id("16813cf26074409c9ef73349b5ddd7af")
    #print {{obj.name_cap}}Dal.del_by_{{obj.name}}_id_list(["1d8f88c5295449339f3cb08a1a8eb754"])
