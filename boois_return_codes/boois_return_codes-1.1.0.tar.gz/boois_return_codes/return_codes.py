# -*- coding: utf-8 -*-
# boois flask 框架,作者:周骁鸣 boois@qq.com
'''返回信息代码
错误分为5层:
系统级: 错误代码以 0x1 开头,英文信息以 sys 开头,如io错误,文件读写权限,socket错误等
数据库级: 错误代码以 0x2 开头,英文信息以 db 开头,如mysql数据连接,读写错误
业务级: 错误代码以 0x3 开头,英文信息以 bll 开头,业务上产生的错误
参数格式级: 错误代码以 0x4 开头,英文信息以 fmt 开头,请求参数不符合接口要求而产生的错误,缺少参数,格式错误
权限级: 错误代码以 0x5 开头,英文信息以 auth 开头,接口调用权限验证不通过时产生的错误
'''

class ReturnCodes():
    #成功

    ok=(0x00000001, "ok", "操作成功")
    input_val_err = (0x30000005, "input_val_err", "输入值没有通过检测!")


@staticmethod
def get_info_by_msg(msg):
    return ReturnCodes.__getattribute__(msg)
