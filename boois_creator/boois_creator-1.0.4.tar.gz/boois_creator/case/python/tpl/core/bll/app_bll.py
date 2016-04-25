#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import uuid

from core.info.{{top_obj_name}}.{{obj.name}}_info import {{obj.name_cap}}Info
from core.info.{{top_obj_name}}.img_info import ImgInfo
from core.adapter.{{top_obj_name}}.{{obj.name}}_adapter import {{obj.name_cap}}Adapter
from core.bll.{{obj.name}}_bll import {{obj.name_cap}}Bll


class {{obj.name_cap}}AppBll(object):
    @staticmethod
    def get_list(app_key, app_token):
        '''
        获取当前应用下的所有的{{obj.comment}},用来做总的{{obj.comment}}权限管理
        :param app_key:
        :param app_token:
        :return: {{obj.name_cap}}Info[]
        '''
        # 这里要验证app_key, app_token
        return {{obj.name_cap}}Bll.get_list_by_app_key(app_key)
        pass

    @staticmethod
    def get_list_by_user_id(app_key, app_token, user_id):
        '''
        根据user_id来获取货品资料,用来获取当前应用下的所有的{{obj.comment}},通常用来做总的{{obj.comment}}权限管理
        :param app_key:
        :param app_token:
        :param user_id:
        :return: {{obj.name_cap}}Info[]
        '''
        return {{obj.name_cap}}Bll.get_list_by_app_key(app_key)
        pass

    @staticmethod
    def add_{{obj.name}}(app_key, app_token, user_id=""):
        '''
        添加一个{{obj.comment}},可以不填user_id,没有user_id都可以认为是管理员添加
        :param app_key: 必填的应用key
        :param app_token: 必填的应用token
        :param user_id: 选填归属用户id,不填的时候认为是管理员添加的
        :return: True|False
        '''
        pass

    @staticmethod
    def del_by_{{obj.name}}_id_list(app_key, {{obj.name}}_id_list=[]):
        '''
        根据id删除{{obj.comment}}
        :param app_key: 必填的应用key
        :param {{obj.name}}_id_list: {{obj.comment}}id
        :return: True|False
        '''
        pass

    # 暂时不提供清空功能,也不提供按user_id清空功能,可以找出所有的{{obj.comment}}的id,然后用id_list删除