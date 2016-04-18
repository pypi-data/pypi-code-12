# -*- coding: utf-8 -*-
__author__ = 'tangke'
from MosT.log import MyLog


class MethodObject(object):
    def __init__(self, name, methodname):
        self.name = name
        self.methodname = methodname

def test_method_call(name, methodname):
    '''
    生成测试对象(哪个类，哪个方法)
    '''
    classname_array = name.split('.')
    packagename, classname = ''.join(classname_array[:-1]), classname_array[-1]
    try:
        packge = __import__(packagename)
    except ImportError, e:
        MyLog.log().error(e)

    if hasattr(packge, classname):
        class_name = getattr(packge, classname)
    else:
        raise Exception('包:' + packagename + '中不存在类:' + classname)
    if hasattr(class_name, methodname):
        method_name = getattr(class_name, methodname)
        apply(method_name, [class_name()])
    else:
        raise Exception('在类'+class_name+'中不存在这样的方法'+methodname)

if __name__ == '__main__':
    test_method_call('test.Test', 'sd')
