#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils.table_struc_creator import factory


class table:
    FIELD_CREATE_DATE="createDate"
    ACTION_CREATE_TABLE=1
    ACTION_ADD_COL=1
    def __init__(self,name,pk,fields=None,engine="MyISAM",charset="utf8",auto_incr=1,comment=""):
        self.name=name
        self.pk=pk
        self.charset=charset
        self.engine=engine
        self.auto_incr=auto_incr
        self.fields=fields
        self.comment=comment or ""
    def to_txt(self,optimize=False):
        if self.pk:
            if isinstance(self.pk,list):
                pkstr=",\n\tPRIMARY KEY (`%s`)" % ("`,`".join(self.pk))
            else:
                pkstr=",\n\tPRIMARY KEY (`%s`)" % self.pk
        else:
            pkstr=""
        tab_arr=[]
        tab_arr.append('''CREATE TABLE `%s` (\n''' % self.name)


        if self.fields and isinstance(self.fields,list) and len(self.fields):
            field_arr=[]
            field_names=[getattr(x,"name") for x in self.fields]
            #主键一定要
            if "id" not in field_names:
                self.fields.insert(0, factory.id("id", "编号"))
            # if table.FIELD_CREATE_DATE not in field_names:
            #     self.fields.append(factory.datetime(table.FIELD_CREATE_DATE, "创建时间"))

            if optimize:
                #检测到没有常规字段则自动添加
                if "guid" not in field_names:
                    self.fields.insert(1, factory.guid("guid", "唯一标识"))
                if "sort" not in field_names:
                    self.fields.append(factory.int("sort", "排序"))
                if "status" not in field_names:
                    self.fields.append(factory.tinyint("status", "状态"))
            for f in self.fields:
                field_arr.append(f.to_txt())
            tabstr="\t"+(",\n\t".join(field_arr))
        else:
            tabstr=""
        tab_arr.append(tabstr)
        tab_arr.append(pkstr)
        tab_arr.append('''\n) ENGINE={engine} AUTO_INCREMENT={auto_incr} DEFAULT CHARSET={charset} COMMENT='{comment}';'''.format(name=self.name,pkstr=pkstr,engine=self.engine,auto_incr=self.auto_incr,charset=self.charset,comment=self.comment))
        return "".join(tab_arr)
    def to_add_txt(self):
        '''ALTER TABLE `employee`
ADD `mobile` CHAR(11) NOT NULL DEFAULT '' COMMENT '手机' ,
ADD `qq` VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'qq' ,
ADD `job` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '岗位' ;'''
        arr=[]
        arr.append("ALTER TABLE `%s`" % self.name)
        fields_arr=["ADD %s " % f.to_txt() for f in self.fields]
        arr.append(",\n".join(fields_arr))
        return "\n".join(arr)+";"
if __name__ == '__main__':

    #name=None, type=None,length=None, default=None, not_null=None, comment=None, auto_incr=None, unsigned=None
    t=table("noticle2","id",[
        # field("id","int",11,0,True,"id",True,True),
        # field("title","varchar",255,"",True,"标题",False,False),
        # field("content","text",None,None,True,"内容",False,False)
        factory.id("id", "编号"),
        factory.varchar("title", "标题"),
        factory.text("content", "内容"),
        factory.decimal("price", "价格"),
        factory.int("cmnt_cnt", "评论数", True),
        factory.datetime("create_time", "创建时间"),
        factory.guid("guid", "guid"),
        factory.char("mobile", "手机", 11)
    ])
    # print t.to_txt()
    # print t.to_txt(True)
    # print t.to_add_text()
    # exit()
    t=table("notice","id",[
        # field("id","int",11,0,True,"id",True,True),
        # field("title","varchar",255,"",True,"标题",False,False),
        # field("content","text",None,None,True,"内容",False,False)
        factory.varchar("title", "标题"),
        factory.text("content", "内容"),
        factory.varchar("author", "作者"),
    ])
    # print t.to_txt()

    t=table("emp2notice","id",[
        # field("id","int",11,0,True,"id",True,True),
        # field("title","varchar",255,"",True,"标题",False,False),
        # field("content","text",None,None,True,"内容",False,False)
        factory.int("empId", "用户"),
        factory.int("noticeId", "内容"),
    ])
    # print t.to_txt()
    # print "\n"
    t=table("employee","id",[
        # field("id","int",11,0,True,"id",True,True),
        # field("title","varchar",255,"",True,"标题",False,False),
        # field("content","text",None,None,True,"内容",False,False)
        factory.char("mobile", "手机号码", 11),
        factory.varchar("qq", "qq"),
        factory.varchar("job", "岗位"),
    ])
    # print t.to_txt()
    print t.to_add_txt()
    exit()
    # print "\n"
    t=table("suggest","id",[
        # field("id","int",11,0,True,"id",True,True),
        # field("title","varchar",255,"",True,"标题",False,False),
        # field("content","text",None,None,True,"内容",False,False)
        factory.int("userId", "用户id"),
        factory.varchar("userName", "用户名"),
        factory.text("content", "qq"),
    ])
    print t.to_txt()