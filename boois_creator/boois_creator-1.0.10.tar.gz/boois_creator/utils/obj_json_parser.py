# coding=utf-8
import copy
import json

from core.info.field import Field
from core.info.obj import Obj
from utils.cmd_parser import cmd_parser


class ObjJsonParser(object):

    def __init__(self,json_str):
        self._json = json_str
        self._arr = {}
        self.load_json_str()
        self._err=0
        self._err_msg="success"
    def load_json_str(self):
        try:
            self._arr=json.loads(self._json)
        except ValueError,ex:
            self._err_msg="obj_json 文件不是合法的json格式,请检查:%s" % ex
            self._err=1

    def _get_top_obj(self):
        if self.err!=0:
            return None
        if not hasattr(self,"_top_obj"):
            #开始解析出顶级的obj
            _comment=self._arr.get("__comment")
            _f,_dict=cmd_parser(_comment)
            top_obj_name=_dict.get(Field.F_NAME)
            top_obj_comment=_dict.get(Field.F_CMNT)
            parent_obj=Obj(name=top_obj_name,comment=top_obj_comment)
            fields=[]
            for k,v in self._arr.items():
                if k.startswith("__"):
                    continue
                f=Field(parent_obj=parent_obj,stm_str=k)
                fields.append(f)
            self._top_obj=Obj(name=top_obj_name,comment=top_obj_comment,fields=fields)
        return self._top_obj

    def _get_child_objs(self):
        if self.err != 0:
            return []
        if not hasattr(self,"_child_objs"):
            #结果容器
            self._child_objs={}
            def each_arr(parent_obj,arr):
                #当前对象的字段容器
                _fields=[]
                for k, v in arr.items():
                    if k.startswith("__"):
                        continue
                    _f, _dict = cmd_parser(k)
                    #当前字段
                    f=Field(parent_obj=copy.deepcopy(parent_obj),stm_str=k)

                    if f.is_sub_obj or f.is_sub_obj_list:
                        sub_cls = f.type_sub
                        _parent_obj=Obj(name=sub_cls,comment=_dict.get(Field.F_CMNT))#
                        # _parent_obj=Obj(name=_f,comment=_dict.get("c"))#

                        if f.is_sub_obj:
                            each_arr(_parent_obj, v)
                        elif f.is_sub_obj_list:
                            each_arr(_parent_obj, v[0])
                    else:
                        pass
                    #每次循环都收集进去
                    _fields.append(f)
                #排除顶级
                if parent_obj.name!=self.top_obj.name:
                    child_obj=copy.deepcopy(parent_obj)
                    child_obj.fields=_fields
                    self._child_objs[child_obj.name]=child_obj
            #传入顶级  开始解析所有的子对象

            each_arr(self.top_obj,self._arr)
        return self._child_objs
    def _get_err(self):
        return self._err
    def _get_err_msg(self):
        return self._err_msg
    top_obj=property(fget=_get_top_obj)
    child_objs=property(fget=_get_child_objs)
    err=property(fget=_get_err)
    err_msg=property(fget=_get_err_msg)

if __name__ == '__main__':
    with open("../demo/goods.json","r") as f:
        json_str=f.read()
    parser=ObjJsonParser(json_str)
    # print parser.top_obj
    # print parser.child_objs
    print parser.err
    for name,so in parser.child_objs.items():
        print name,",".join([x.name for x in so.fields])