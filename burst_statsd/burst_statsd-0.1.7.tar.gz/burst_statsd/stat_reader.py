# -*- coding: utf-8 -*-
"""
读取gateway统计数据并解析
"""

import os
import re
import json


class StatReader(object):

    cmd = None

    def __init__(self, cmd):
        """
        :param cmd: 工具文件的路径
        :return:
        """

        self.cmd = cmd

    def read(self):
        """
        读取一次
        :return:
        """

        output = os.popen(self.cmd).read()
        str_json = re.search(r'{.*}', output, re.S).group()

        return json.loads(str_json)
