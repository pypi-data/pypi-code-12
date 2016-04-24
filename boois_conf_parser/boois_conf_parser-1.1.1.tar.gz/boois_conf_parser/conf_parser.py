# coding:utf-8
'''


'''

def conf_parser(conf_str):
    """

    """
    conf_list = {}
    for conf in conf_str.split("\n"):
        conf = conf.strip()
        if not conf or conf.startswith("#"):
            continue
        conf = conf.split("#")[0]
        key = conf[0:conf.find("=")]
        val = conf[conf.find("=")+1:]
        conf_list[key] = val
    return conf_list


if __name__ == "__main__":
    print conf_parser("""
# 服务名称
title=图片服务
# 服务说明
desc=用来提供公共图片服务
# 服务密钥串
sec=2b77736accb941f2b43d5e28cbc0a186
# 允许使用当前服务的应用名称
allow=jiupin|boois|center|sg
# 服务的超级管理员账号
owner=jiupin.boois
# 管理员的user_id
owner_id=c5956c0919ff4d8da1b6262723649569
# 管理员的操作密码(与管理员原始的密码不同,用于高级授权,类似支付密码)
owner_oppsw=0000
""")
