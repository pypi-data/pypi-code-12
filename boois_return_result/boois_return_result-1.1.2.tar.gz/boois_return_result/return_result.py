# -*- coding: utf-8 -*-
# boois flask 框架,作者:周骁鸣 boois@qq.com
'''返回信息代码

'''
import json
import conf
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from application.utils.return_codes import ReturnCodes


class ReturnResult(object):
    def __init__(self, return_code, info=None,result=None,debug=""):
        self.return_code = return_code
        self.result = result
        self.debug = debug
        self.code, self.msg, self.info = return_code
        if info :
            self.info=info
        self._json = None

    def is_code(self, code):
        return self.code == code

    def is_msg(self, msg):
        return self.msg == msg

    def _is_ok(self):
        return self.is_code(ReturnCodes.ok)

    def _is_failed(self):
        return not self.is_code(ReturnCodes.ok)

    def _encode_json(self):
        if self._json is None:
            self._json = '''{"code":"%s","msg":"%s","info":"%s","result":%s, "debug":"%s"}''' % (
                '{:0>8}'.format(conf.DOMAIN_PORT)+""+'{:0>8}'.format(self.code),
                self.msg,
                self.info,
                json.dumps(self.result,ensure_ascii=False,indent=1),
                self.debug
            )
        return self._json

    json = property(fget=_encode_json)
    is_ok = property(fget=_is_ok)
    is_failed = property(fget=_is_failed)
