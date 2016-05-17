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

    ok=(1, "ok", "操作成功")
    input_val_err = (2, "input_val_err", "输入值没有通过检测!")
    # 失败
    failed = (3, "failed", "操作失败")
    err = (4, "err", "发生错误")
    empty=(5,"empty","不能为空")
    exists=(6,"exists","已经存在")
    no_exists=(7,"no_exists","不存在")

    # 系统
    sys_io_err = (8, "sys_io_err", "io错误")
    sys_cfg_err = (9, "sys_cfg_err", "系统配置错误")
    third_party_err = (10, "third_party_err", "调用第三方失败")

    # 数据库
    db_err = (11, "db_err", "数据库错误")
    # 业务
    # 参数格式
    fmt_empty = (12, "fmt_empty", "不能为空")
    fmt_int_err = (13, "fmt_int_err", "不是整数")
    fmt_float_err = (14, "fmt_float_err", "不是小数")
    fmt_json_err = (15, "fmt_json_err", "不是json格式的字符串")
    fmt_guid_err = (16, "fmt_guid_err", "不是32位无横线guid格式的字符串")
    fmt_err = (17, "fmt_err", "格式错误")

    # 权限
    app_key_empty = (18, "app_key_empty", "app_key不能为空!")
    app_key_err = (19, "app_key_err", "app_key错误")

    app_token_empty = (20, "app_token_empty", "app_token不能为空!")
    app_token_err = (21, "app_token_err", "app_token验证失败!")

    app_sec_empty = (22, "app_sec_empty", "app_sec不能为空!")
    app_sec_err = (23, "app_sec_err", "app_sec验证失败!")


    psw_err = (24, "psw_err", "密码错误")
    psw_empty = (25, "psw_empty", "密码不能为空")
    psw_fmt_err = (26, "psw_fmt_err", "密码格式错误")
    user_id_empty = (27, "user_id_empty", "user_id不能为空")
    user_id_err = (28, "user_id_err", "user_id错误")
    user_id_fmt_err = (29, "user_id_fmt_err", "user_id格式错误")
    user_token_empty = (30, "user_token_empty", "user_token不能为空")
    user_token_err = (31, "user_token_err", "user_token错误")
    user_token_fmt_err = (32, "user_token_fmt_err", "user_token格式错误")
    no_cache = (33, "no_cache", "没有找到缓存,用户未登录")
    account_empty = (43, "account_empty", "账号不能为空")
    account_fmt_err = (35, "account_fmt_err", "账号格式错误")
    account_err = (36, "account_err", "账号错误")
    len_err = (37, "len_err", "长度错误")
    regex_err = (38, "regex_err", "没有通过格式检查")
    account_exists = (39, "account_exists", "账号已经存在")
    id_empty = (40, "id_empty", "id不能为空")
    id_err = (41, "id_err", "id错误")
    token_empty = (42, "token_empty", "token不能为空")
    token_err = (43, "token_err", "token错误")
    sec_empty = (47, "sec_empty", "sec不能为空")
    sec_err = (48, "sec_err", "sec错误")


@staticmethod
def get_info_by_msg(msg):
    return ReturnCodes.__getattribute__(msg)
