#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import re
import sys

from core import json_checker

reload(sys)
sys.setdefaultencoding("utf-8")
from jinja2 import Template

from core.bean import Field, Obj
CUR_DIR=os.path.dirname(sys.argv[0])

def cls_name(txt):
    txt= re.sub("(_[a-z])",lambda t:t.group(1).lstrip("_").upper(),txt).lstrip("_")
    return txt[0].upper()+"".join(txt[1:])
def render(tpl_file_name,*args,**kwargs):
    with open(CUR_DIR+"/tpl/"+tpl_file_name) as f:
        template = Template(f.read())
    return template.render(*args,**kwargs)
def render_file(tpl_file_name,*args,**kwargs):
    with open(CUR_DIR + "/" + tpl_file_name) as f:
        template = Template(f.read())
    return template.render(*args, **kwargs)
def _total(num):
    res=None
    for i in range(num):
        if not res:
            res=1<<i
        else:
            res=res|(1<<i)
    return res
def _init_package(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    init_file= path + "/__init__.py"
    if not os.path.isfile(init_file):
        with open(init_file,"wb") as f:
            f.write("# -*- coding: utf-8 -*-")

def each_arr(obj_name,obj_comment, arr, func):
    # print arr
    fields=[]
    # print arr
    for k,v in arr.items():
        if k.startswith("__"):
            continue
        f=Field(obj_name,k,v)
        obj_comment1=f.comment
        if f.type_str in ["list","obj"]:
            sub_cls=f.type_sub
        else:
            sub_cls=f.name
        if isinstance(v,dict):
            each_arr(sub_cls, obj_comment1,v, func)
        elif isinstance(v,list):
            each_arr(sub_cls, obj_comment1,v[0], func)
        # print f
        fields.append(f)
    # return fields
    # print obj_name,fields
    func(obj_name,obj_comment,fields,arr)
def get_obj2fields(obj_name, txt):
    res={}
    def func(obj_name,obj_comment,fields,arr):
        if obj_name in res.keys():
            # ret=cmp(res.get(obj_name),(fields,arr))
            # if ret<0:
                #新的多
                # res[obj_name]=(fields,arr)
            print "[WARN] 存在相同的类,覆盖,%s,json:%s" %(obj_name,json.dumps(arr,ensure_ascii=False))
            # else:
            #     print "[WARN] 存在相同的类,跳过,%s,json:%s" %(obj_name,json.dumps(arr,ensure_ascii=False))
            #     print "obj_name",obj_name
        res[obj_name]=(obj_comment,fields,arr)
    arr=json.loads(txt)
    #第一下加载arr进行解析
    each_arr(obj_name,arr.get("__comment"), arr, func)
    return res

def gen_by_fields(obj_name, fields,comment):
    o=Obj(obj_name,fields,comment)
    path=CUR_DIR+"/out/%s" % obj_name
    if not os.path.isdir(path):
        os.makedirs(path)

    with open("%s/%s_info.py" % (path,obj_name),"wb") as f:
        f.write(render("info.py",obj=o))
def auto_pep8(filename):
    # os.system("autopep8 --in-place --aggressive --aggressive %s" % filename)
    # os.system("autopep8 --in-place  %s" % filename)
    pass
def gen_by_json_file(json_filename, out_path, test_path,adapter_path,demo_path,bll_path=None,dal_path=None,ui=None):
    with open(json_filename,"r") as f:
        json_txt=f.read()
    # fields=parse_json_arr(txt)
    # print "json_filename" ,json_filename
    top_obj_name=json_filename.replace("\\", "/").split("/")[-1].split(".")[0]
    is_ok= json_checker.Checker().check(top_obj_name, json_txt)
    if not is_ok:
        print "该对象说明文件不符规范,无法生成"
        exit()
    fields_arr=get_obj2fields(top_obj_name, json_txt)
    # exit()
    for _obj_name, (obj_comment,_fields,data_arr) in fields_arr.items():
        print "obj_name",_obj_name
        # print "_fields",_fields
        # continue
        #取本身这个对象里面的__commnet 如果没有找其key值的注释
        o=Obj(_obj_name, _fields,data_arr,obj_comment)
        # for _f in _fields:
        #     print _obj_name,_f
        # exit()
        obj_out_path= out_path + "/" + top_obj_name

        _init_package(obj_out_path)
        out_file="%s/%s_info.py" % (obj_out_path, _obj_name)
        print "out_file:",out_file
        #bak
        # if os.path.isfile(out_file):
        #     shutil.copy(out_file,  out_file+".bak")
        with open(out_file,"wb") as f:
            f.write(render("info.py",obj=o,top_obj_name=top_obj_name,total=_total(len(o.fields))))
        # auto_pep8(out_file)
        # print "ok"
        #生成test case
        # test_path="test"
        _init_package(test_path)
        obj_test_path= test_path + "/" + top_obj_name
        if not os.path.isdir(obj_test_path):
            os.makedirs(obj_test_path)
        test_out_file="%s/test_%s_info.py" % (obj_test_path, _obj_name)
        with open(test_out_file,"wb") as f:
            f.write(render("test_info.py",obj=o,top_obj_name=top_obj_name))
        # auto_pep8(test_out_file)
        #生成adapter


        _init_package(adapter_path)
        obj_adapter_path= adapter_path + "/" + top_obj_name

        _init_package(obj_adapter_path)
        adapter_out_file="%s/%s_adapter.py" % (obj_adapter_path, _obj_name)
        with open(adapter_out_file,"wb") as f:
            f.write(render("adapter.py",obj=o,top_obj_name=top_obj_name))
        # auto_pep8(adapter_out_file)
        #demo

        _init_package(demo_path)
        # demo_out_file="%s/%s_adapter.py" % (obj_demo_path, _obj_name)
        # _init_file(obj_demo_path)
        demo_out_file="%s/demo_%s.py" % (demo_path, _obj_name)
        # print demo_out_file
        with open(demo_out_file,"wb") as f:
            f.write(render("demo.py",obj=o,top_obj_name=top_obj_name))
        # auto_pep8(demo_out_file)
        #bll
        # obj_bll_path= bll_path + "/" + top_obj_name

        _init_package(bll_path)
        _init_package(dal_path)
        if _obj_name==top_obj_name:
            #bll
            bll_out_file="%s/%s_bll.py" % (bll_path, _obj_name)
            pub_bll_out_file="%s/%s_pub_bll.py" % (bll_path, _obj_name)
            app_bll_out_file="%s/%s_app_bll.py" % (bll_path, _obj_name)
            user_bll_out_file="%s/%s_user_bll.py" % (bll_path, _obj_name)
            user_dal_out_file="%s/%s_dal.py" % (dal_path, _obj_name)
            # print demo_out_file
            with open(bll_out_file,"wb") as f:
                f.write(render("bll.py",obj=o,top_obj_name=top_obj_name))
            #pub_bll
            with open(pub_bll_out_file, "wb") as f:
                f.write(render("pub_bll.py", obj=o, top_obj_name=top_obj_name))
            #app_bll
            with open(app_bll_out_file, "wb") as f:
                f.write(render("app_bll.py", obj=o, top_obj_name=top_obj_name))
            #user_bll
            with open(user_bll_out_file, "wb") as f:
                f.write(render("user_bll.py", obj=o, top_obj_name=top_obj_name))
            # user_bll
            with open(user_dal_out_file, "wb") as f:
                f.write(render("dal.py", obj=o, top_obj_name=top_obj_name))


        #ui
        if ui:
            #生成ui
            ui_path="ui"
            if not os.path.isdir(ui_path):
                os.makedirs(ui_path)
            # demo_out_file="%s/%s_adapter.py" % (obj_demo_path, _obj_name)
            # _init_file(obj_demo_path)
            ui_out_file="%s/%s.ui" % (ui_path, _obj_name)
            # print demo_out_file
            with open(ui_out_file,"wb") as f:
                f.write(render("ui2.xml",obj=o,top_obj_name=top_obj_name))
            cmd='pyuic4 -o "%s/ui_%s.py" "%s"' % (ui_path,_obj_name,ui_out_file)
            # print cmd
            # exit()
            os.system(cmd)
            #editor
            ed_out_file="%s/editor_%s.py" % (ui_path, _obj_name)
            with open(ed_out_file,"wb") as f:

                f.write(render("editor.py",obj=o,top_obj_name=top_obj_name))

def gen_files_out(case, fields_arr, top_obj_name):

    # print fields_arr
    with open("%s/case/%s/files_out.txt" % (CUR_DIR,case), "wb") as f:
        f.write(render_file("case/python/files.txt", fields_arr=fields_arr,top_obj_name=top_obj_name))
def parse_files_out(filename):
    res=[]
    with open(filename,"r") as f:
        arr=f.readlines()
        for a in arr:
            a=a.strip()
            if not a:
                continue
            if a.startswith("#"):
                continue
            row_arr=a.split("=>")

            if len(row_arr)!=2:
                print "line err:",a
                continue
            tpl,out_file=row_arr
            res.append((tpl.strip(),out_file.strip()))
    return res
def gen2(json_filename, case, out_path):
    with open(json_filename, "r") as f:
        json_txt = f.read()
    # fields=parse_json_arr(txt)
    # print "json_filename" ,json_filename
    top_obj_name = json_filename.replace("\\", "/").split("/")[-1].split(".")[0]
    is_ok = json_checker.Checker().check(top_obj_name, json_txt)
    if not is_ok:
        print "该对象说明文件不符规范,无法生成"
        exit()
    fields_arr = get_obj2fields(top_obj_name, json_txt)
    gen_files_out(case, fields_arr, top_obj_name)
    file_out_arr=parse_files_out("%s/case/%s/files_out.txt" % (CUR_DIR,case))
    # print file_out_arr
    # exit()
    for tpl,out_file in file_out_arr:
        if "#" in tpl:
            tpl1,_obj_name=tpl.split("#")
            obj_comment, _fields, data_arr=fields_arr.get(_obj_name)
            o=Obj(_obj_name, _fields, data_arr, obj_comment)
        else:
            tpl1=tpl
            o=None

        write_file(out_path+"/"+out_file,render_file("case/%s/tpl/%s" % (case,tpl1), obj=o, top_obj_name=top_obj_name))
def write_file(file,txt):
    path=os.path.dirname(file)
    if not os.path.isdir(path):
        os.makedirs(path)
    print "creating ", file
    with open(file, "wb") as f:
        f.write(txt)
if __name__ == '__main__':
    gen2("goods.json","python","out2")
