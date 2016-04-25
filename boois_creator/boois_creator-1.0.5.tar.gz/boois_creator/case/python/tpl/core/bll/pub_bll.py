#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import uuid

from core.info.{{top_obj_name}}.{{obj.name}}_info import {{obj.name_cap}}Info
from core.info.{{top_obj_name}}.img_info import ImgInfo
from core.adapter.{{obj.name}}.{{obj.name}}_adapter import {{obj.name_cap}}Adapter
from core.dal.{{obj.name}}_dal import {{obj.name_cap}}Dal
from utils.search_str_parser import SearchAdapter, SortItemInfo


class {{obj.name_cap}}PubBll(object):
    @staticmethod
    def get_list(app_key, serach_condition_str="", page_size=10, page=1):
        '''
        根据app_key来获取公共资料,用搜索条件来获取当前应用下的所有{{obj.comment}},
        :param app_key:
        :param serach_condition_str: &s.field.1=condition_str
        有以下几种形式(用了四种判定符各自组合:!,*,~,=):
        1.以！开头的表示否
        &s.field = !abc => field <> abc
        &s.field =!*abc* => field not like '%abc%'
        &s.field = !*abc => field not like '%abc'
        &s.field = !abc* => field not like 'abc%'
        &s.field = !~1,2,3~ =>相当于not in(...),实际将转化为 field<>1 or field<>2 or filed<>3
        2.以波浪线为范围的
        &s.field = 2016-1-1 1:1:1~~2016-1-1 1:1:1 => field between '2016-1-1 1:1:1' and '2016-1-1 1:1:1' 用于时间
        &s.field = ~1~ or ~1,2,3~ => 相当于in(...),实际将转化为 field=1 or field=2 or filed=3
        &s.field = ~1 => field<1 小于
        &s.field = ~=1 => field<=1 小于等于
        &s.field = 1~ => field>1 大于
        &s.field = 1=~ => field>1 大于等于
        &s.field = 0~1 => field<0 and field>1
        &s.field = 0=~=1 => field>=0 and field<=1
        &s.field = 0~=1 => field>0 and field=<1
        &s.field = 0=~1 => field>=0 and field<1
        3.带星号通配符的
        &s.field = *abc* => field like '%abc%'
        &s.field = abc* => field like 'abc%'
        &s.field = *abc => field like '%abc'
        4.什么都没有的
        &s.field = abc  => field = abc
        :return: {{obj.name_cap}}Info[]
        '''
        sa = SearchAdapter(serach_condition_str)
        return {{obj.name_cap}}Dal.get_list(sa.where_str, sa.mapping, page_size=page_size, page=page, sort_field=sa.sorts[-1].field if len(sa.sorts)!=0 else "id",
                                is_asc=sa.sorts[-1].sort_type == SortItemInfo.ASC if len(sa.sorts)!=0 else True,except_field_list=[{{obj.name_cap}}Info.F_USER_ID_NAME])

    @staticmethod
    def get_by_{{obj.name}}_id(app_key, {{obj.name}}_id):
        '''
        根据 {{obj.name}}_id 获取单个{{obj.comment}}资料
        :param app_key:
        :param {{obj.name}}_id:
        :return:
        '''
        list, count = {{obj.name_cap}}PubBll.get_list("", "s.{{obj.name}}_id=%s" % {{obj.name}}_id, page_size=1, page=1)
        if count == 0:
            return None
        else:
            return list[0]

    @staticmethod
    def get_category_list(app_key,parent_category_id=0):
        '''
        获取当前应用的公共的分类
        :param app_key:
        :param parent_category_id:
        :return:
        '''
        return ""

    @staticmethod
    def get_list_by_category(app_key,category_id, page_size=10, page=1):
        '''
        获取当前应用的公共的分类
        :param app_key:
        :param category_id:
        :param page_size:
        :param page:
        :return:
        '''
        return {{obj.name_cap}}PubBll.get_list("", "s.category_id=%s" % category_id, page_size=1, page=1)

    @staticmethod
    def get_list_by_tag(app_key,tag_name, page_size=10, page=1):
        '''
        通过当tag的名称获取{{obj.comment}}列表,暂时是用like来实现,后续会用索引的方式实现  # TODO
        :param app_key:
        :param tag_name:
        :param page_size:
        :param page:
        :return:
        '''
        return {{obj.name_cap}}PubBll.get_list("", "s.tag_list=*%s*" % tag_name, page_size=1, page=1)


if __name__ == "__main__":
    # {{obj.name_cap}}PubBll.get_list("", "s.{{obj.name}}_id=*16813cf26074409c9ef73349b5ddd7af*&st.id=1")
    print {{obj.name_cap}}PubBll.get_list_by_tag("", "特别")
