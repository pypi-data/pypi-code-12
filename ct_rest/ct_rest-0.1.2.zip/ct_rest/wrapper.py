# -*- coding:utf-8 -*-
import json, urllib
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.db import connection


def REST(method = None, header=None, body=None):
    def _warpper(func):
        def __warpper(request):
            '''
            实际操作函数
            Args:
                request:
            Returns:
            '''
            def check(rule, ins):
                '''
                规则检查
                Args:
                    rule:
                    规则, 例如:
                    {
                        "username":{
                            "length":5-20,
                            "type":"str"
                        },
                        "password":{
                            "type":"int"
                        },
                        "phone":{
                            "required":False
                        }
                    }
                    ins:
                    检查实例
                Returns:
                    错误信息
                '''
                errorInfo = []
                for k,v in rule.iteritems():
                    if v.get("default") and k not in ins.keys():
                        ins[k] = v["default"]
                        continue
                    if v.get("required") != False and k not in ins.keys():
                        errorInfo.append(u"你没传必须参数"+str(k))
                        continue
                    if v.get("length"):
                        [minLength, maxLength] = v["length"].split("-")
                        if len(ins[k]) > int(maxLength) or len(ins[k]) < int(minLength):
                            errorInfo.append(u"参数%s限制长度为%s"%(k, v["length"]))
                    if v.get("type"):
                        if v["type"] == "int":
                            try:
                                ins[k] = int(ins[k])
                            except Exception, e:
                                errorInfo.append(u"参数%s转为类型%s时出错, 错误为%s" %(k, str(int), str(e)))
                        elif v["type"] == "str":
                            try:
                                ins[k] = str(ins[k])
                            except Exception, e:
                                errorInfo.append(u"参数%s转为类型%s时出错, 错误为%s" %(k, str(str), str(e)))
                        elif v["type"] == "json":
                            try:
                                ins[k] = json.loads(ins[k])
                            except Exception, e:
                                errorInfo.append(u"参数%s转为类型%s时出错, 错误为%s" %(k, "json", str(e)))
                    if v.get("lambda"):
                        result = True
                        try:
                            result = v["lambda"](ins[k])
                        except Exception, e:
                            errorInfo.append(u"匿名函数执行出错, 错误为%s" %(str(e)))
                        if not result:
                            errorInfo.append(u"匿名函数执行结果为假")
                return errorInfo

            headerParams = {}
            bodyParams = {}
            errorInfo = []
            # 检查方法
            if method:
                if request.method != method or request.method not in method:
                    errorInfo.append(u"方法传错了")
                # 如果不传method, 则不进行任何检查.
                # 处理头部信息
                for k, v in request.META.iteritems():
                    if "HTTP_" in k:
                        headerParams[k.replace("HTTP_","").lower()] = v
                # 验证必须头部信息
                if header:
                    errorInfo.extend(check(header, headerParams))
                # 处理body信息
                if len(request.body) > 0:
                    try:
                        for bodyPair in request.body.split("&"):
                            bodyParams[bodyPair.split("=")[0]] = urllib.unquote(bodyPair.split("=")[1])
                    except Exception,e:
                        errorInfo.append(u"请按照x-www-form-urlencoded格式化body参数, 比如:key1=value1&key2=value2, 然而你的body是%s"%request.body)
                # 验证必须body信息
                if body:
                    errorInfo.extend(check(body, bodyParams))
            # 按照UCore格式化输出
            if len(errorInfo)==0:
                try:
                    with transaction.atomic():
                        toReturn = {"returnObj": func(request, {"header":headerParams, "body":bodyParams}),"statusCode":800,"note":u"此接口由ct-rest生成原型"}
                    qs = connection.queries
                    if len(qs) > 0:
                        for q in qs:
                            if float(q["time"]) > 1:
                                print q # FIXME log this sql
                except Exception,e:
                    toReturn = {"statusCode":400,"viewError":str(e),"note":u"此接口由ct-rest生成原型"}
            else:
                toReturn = {"statusCode":400,"checkError":errorInfo,"note":u"此接口由ct-rest生成原型"}
            return HttpResponse(json.dumps(toReturn))
        return __warpper
    return _warpper