#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import sys

from utils.cmd_parser import cmd_parser
from utils.table_struc_creator import factory
from utils.table_struc_creator.table import table

reload(sys)
sys.setdefaultencoding("utf-8")
import json
import re


def cls_name(txt):
    if not txt:
        # print "=="
        return ""
    txt= re.sub("(_[a-z])",lambda t:t.group(1).lstrip("_").upper(),txt).lstrip("_")
    return txt[0].upper()+"".join(txt[1:])

class Obj(object):

    def __init__(self,name="",fields=[],data_arr=None,comment=None):
        self.name=name
        self.name_cap=cls_name(name)
        self.name_cls="%s_info.%s" %(name,self.name_cap)
        self.fields=fields
        self.data_arr=data_arr
        self.fields_names=[x.name for x in self.fields]
        self.comment=comment or ""
        self.data_json=json.dumps(data_arr,ensure_ascii=False)
        self.mysql_create_sql=self.get_mysql_create_sql()


        #头部import语句

    def get_mysql_create_sql(self):
        fields=[]
        # f_names=[]
        for f in self.fields:
            if f.name=='%s_id' % self.name:
                one= factory.guid(f.name)
            elif f.type in ['status']:
                one= factory.int(f.name)
            elif f.type in ['price']:
                one= factory.decimal(f.name)
            elif f.type in ['datetime.datetime']:
                one= factory.datetime(f.name)
            elif f.type in ['str']:
                one= factory.varchar(f.name)
            elif f.type:
                one= factory.text(f.name)
            # f_names.append(f.name)
            one.comment=f.comment or f.name
            fields.append(one)
        # t=table(self.name,"id",fields)
        t=table(name=self.name,pk="id",fields=fields,comment=self.comment)
        return t.to_txt(False)


class Field(object):

    def __repr__(self):
        return "name:{n}, type:{t}, type_str:{ts}, type_sub:{tsb}, len:{l}, default:{d}, comment:{c}, checker:{k}".format(n=self.name, t=self.type, ts=self.type_str, tsb=self.type_sub, l=self.length, d=self.default, c=self.comment, k=self.checker_stm)
    def init_para(self):
        arr=self.opts
        _t=arr.get("t") or "str"
        _d=arr.get("d")
        _l=arr.get("l")
        _n=arr.get("n") or "true"
        _c=arr.get("c") or self.name
        _k=arr.get("k") or '-t str'
        #处理defalut
        if _d is None:
            if _t in ['str']:
                _d=""
            elif _t in ['int']:
                _d=0
            elif _t in ['float','decimal']:
                _d=0.0
        if _l is None:
            if _t in ['str']:
                _l=255
            elif _t in ['int']:
                _l=11
            elif _t in ['float','decimal']:
                _l=11

        self.type=_t
        self.type_str=""
        self.type_sub=""
        self.length=_l
        #这里要根据type转成相应的值
        self.default_stm=None
        if self.type in ['str']:
            self.type_str="str"
            self.default=arr.get("d") or ""
        elif self.type in ['int']:
            self.type_str="int"
            self.default=int(_d) if _d else 0
        elif self.type in ['float']:
            self.type_str="float"
            self.default=float(_d) if _d else 0.0
        elif self.type in ['decimal']:
            self.type_str="decimal"
            self.default=float(_d) if _d  else 0.00
        elif self.type.startswith("[") and self.type.endswith("]"):
            self.type_str="list"
            self.type_sub=self.type.replace("[","").replace("]","")
            self.default=[]
        elif self.type.startswith("{") and self.type.endswith("}"):
            self.type_str="obj"
            self.type_sub=self.type.replace("{","").replace("}","")
            self.default_stm="self.default=%s()" % self.type_str
            self.default=None
        elif self.type.startswith("<") and self.type.endswith(">"):
            self.type_str="sys"
            self.type_sub=self.type.replace("<","").replace(">","")
            if self.type_sub=="datetime.datetime":
                self.default=datetime.datetime.strptime(_d,"%Y-%m-%d %H:%M:%S") if _d else datetime.datetime.now()
            else:
                raise ValueError("非法type:%s," % self.type)
        else:
            raise ValueError("非法type:%s" % self.type)

        self.nullable=_n in ["true","1"]
        self.comment=_c
        self.checker_stm=_k

        #old
        self.obj_name_cap=cls_name(self.obj_name)
        self.field_name=self.name
        self.name_upper=self.name.upper()
        self.name_json= self.name
        self.cls_file=self.type_sub if self.type_str in ['obj','list'] else ""  #[obj],{obj} 另外<sys>,str,int,之类就无需在adpater中声明import
        try:
            self.cls_cap=cls_name(self.cls_file)
        except:
            print self.name

        self.name_field_index="F_%s" % self.name_upper
        self.name_field_name="F_%s_NAME" % self.name_upper

        # if not self.cls_cap:
        #     print "e_f", self.name

        self.type_show="%s_info.%sInfo" % (self.cls_file,self.cls_cap)
        self.strfy_prop="json"

    def init_other(self):
        self.checker_common='''chker = ValiRuleChker(r'{checker_stm}')
        msg,info = chker.chk(val)
        if not chker.is_validated:
            raise ValueError("{f} %s" % info)'''.format(f=self.name, checker_stm=self.checker_stm)
        self.checker_obj='''
        if not isinstance(val, {obj}):
            raise ValueError("{f} 必须是{obj}类型")'''.format(f=self.type_sub,obj=self.type_show)
        self.checker_raw_type= '''
        if not isinstance(val, {obj}):
            raise ValueError("{f} 必须是{obj}类型")'''.format(f=self.name,obj=self.type_sub)#datetime.datetime
        self.checker_obj_list= '''
        if not isinstance(val, list):
            raise ValueError("{f} 必须是list类型")
        for _ in val:
            if not isinstance(_,{obj}):
                raise ValueError("{f} 的每一项都必须是{obj}类型")'''.format(f=self.name,obj=self.type_show)
        self.checker= "return True #TODO"

        #endregion
        if self.type_str=="str":
            self.load_arr_stm='''arr.get(%s_info.%sInfo.%s)''' % (self.obj_name,self.obj_name_cap,self.name_field_name)
            self.load_arr_stm2='''if {on}_info.{nc}Info.{nfn} in arr:
            arr.get({on}_info.{nc}Info.{nfn})'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.name,on=self.obj_name,nc=self.obj_name_cap,nfn=self.name_field_name)
            self.dump_arr_stm='''self.info.get_%s()''' % self.name
            self.dump_mysql_data_stm='''self.info.get_%s()''' % self.name
            self.load_mysql_data_stm='''arr.get(%s_info.%sInfo.%s)''' %  (self.obj_name,self.obj_name_cap,self.name_field_name)
            self.load_mysql_data_stm2='''if {on}_info.{onc}Info.{nfn} in arr and arr.get({on}_info.{onc}Info.{nfn}) is not None:
            self.info.set_{n}({lmds},False)
            '''.format(on=self.obj_name,onc=self.obj_name_cap,nfn=self.name_field_name,n=self.name,lmds=self.load_mysql_data_stm)
            self.checker= self.checker_common
            self.default_val="''"
        elif self.type_str in ["float","decimal"]:
            self.dump_arr_stm='''self.info.get_%s()''' % self.name
            self.load_arr_stm2='''if {on}_info.{nc}Info.{nfn} in arr:
            arr.get({on}_info.{nc}Info.{nfn})'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.name,on=self.obj_name,nc=self.obj_name_cap,nfn=self.name_field_name)
            self.dump_mysql_data_stm='''self.info.get_%s()''' % self.name
            self.load_mysql_data_stm='''arr.get(%s_info.%sInfo.%s)''' %  (self.obj_name,self.obj_name_cap,self.name_field_name)
            self.load_mysql_data_stm2='''if {on}_info.{onc}Info.{nfn} in arr and arr.get({on}_info.{onc}Info.{nfn}) is not None:
            self.info.set_{n}({lmds},False)
            '''.format(on=self.obj_name,onc=self.obj_name_cap,nfn=self.name_field_name,n=self.name,lmds=self.load_mysql_data_stm)
            self.checker=self.checker_common
            self.default_val=0
        elif self.type_str=="int":
            self.load_arr_stm='''arr.get(%s_info.%sInfo.%s)''' %  (self.obj_name,self.obj_name_cap,self.name_field_name)
            self.load_arr_stm2='''if {on}_info.{nc}Info.{nfn} in arr:
            arr.get({on}_info.{nc}Info.{nfn})'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.name,on=self.obj_name,nc=self.obj_name_cap,nfn=self.name_field_name)
            self.dump_arr_stm='''self.info.get_%s()''' % self.name
            self.dump_mysql_data_stm='''self.info.get_%s()''' % self.name
            self.load_mysql_data_stm='''arr.get(%s_info.%sInfo.%s)''' % (self.obj_name,self.obj_name_cap,self.name_field_name)
            self.load_mysql_data_stm2='''if {on}_info.{onc}Info.{nfn} in arr and arr.get({on}_info.{onc}Info.{nfn}) is not None:
            self.info.set_{n}({lmds},False)
            '''.format(on=self.obj_name,onc=self.obj_name_cap,nfn=self.name_field_name,n=self.name,lmds=self.load_mysql_data_stm)
            self.checker=self.checker_common
            self.default_val=0
        elif self.type_str=="sys" and self.type_sub=="datetime.datetime":
            self.load_arr_stm='''datetime.datetime.strptime(arr.get(%s_info.%sInfo.%s),"%%Y-%%m-%%d %%H:%%M:%%S")''' %  (self.obj_name,self.obj_name_cap,self.name_field_name)

            self.load_arr_stm2='''if {on}_info.{nc}Info.{nfn} in arr:
            datetime.datetime.strptime(arr.get({on}_info.{nc}Info.{nfn}),"%%Y-%%m-%%d %%H:%%M:%%S")'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.name,on=self.obj_name,nc=self.obj_name_cap,nfn=self.name_field_name)
            self.dump_arr_stm='''self.info.get_%s().strftime("%%Y-%%m-%%d %%H:%%M:%%S")''' % self.name
            self.dump_mysql_data_stm='''self.info.get_%s().strftime("%%Y-%%m-%%d %%H:%%M:%%S")''' % self.name

            # self.load_mysql_data_stm='''datetime.datetime.strptime(arr.get(%s_info.%sInfo.%s),"%%Y-%%m-%%d %%H:%%M:%%S")''' %  (self.obj_name_cap,self.name_field_name)#从文本读进来他就是str类型
            self.load_mysql_data_stm='''arr.get(%s_info.%sInfo.%s)''' %  (self.obj_name,self.obj_name_cap,self.name_field_name)#mysql出来的数据是datetime.datetime
            #判断下类型
            self.load_mysql_data_stm='''datetime.datetime.strptime(arr.get(%s_info.%sInfo.%s),"%%Y-%%m-%%d %%H:%%M:%%S") if isinstance(arr.get(%s_info.%sInfo.%s),(str,unicode)) else arr.get(%s_info.%sInfo.%s)''' %  (self.obj_name,self.obj_name_cap,self.name_field_name,self.obj_name,self.obj_name_cap,self.name_field_name,self.obj_name,self.obj_name_cap,self.name_field_name)
            self.load_mysql_data_stm2='''if {on}_info.{onc}Info.{nfn} in arr and arr.get({on}_info.{onc}Info.{nfn}) is not None:
            self.info.set_{n}({lmds},False)
            '''.format(on=self.obj_name,onc=self.obj_name_cap,nfn=self.name_field_name,n=self.name,lmds=self.load_mysql_data_stm)
            self.checker=self.checker_raw_type
            self.default_val="datetime.datetime.now()"
        elif self.type_str=="list":#list
            # cls=self.type.replace("[","").replace("]","")

            #[service_info.ServiceInfo(data_arr=x) for x in arr.get("services")]
            #service_adapter.ServiceAdapter().load_arr(x).get_info()
            self.load_arr_stm='''[%s_adapter.%sAdapter().load_arr(x).get_info() for x in arr.get(%s_info.%sInfo.%s)]''' %(self.cls_file,self.cls_cap,self.obj_name, self.obj_name_cap,self.name_field_name)
            # self.dump_arr_stm='''",".join([x.json for x in self.info.get_%s()])''' % self.name
            self.load_arr_stm2='''if {on}_info.{nc}Info.{nfn} in arr:
            self.info.set_{n}([{cf}_adapter.{cc}Adapter(x).arr for x in self.info.get_{n}()])'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.name,on=self.obj_name,nc=self.obj_name_cap,nfn=self.name_field_name)
            self.dump_arr_stm='''%s_adapter.%sAdapter(self.info.get_%s()).arr''' % (self.cls_file,self.cls_cap,self.name_json)
            self.dump_mysql_data_stm='''json.dumps([%s_adapter.%sAdapter(x).arr for x in self.info.get_%s()],ensure_ascii=False, cls=JsonEncoder)''' % (self.cls_file,self.cls_cap,self.name_json)
            self.load_mysql_data_stm='''[%s_adapter.%sAdapter().load_arr(x).get_info() for x in json.loads(arr.get(%s_info.%sInfo.%s))]''' % (self.cls_file,self.cls_cap,self.obj_name, self.obj_name_cap,self.name_field_name)
            self.load_mysql_data_stm2='''if {on}_info.{onc}Info.{nfn} in arr and arr.get({on}_info.{onc}Info.{nfn}) is not None:
            self.info.set_{n}({lmds},False)
            '''.format(on=self.obj_name,onc=self.obj_name_cap,nfn=self.name_field_name,n=self.name,lmds=self.load_mysql_data_stm)
            self.checker=self.checker_obj_list
            self.default_val="[]"
        elif self.type_str=="obj":

            # self.load_arr_stm='''[%s(data_arr=x) for x in arr.get(%s_info.%sInfo.%s)]''' %(self.type,self.name_json)
            # self.load_arr_stm='''{cf}_adapter.{cc}Adapter().load_arr(arr.get({n}_info.{nc}Info.{nfn})).get_info()'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.obj_name,nfn=self.name_field_name)
            self.load_arr_stm2='''if {on}_info.{nc}Info.{nfn} in arr:
            self.info.set_{n}({cf}_adapter.{cc}Adapter().load_arr(arr.get({on}_info.{nc}Info.{nfn})).get_info())'''.format(cf=self.cls_file,cc=self.cls_cap, n=self.name,on=self.obj_name,nc=self.obj_name_cap,nfn=self.name_field_name)
            # self.dump_arr_stm='''%s(data_arr=self.info.get_%s()).json''' % (self.type,self.name)
            # self.dump_arr_stm='''%s(data_arr=self.info.get_%s()).arr''' % (self.type,self.name)
            self.dump_arr_stm='''%s_adapter.%sAdapter(self.info.get_%s()).arr''' % (self.cls_file,self.cls_cap,self.name_json)
            self.dump_mysql_data_stm='''%s_adapter.%sAdapter(self.info.get_%s()).json''' % (self.cls_file,self.cls_cap,self.name_json)
            self.load_mysql_data_stm='''%s_adapter.%sAdapter().load_arr(json.loads(arr.get(%s_info.%sInfo.%s))).get_info()''' %(self.cls_file,self.cls_cap,self.obj_name, self.obj_name_cap,self.name_field_name)
            self.load_mysql_data_stm2='''if {on}_info.{onc}Info.{nfn} in arr and arr.get({on}_info.{onc}Info.{nfn}) is not None:
            self.info.set_{n}({lmds},False)
            '''.format(on=self.obj_name,onc=self.obj_name_cap,nfn=self.name_field_name,n=self.name,lmds=self.load_mysql_data_stm)
            self.checker=self.checker_obj
            self.default_val="%s_info.%sInfo()" % (self.cls_file,self.cls_cap)
    def __init__(self, obj_name,json_key,json_val):
        self.obj_name=obj_name#传入这个字段所属的obj
        json_key=json_key.replace("'",'"')
        field_name,opts=cmd_parser(json_key)
        self.name=field_name.rstrip("_list") if field_name.endswith("_list") else field_name
        # print self.name
        self.json_key=json_key
        self.opts=opts
        self.init_para()
        self.init_other()
        #old params:  obj_name,field_name, name_json, type="", strfy_prop="json"
        #type:str price status datetime list sub_obj
        #child_type: type为list时有效


if __name__ == '__main__':
    # afs=[
    #     Field("app_key","","str"),
    #     Field("cover_img_info","img","img_info.ImgInfo"),
    #     Field("post_date","","datetime"),
    #     Field("title_tag_info_list","title_tag","[tag_info.TagInfo]","str"),
    #     Field("img_info_list","imgs","[img_info.ImgInfo]"),
    #     Field("status","","status"),
    #     Field("category_info_list","category","[category_info.Category]","str"),
    # ]
    # ao=Obj("goods","article","Article","article")
    d=Desc("-t str -l 36 -n false -c 唯一id")
    d=Desc('-t str -l 36 -n false -c 唯一id -k "-t guid"')
    d=Desc('-t int -l 11 -n false -c 数量 -k "-t +int|zero"')
    d=Desc('-t float -l 11 -n false -c 分数 -k "-t +int|float|zero"')
    d=Desc('-t decimal -l 11 -n false -c 价格 -k "-t +int|+float|zero"')
    d=Desc('-t <datetime> -l 11 -n false -c 时间 -k "-t datetime')
    d=Desc('-t {goods} -l 11 -n false -c 商品')
    d=Desc('-t [goods] -l 11 -n false -c 关联商品')
    print "type:",d.type
    print "length:",d.length
    print "default:",type(d.default),d.default
    print "default_stm:",type(d.default_stm),d.default_stm
    print "nullable:",type(d.nullable),d.nullable
    print "comment:",d.comment
    print "checker:",d.checker
    print "="*30
    exit()


