#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from core.info.field import Field
from utils.cmd_parser import cmd_parser

reload(sys)
sys.setdefaultencoding("utf-8")
# json检查器,遍历整个json,检查key是否符合要求
# key不能包含"id"
# 必须包含"{key}_id"
# 某个key包含多个对象时,key必须以_list结尾
# 某个key没包含多个对象时,不能以_list结尾

import json


class ObjJsonChecker(object):
    def _get_is_ok(self):
        return self._is_ok

    def _set_is_ok(self, val):
        self._is_ok = val

    is_ok = property(fget=_get_is_ok, fset=_set_is_ok)

    def __init__(self):
        self.is_ok = True
        self.obj_keys=[] #属于子对象的key是不能重复出现的,比如goods的description 和goods下service的description

    def _check(self, curr_key, arr):
        # print "当前检测:",arr
        keys=[]
        #是否有主键的标识
        has_pk=False
        for k2, v in arr.items():
            if k2.startswith("__"):
                continue
            k,_=cmd_parser(k2.replace("'",'"'))#转换下 这点很重要
            #标记主键
            if Field.F_PK in _.keys():
                has_pk=True
            # -l 1,3合法  -l 1非法
            if Field.F_LENGTH in _:
                nums=_.get(Field.F_LENGTH)
                if nums.count(",")!=1:
                    print '[ERROR] key值: -%s 声明错误,正确格式:-%s m,n,请检查 "%s":%s' % (Field.F_LENGTH,Field.F_LENGTH,k2, json.dumps(v, ensure_ascii=False))
                    self.is_ok = False
            if not _ or not all([x in _.keys() for x in [Field.F_CMNT]]): #-t默认str  但-c一定要有
                print '[ERROR] key值: %s必须声明类型,字段名称等信息,请检查 "%s":%s' % (k,k2,json.dumps(v, ensure_ascii=False))
                self.is_ok=False
            #checker
            # checker=_.get("k")
            # print checker
            # if checker and (not checker.startswith("'") or not checker.endswith("'")):
            #     print '[ERROR] key值: %s声明的检查器错误,请检查 "%s":%s' % (k,k2,json.dumps(v, ensure_ascii=False))
            #     self.is_ok=False
            keys.append(k)
            # list
            if isinstance(v, list):
                if len(v)>1:
                    print '[ERROR] key值: %s包含多个对象,仅需声明一个子象,请检查 "%s":%s' % (k,k2,json.dumps(v, ensure_ascii=False))
                    self.is_ok=False
                k1 = "".join(k.split("_list")[:-1]) or k
                # print k,k1
                if k1 in self.obj_keys:
                    print '[ERROR] key值: %s不能反复重复出现,请检查 "%s":%s' % (k,k2,json.dumps(v, ensure_ascii=False))
                    self.is_ok=False
                self.obj_keys.append(k1)
                if not k.endswith("_list"):
                    print '[ERROR] key值: %s 包含多个对象,应以_list结尾,请检查 "%s":%s' % (k, k, json.dumps(v, ensure_ascii=False))
                    self.is_ok = False
                for i, x in enumerate(v):
                    if "%s%s%s" % (Field.WRAP_SUB_OBJ_LIST_LEFT,k1,Field.WRAP_SUB_OBJ_LIST_RIGHT)!=_.get(Field.F_TYPE):

                        print '[ERROR] key值: %s 声明的类型为:%s,与key值不符合,正确值为%s%s%s,请检查 "%s"' % (k,_.get(Field.F_TYPE),Field.WRAP_SUB_OBJ_LIST_LEFT,k,Field.WRAP_SUB_OBJ_LIST_RIGHT, k2)
                        self.is_ok = False
                    # print k,k1
                    # if k=="category_list":
                    # print k1,i,x
                    if not isinstance(x, dict):
                        print '[ERROR] key值: %s 的值必须是由对象组成的list,请检查 "%s":%s' % (k, k, json.dumps(v, ensure_ascii=False))
                        self.is_ok=False
                    else:
                        self._check(k1, x)
            # dict
            elif isinstance(v, dict):
                # print k,self.obj_keys
                if k in self.obj_keys:
                    print '[ERROR] key值: %s不能反复重复出现,请检查 "%s":%s' % (k,k2,json.dumps(v, ensure_ascii=False))
                    self.is_ok=False
                self.obj_keys.append(k)

                if "%s%s%s" % (Field.WARP_SUB_OBJ_LEFT,k,Field.WARP_SUB_OBJ_RIGHT)!=_.get(Field.F_TYPE):
                    print '[ERROR] key值: %s 声明的类型为:%s,与key值不符合,正确值为%s%s%s,请检查 "%s"' % (k,_.get(Field.F_TYPE),Field.WARP_SUB_OBJ_LEFT,k,Field.WARP_SUB_OBJ_RIGHT, k2)
                    self.is_ok=False
                self._check(k, v)
            # str int float ...
            else:
                if k.endswith("_list"):
                    print '[ERROR] key值: %s 没有包含多个对象,不能以_list结尾,请检查 "%s":%s' % (k, k, json.dumps(v, ensure_ascii=False))
                    self.is_ok = False

        # 检测两个固定key

        if "id" in keys:
            print '[ERROR] 不能包含id,请检查: "id":', arr.get("id")
            self.is_ok = False
        #如果没有设置主键就要报错了
        if not has_pk:
            print '[ERROR] 至少一个字段被设置为主键,请检查 : %s' % json.dumps(arr, ensure_ascii=False)
            self.is_ok = False
        # if "%s_id" % curr_key not in keys:
            # print "--"
            # print '[ERROR] 必须包含 %s_id,请检查:%s' % (curr_key, json.dumps(arr, ensure_ascii=False))
            # self.is_ok = False
            # if "__comment" not in keys:
            #     print '[ERROR] 必须包含 __comment,该key非常重要,一定要有的,请检查 %s:%s' % (curr_key,json.dumps(arr,ensure_ascii=False))
            #     self.is_ok=False

    def check(self, txt):
        try:
            arr = json.loads(txt)
        except ValueError, e:
            print "该对象说明文件不是合法的json格式", e
            self.is_ok = False
            arr=None
        if arr:
            __comment=arr.get("__comment")
            if not __comment:
                print '[ERROR] 对象声明文件的json缺少字段:__comment'
                exit()
                self.is_ok = False
            else:
                _, opts = cmd_parser(arr.get("__comment"))
            self._check(opts.get(Field.F_NAME), arr)
        return self.is_ok



if __name__ == '__main__':
    with open("../demo/goods.json","r") as f:
        a=f.read()
    print ObjJsonChecker().check(a)
