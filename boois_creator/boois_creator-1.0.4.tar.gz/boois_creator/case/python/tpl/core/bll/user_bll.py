#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import uuid

from core.info.{{top_obj_name}}.goods_info import {{obj.name_cap}}Info
from core.info.{{top_obj_name}}.img_info import ImgInfo
from core.adapter.{{obj.name}}.{{obj.name}}_adapter import {{obj.name_cap}}Adapter
from core.dal.{{obj.name}}_dal import {{obj.name_cap}}Dal

class {{obj.name_cap}}UserBll(object):

    @staticmethod
    def get_list_by_app_key(app_key, app_token):
        '''
        根据app_key来获取{{obj.comment}}资料,用来获取当前应用下的所有的{{obj.comment}},通常用来做总的{{obj.comment}}权限管理
        :param app_key:
        :param app_token:
        :return: {{obj.name_cap}}Info[]
        '''
        pass

    @staticmethod
    def get_list_by_user_id(user_id):
        '''
        根据user_id来获取{{obj.comment}}资料,用来获取当前应用下的所有的{{obj.comment}},通常用来做总的{{obj.comment}}权限管理
        :param app_key:
        :return: {{obj.name_cap}}Info[]
        '''
        pass

    @staticmethod
    def add_{{obj.name}}(app_key,user_id=""):
        '''
        添加一个{{obj.comment}},如果不填user_id则认为是管理员添加
        :param app_key: 必填的应用key
        :param user_id: 选填归属用户id,不填的时候认为是管理员添加的
        :return: True|False
        '''
        pass

    @staticmethod
    def del_{{obj.name}}(app_key,user_id=""):
        '''
        添加一个{{obj.comment}},如果不填user_id则认为是管理员添加
        :param app_key: 必填的应用key
        :param user_id: 选填归属用户id,不填的时候认为是管理员添加的
        :return: True|False
        '''
        pass
