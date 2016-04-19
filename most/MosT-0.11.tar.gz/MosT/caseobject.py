# -*- coding: utf-8 -*-
__author__ = 'tangke'


class CaseObject(object):
    # __slots__ = ('casename', 'description', 'class', 'method')
    def __str__(self):
        return '''
                    用例名:{casename}
                    用例描述:{description}
                    用例类:{caseclass}
                    用例方法:{casemethod}
                    用例请求的方式:{method}
                    用例请求的url:{url}
                    用例请求的headers:{headers}
                    用例请求的参数:{params}
                    用例请求的参数的方式:{params_type}
                   '''.format(casename=self.casename, description=self.description, caseclass=self.caseclass,
                              casemethod=self.casemethod, method=self.method, url=self.url, headers=self.headers, params=self.params, params_type=self.params_type)


if __name__ == '__main__':
    case = CaseObject()
    case.s = 'sd'
