# coding:utf-8
'''
本模块用于输入参数的合法性
'''
from functools import wraps

from core.utils.return_codes import ReturnCodes
from core.utils.return_result import ReturnResult
from utils.vali_rule_chker import ValiRuleChker
from flask import request



class InputValidation(object):
    GET = 1 << 0  # 0001
    POST = 1 << 1  # 0010

    # 有GET权限  GET&vali_type   0001 & 1000 = 0000 等于零则没有全新啊
    # 有POST权限  GET&vali_type   0010 & 1110 = 0010 大于零则有权限

    @staticmethod
    def validation(vali_type, *rules):
        '''
        使用方法：在方法前加装饰器,然后在方法参数中加上您自己设置的field参数
        @InputValidation.validation(
        InputValidation.GET|InputValidation.POST,
            r'     field -n -l 1,4 -r "/^1$/gi" -i test%s123123 -t +int|-float     ',
        )
        def foo(field="")
        :param vali_type:
        :param rules: filed -n 0 -l 1,4 -r /mobi/gi -i test%s123123 -t +int|-float
        :return:
        '''
        if not isinstance(vali_type, int):
            raise ValueError("InputValidation.validation的第一个参数必须是InputValidation.GET|InputValidation.POST形式")

        def _input_validation(function):
            @wraps(function)
            def wrap_function(*args, **kwargs):
                val_list = {}
                for rule in rules:  # 逐个读取rule
                    chker = ValiRuleChker(rule)
                    if vali_type == InputValidation.GET | InputValidation.POST:
                        val = request.form.get(chker.field) or request.args.get(chker.field)
                    else:
                        if InputValidation.GET & vali_type > 0:  # 如果是GET
                            val = request.args.get(chker.field)
                        if InputValidation.POST & vali_type > 0:
                            val = request.form.get(chker.field)
                    msg, info = chker.chk(val)
                    if not chker.is_validated:
                        return ReturnResult(ReturnCodes.input_val_err, info=info).json
                    else:
                        val_list[chker.field] = val
                print kwargs
                return function(*args, **dict(val_list,**kwargs))

            return wrap_function

        return _input_validation
