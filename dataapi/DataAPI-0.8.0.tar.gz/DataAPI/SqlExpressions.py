# -*- coding: utf-8 -*-
u"""
Created on 2015-12-31

@author: cheng.li, weijun.shen, yuchen.lai
"""


class SQLQuery(object):
    def __repr__(self):
        return self.__str__()

    def __or__(self, right):
        return ORStatement(self, right)

    def __and__(self, right):
        return ANDStatement(self, right)


class Condition(SQLQuery):
    def __init__(self, field, condition, op):
        self.field = field
        self.condition = condition
        self.op = op

    def __str__(self):

        if self.op == u"in":
            sep = True
        else:
            sep = False

        if sep:
            return u"({field} {op} ({condition}))".format(field=self.field,
                                                          op=self.op,
                                                          condition=self.condition)
        else:

            try:
                conditons_list = self.condition.split(u',')
            except AttributeError:
                conditons_list = [self.condition]

            sql_str = ""
            for con in conditons_list:
                if sql_str == "":
                    sql_str += u"{field} {op} {condition}".format(field=self.field,
                                                                  op=self.op,
                                                                  condition=con)
                else:
                    sql_str += u" or {field} {op} {condition}".format(field=self.field,
                                                                      op=self.op,
                                                                      condition=con)
            return u'(' + sql_str + u')'

    # for python 2
    def __nonzero__(self):
        return bool(self.condition)

    # for python 3
    def __bool__(self):
        return bool(self.condition)


class ANDStatement(SQLQuery):
    def __init__(self, left_condition, right_condition):
        self.left = left_condition
        self.right = right_condition

    def __str__(self):
        if self.left and self.right:
            return u"({left} and {right})".format(left=self.left,
                                                  right=self.right)
        elif self.left:
            return self.left.__str__()
        elif self.right:
            return self.right.__str__()
        else:
            return None

    # for python 2
    def __nonzero__(self):
        return bool(self.left) or bool(self.right)

    # for python 3
    def __bool__(self):
        return bool(self.left) or bool(self.right)


class ORStatement(SQLQuery):
    def __init__(self, left_condition, right_condition):
        self.left = left_condition
        self.right = right_condition

    def __str__(self):
        if self.left and self.right:
            return u"({left} or {right})".format(left=self.left,
                                                 right=self.right)
        elif self.left:
            return self.left.__str__()
        elif self.right:
            return self.right.__str__()
        else:
            return None

    # for python 2
    def __nonzero__(self):
        return bool(self.left) or bool(self.right)

    # for python 3
    def __bool__(self):
        return bool(self.left) or bool(self.right)
