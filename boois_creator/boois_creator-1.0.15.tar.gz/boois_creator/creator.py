#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pprint
import re
import sys

import datetime
reload(sys)
import os

sys.path.append(os.path.dirname(__file__))

sys.setdefaultencoding("utf-8")

from utils.obj_json_checker import ObjJsonChecker
from utils.str_fmt_helper import camel, camel_lower
import shutil

from utils import obj_json_parser
from utils.tpl_filename_parser import TplFilenameParser

from jinja2 import Environment, FileSystemLoader
VERSION_STR="该文件由boois_creator_v0.0.1于%s生成" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Creator(object):
    def __init__(self, json_file_path_list, tpl_path, out_path, is_overwrite=False):
        '''

        :param json_file_path_list: 多个json文件的路径组成的列表
        :param tpl_path: 模板的路径
        :param out_path: 生成的代码的存储路径
        :param is_overwrite: 生成的的文件是否覆盖已存在的文件
        '''
        self.json_file_path_list = json_file_path_list if isinstance(json_file_path_list, list) else [
            json_file_path_list]
        self.tpl_path = tpl_path
        if not os.path.isdir(tpl_path):
            print "[ERROR] 模板路径不存在"
            exit()
        self.out_path = out_path
        self.is_overwrite = is_overwrite
        self._init_tpl_engine()
    #初始化模板引擎 设置模板路径  自定义过滤器
    def _init_tpl_engine(self):
        env = Environment(loader=FileSystemLoader(self.tpl_path))
        # http://www.pythonfan.org/docs/python/jinja2/zh/templates.html#builtin-filters
        # 自定义过滤器
        env.filters['camel'] = camel
        env.filters['camel_lower'] = camel_lower
        self.env = env
    #以文件作为模板进行渲染
    def render_tpl(self, tpl_file_name, *args, **kwargs):
        template = self.env.get_or_select_template(template_name_or_list=tpl_file_name)
        return template.render(v=VERSION_STR,*args, **kwargs)
    #以字符串作为模板进行渲染
    def render_str(self, tpl_str, *args, **kwargs):
        # print "tpl_str", tpl_str
        template = self.env.from_string(tpl_str)
        return template.render(v=VERSION_STR,*args, **kwargs)
    #返回生成器目标路径
    def cover_to_out_path(self, path):

        return os.path.join(self.out_path, path.split(self.tpl_path)[-1].lstrip("/"))
    #返回模板文件相对模板目录的相对路径,供jinjia2渲染使用
    def get_rel_path(self, path):
        return path.split(self.tpl_path)[-1].lstrip("/")

    #生成一个列表,该列表本次生成任务
    def create(self):

        todo = []
        for f in self.json_file_path_list:
            if not os.path.isfile(f):
                print "[WARNING] %s文件不存在,跳过" % f
                continue
            with open(f, "r") as f1:
                json_str = re.sub("/\*(.*?)\*/","",f1.read(),1,re.S)
            # 检测json
            # print json_str
            # exit()
            # obj_name1 = f.split("/")[-1].split(".")[0]
            is_ok = ObjJsonChecker().check(json_str)
            if not is_ok:
                print "[ERROR] %s 内的json不是合法的对象说明文件,请检查后再生成" % f
                continue
            parser = obj_json_parser.ObjJsonParser(json_str)
            if parser.err != 0:
                print "[ERROR] %s的内容不是合法的json" % f
                continue

            # 用来渲染模板的变量
            self.data = {
                "top_obj": parser.top_obj,
                "child_objs": parser.child_objs,#以子对象名称为key的dict
                "child_obj_list": parser.child_objs.values()# 子对象组成的列表
            }
            # pprint.pprint(self.data)
            # pprint.pprint(self.data.get("top_obj").fields)
            # exit()

            # 开始处理生成的逻辑
            # 遍历交过来的模板
            parser = obj_json_parser.ObjJsonParser(json_str)
            curr_dir = self.tpl_path
            #递归的进入目录,遍历目录和文件
            def each_dir(path):
                for d in os.listdir(path):
                    #跳过__开头的文件,但__init__.py除外,目前__include目录存储着模板片段
                    if d.startswith("__") and d!="__init__.py":
                        continue
                    full_path = os.path.join(path, d)
                    #用以模板文件的类型
                    filename_parser = TplFilenameParser(d)
                    #静态文件:文件名和文件内容都不需要被渲染的文件
                    if filename_parser.is_static:
                        out_path=self.cover_to_out_path(full_path)#生成目的地的相对路径
                        one = {
                            "data": None,
                            "is_static": True

                        }
                        #目前暂时没有这种情况
                        if "###" in out_path or "##" in out_path:
                            # print one.get("out_path")
                            print "ignore,%s" % out_path
                            continue
                        # TODO tpl/python/info/#{{top_obj.name}}/__init__.py  =>  out/python/info/#{{top_obj.name}}/__init__.py
                        #本级静态文件,但父级不是
                        elif "#" in out_path:
                            #把真正的路径渲染出来
                            out_path=self.render_str(out_path.replace("#",""),**self.data)
                            #print out_path
                        if os.path.isdir(full_path):
                            #目录是直接创建 所以不需要src
                            one['tpl'] = None
                            one['is_path'] = True
                        else:
                            #文件是复制过去的  所以要指定src
                            one['src'] = full_path
                            one['is_path'] = False

                        one["out_path"]=out_path
                        todo.append(one)

                    elif filename_parser.is_simple:
                        # tpl=self.get_rel_path(os.path.dirname(full_path.replace("#",""))+"/"+self.render_str(filename_parser.filename_to_render,**self.data))
                        tpl = self.get_rel_path(full_path)
                        one = {
                            "tpl": tpl,
                            "is_path": os.path.isdir(full_path),
                            "out_path": os.path.join(self.out_path,tpl.replace("@", "")),
                            "data": {}
                        }

                        todo.append(one)

                    elif filename_parser.is_single_and_multi:
                        # pass
                        #处理顶级对象
                        tpl = self.get_rel_path(full_path)

                        one = {
                            "tpl": tpl,
                            "is_path": os.path.isdir(full_path),
                            "out_path": os.path.join(self.out_path,
                                                     self.render_str(tpl.replace("#", ""), obj=parser.top_obj,
                                                                     **self.data)),
                            "data": dict({"obj": parser.top_obj}, **self.data)
                        }

                        todo.append(one)
                        #处理子对象
                        for obj_name, obj in parser.child_objs.items():
                            tpl = self.get_rel_path(full_path)
                            one = {
                                "tpl": tpl,
                                "is_path": os.path.isdir(full_path),
                                "out_path": os.path.join(self.out_path,
                                                         self.render_str(tpl.replace("#", ""), obj=obj, **self.data)),#传入当前的obj
                                "data": dict({"obj": obj}, **self.data)
                            }
                            #
                            todo.append(one)

                    elif filename_parser.is_multi:
                        for obj_name, obj in parser.child_objs.items():
                            tpl = self.get_rel_path(full_path)

                            one = {
                                "tpl": tpl,
                                "is_path": os.path.isdir(full_path),
                                "out_path": os.path.join(self.out_path,
                                                         self.render_str(tpl.replace("#", ""), obj=obj, **self.data)),
                                "data": dict({"obj": obj}, **self.data)
                            }

                            todo.append(one)
                    elif filename_parser.is_single:
                        # tpl=self.get_rel_path(os.path.dirname(full_path.replace("#",""))+"/"+self.render_str(filename_parser.filename_to_render,**self.data))
                        tpl = self.get_rel_path(full_path)
                        one = {
                            "tpl": tpl,
                            "is_path": os.path.isdir(full_path),
                            "out_path": os.path.join(self.out_path,
                                                     self.render_str(tpl.replace("#", ""), obj=parser.top_obj,
                                                                     **self.data)),
                            "data": dict({"obj": parser.top_obj}, **self.data)
                        }

                        todo.append(one)
                    if os.path.isdir(full_path):
                        each_dir(full_path)

            each_dir(curr_dir)
        # self._debug(todo)
        # print 1
        self.do_create(todo)
    #测试使用
    def _debug(self,todo):
        res=[]
        for x in todo:
            if 'data' in x:
                del x['data']
            res.append(x)

        print json.dumps(res, ensure_ascii=False)
        exit()

    # 生成代码的操作

    def do_create(self, todo):
        for one in todo:
            # print one.get("is_static")
            out_file = one.get("out_path")
            parent_path = os.path.dirname(out_file)
            if not os.path.isdir(parent_path):

                os.makedirs(parent_path)

            if one.get("is_static"):
                # print one.get("is_path")
                if one.get("is_path"):
                    if not os.path.isdir(one.get("out_path")):
                        os.makedirs(out_file)
                else:
                    src = one.get("src")
                    if src.endswith(".DS_Store"):
                        continue
                    # print src," => ",out_file

                    if not os.path.isfile(out_file):
                        print "creating %s" % out_file

                        shutil.copyfile(src, out_file)
                    else:
                        if self.is_overwrite:
                            print "creating %s" % out_file

                            os.remove(out_file)
                            shutil.copyfile(src, out_file)
                        else:
                            print "skip %s" % out_file
            else:
                if not one.get("is_path"):
                    # print one.get("tpl")," => ",out_file,"==",os.path.join(self.tpl_path,one.get("tpl")),"==",os.path.isfile(os.path.join(self.tpl_path,one.get("tpl")))
                    # print out_file
                    txt = self.render_tpl(one.get("tpl"), **one.get("data"))

                    if not os.path.isfile(out_file):
                        print "creating %s" % out_file
                        with open(out_file, "w") as f:
                            f.write(txt)
                    else:
                        if self.is_overwrite:
                            print "creating %s" % out_file
                            with open(out_file, "w") as f:
                                f.write(txt)
                        else:
                            print "skip %s" % out_file


if __name__ == '__main__':
    if len(sys.argv)==4:
        # print os.path.dirname(__file__)+"/tpl/python"
        c = Creator(sys.argv[1], os.path.dirname(__file__)+"/tpl/python", sys.argv[2], sys.argv[3]=="True")
        c.create()
    else:
        c = Creator("demo/goods.json", "tpl/python", "out/python", True)
        # c = Creator("demo/goods.json", "tpl/python", "/Volumes/d01/code/api-ser/servs/goods/v0.0.0/core", True)
        # c = Creator("demo/goods.json", "tpl/android", "out/android/out/src", True)
        c.create()
