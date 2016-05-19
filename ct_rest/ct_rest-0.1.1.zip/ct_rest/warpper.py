# -*- coding:utf-8 -*-
import json
from django.http import HttpResponse


def REST(method = None, header=None, body=None):
    def _warpper(func):
        def __warpper(request):
            statusCode = None
            headerParams = {}
            bodyParams = {}
            errorInfo = []
            # 检查方法
            if method:
                if request.method != method or request.method not in method:
                    statusCode = "500"
                    errorInfo.append("方法传错了")
            # 处理头部信息
            for k, v in request.META.iteritems():
                if "HTTP_" in k:
                    headerParams[k.replace("HTTP_","").lower()] = v
            # 验证必须头部信息
            if header:
                for ins in header:
                    if ins not in headerParams.keys():
                        statusCode = "500"
                        errorInfo.append("你没传header必须参数"+str(ins))
            # 处理body信息
            if len(request.body) > 0:
                try:
                    for bodyPair in request.body.split("&"):
                        bodyParams[bodyPair.split("=")[0]] = bodyPair.split("=")[1]
                except Exception,e:
                    statusCode = "500"
                    errorInfo.append("请按照x-www-form-urlencoded格式化body参数, 比如:key1=value1&key2=value2, 然而你的body是"+body)
            # 验证必须body信息
            if body:
                for ins in body:
                    if ins not in bodyParams.keys():
                        statusCode = "500"
                        errorInfo.append("你没传body必须参数"+str(ins))
            # 按照UCore格式化输出
            if not statusCode:
                params = dict(headerParams, **bodyParams)
                toReturn = {"returnObj":func(request, params),"statusCode":"800","note":"此接口由ct-rest生成原型"}
            else:
                toReturn = {"statusCode":statusCode,"errorInfo":errorInfo,"note":"此接口由ct-rest生成原型"}
            return HttpResponse(json.dumps(toReturn))
        return __warpper
    return _warpper