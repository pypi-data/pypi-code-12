#coding:utf-8

import os
import json
import traceback
from base import BaseService

__author__ = 'lufeng'


class CMDBService(BaseService):
    """
    cmdb客户端链接工具
    """

    def get_email(self, um):
        emails = set([])
        result = self.get_resource("entity/search", {"schema": "user", "q": "attributes.um:%s" % um})
        if result.get("success"):
            for res in result["data"]["content"]:
                email = res.get("attributes", {}).get("email")
                for e in email:
                    if e:
                        emails.add(e)
        return list(emails)

    def get_department(self, um):
        """
        department
        :param um:
        :return:
        """
        if not um:
            return ''
        result = self.get_resource("entity/search", {"schema": "user", "q": "attributes.um:%s" % um})
        if result.get("success") and result["data"]["content"]:
            entity = result["data"]["content"][0]
            attr = entity.get("attributes", {})
            return attr.get("department", '')
        else:
            return ''

    def get_department_users(self, um):
        """
        获取部门用户列表
        :param um:
        :return:
        """
        users = set([])
        department = self.get_department(um)
        if not department:
            return list(users)
        result = self.get_resource("entity/search", {"schema": "user", "q": u"attributes.department:%s" % department})
        if result.get("success") and result["data"]["content"]:
            for ent in result["data"]["content"]:
                users.add(ent["attributes"]["um"])
        return list(users)

    def get_contact(self, um):
        """
        获取姓名和联系电话
        :param um:
        :return:
        """
        phone = set([])
        result = self.get_resource("entity/search", {"schema": "user", "q": "attributes.um:%s" % um})
        if result.get("success") and result["data"]["content"]:
            entity = result["data"]["content"][0]
            attr = entity.get("attributes", {})
            for p in attr.get("phone", []):
                if p:
                    phone.add(p)
            user = {
                "name": attr.get("name"),
                "phone": list(phone)
            }
            return user
        else:
            return None

    def get_name(self, um):
        """

        """
        if not um:
            return ''
        result = self.get_resource("entity/search", {"schema": "user", "q": "attributes.um:%s" % um})
        if result.get("success") and result["data"]["content"]:
            entity = result["data"]["content"][0]
            attr = entity.get("attributes", {})
            return attr.get("name", '')
        else:
            return ''

    def get_minions(self, um):
        """
        获取直接下属列表
        :param um:
        :return:
        """
        return []

    def is_op(self, um):
        """
        获取直接下属列表
        :param um:
        :return:
        """
        return False