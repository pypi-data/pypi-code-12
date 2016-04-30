# coding: utf-8
"""
    pyextend.network.regex
    ~~~~~~~~~~~~~~~~~~~~
    pyextend network regex

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

__all__ = ['email_match', 'email_pattern']

import re

# 表达式,如果匹配成功 这返回Match对象,否则返回None
# bill.gates@microsoft.com
# 当匹配成功时,在第1,3组中分别存放着
# Email的名字 如 bill.gates,
# Email服务器 如 microsoft.com
email_pattern = r'(\w+([-.]\w+)*)@(\w+([-.]\w+)*\.\w+([-.]\w+)*)'


def email_match(string):
    """邮箱地址匹配. 匹配成功返回(email_name, email_server), 否则返回None"""
    m = re.match(email_pattern, string)
    if m:
        # print('Match success: %s' % m.string)
        return m.groups()[0], m.groups()[2]
    else:
        # print('Match failed: %s' % string)
        return None

if __name__ == '__main__':
    from pyextend.core import log

    L = ['someone@gmail.com',
         'bill.gates@microsoft.com',
         'bill.ga.tes@microsoft.com',
         'bill.gates@micro.soft.com',
         'bill.gates@micro..soft.com',
         'bill..gates@microsoft.com',
         ]
    for email in L:
        res = email_match(email)
        if res:
            log.debug('Match success: %s' % email)
            log.info('EmailName: %s, EmailServer: %s' % (res[0], res[1]))
        else:
            log.error('Match failed: %s' % email)
    log.info('Done.')
