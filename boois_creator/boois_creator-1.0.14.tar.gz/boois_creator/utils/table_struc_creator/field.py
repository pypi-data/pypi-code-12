#!/usr/bin/env python
# -*- coding: utf-8 -*-
class field:
    def __init__(self, name=None, type=None,length=None, default=None, not_null=None, comment=None, auto_incr=None, unsigned=None):
        self.name=name
        self.type=type
        self.length=length
        self.default=default
        self.not_null=not_null
        self.comment=comment
        self.auto_incr=auto_incr
        self.unsigned=unsigned
    def to_txt(self):
        arr=[]
        arr.append("`%s` " % self.name)
        if self.type and self.length:
            arr.append("%s(" % self.type)
            arr.append("%s) " % self.length)
        else:
            arr.append("%s " % self.type)

        if self.unsigned and self.type in['int','tinyint','decimal']:
            arr.append("unsigned ")
        if self.not_null or self.auto_incr:
            arr.append("NOT NULL ")
        else:
            arr.append(" NULL ")
        if self.default is not None:#可能0
            arr.append("DEFAULT \"%s\" "% self.default)
        else:
            # arr.append(" DEFAULT ")
            pass
        if self.auto_incr:
            arr.append("AUTO_INCREMENT ")
        if self.comment:
            arr.append("COMMENT \"%s\" "% self.comment)
        return "".join(arr)


if __name__ == '__main__':
    f=field("id","int",11,0,True,"id",True,True)
    print f.to_txt()