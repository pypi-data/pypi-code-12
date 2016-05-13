#!/usr/bin/env python
# coding:utf-8
'''
萧鸣-原创:boois@qq.com 2016.1.21
本模块用于将一个request.string类型的字符串转换成数据库的sql字符串

'''
import sys
import re
import urllib
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding("utf-8")


def search_str_parse(args_str):
    '''
    规则是:s.word.0=123123&s.word1.1=asdfasd&&s.word1=asdfasd&&&&&
    word只能是字母数字下划线组合
    s.表示是开头,word是指搜索字段名,.0表示不显示,.1和空表示默认显示
    s.word.0=foo：是一个搜索字段,字段名为word,默认不显示在ui中,.0表示为不显示,foo是搜索的值
    s.word.1=foo：是一个搜索字段,字段名为word,默认不显示在ui中,.1表示为显示在UI中,foo是搜索的值
    s.word=foo：是一个搜索字段,字段名为word,默认不显示在ui中,无显示后缀表示为默认显示在UI中,foo是搜索的值
    :param args_str:搜索字符串,也就是url的request.querystring部分
    :return:[('word', False, '123123'), ('word1', True, 'asdfasd'), ('word1', True, 'asdfasd')]
    '''
    if not args_str:
        return []
    sharp_pos = args_str.find("#")
    if sharp_pos != -1:
        args_str = args_str[0:sharp_pos]
    args_str = "&" + args_str.split("?")[-1].strip("&")  # 将字符串转换为标准的  &a=1&a=2&a=3模式
    # 用正则表达式获取到所有s.word.0=1,s.word.1=2,s.word=3
    args_list = re.findall("[&]+s\.([^=\.]*)(?:(\.0|\.1)*)?[^=]*\s*=\s*([^&]*)", args_str)
    search_group = OrderedDict()
    for word, is_show, val in args_list:
        search_group[word] = (word.strip(), is_show == ".1" or is_show == "", val)
    return search_group.values()


class SearchConditionParser(object):
    '''
    根据搜索字符串来解析出搜索条件
    :param search_val:用来解析的search_str
    :return:(code, search_val, sql_str, where_str, mapping, info)
    有以下几种形式(用了四种判定符各自组合:!,*,~,=):
    1.以！开头的表示否
    &s.field = !abc => field <> abc
    &s.field =!*abc* => field not like '%abc%'
    &s.field = !*abc => field not like '%abc'
    &s.field = !abc* => field not like 'abc%'
    &s.field = !~1,2,3~ =>相当于not in(...),实际将转化为 field<>1 or field<>2 or filed<>3
    2.以波浪线为范围的
    &s.field = 2016-1-1 1:1:1~~2016-1-1 1:1:1 => field between '2016-1-1 1:1:1' and '2016-1-1 1:1:1' 用于时间
    &s.field = ~1~ or ~1,2,3~ => 相当于in(...),实际将转化为 field=1 or field=2 or filed=3
    &s.field = ~1 => field<1 小于
    &s.field = ~=1 => field<=1 小于等于
    &s.field = 1~ => field>1 大于
    &s.field = 1=~ => field>1 大于等于
    &s.field = 0~1 => field<0 and field>1
    &s.field = 0=~=1 => field>=0 and field<=1
    &s.field = 0~=1 => field>0 and field=<1
    &s.field = 0=~1 => field>=0 and field<1
    3.带星号通配符的
    &s.field = *abc* => field like '%abc%'
    &s.field = abc* => field like 'abc%'
    &s.field = *abc => field like '%abc'
    4.什么都没有的
    &s.field = abc  => field = abc
    #(\;|'|\sand\s|exec\s|\sinsert\s|select|delete|update|\scount|\*|\!|\~|\%|\schr\(|\smid\(|master|truncate|\schar|declare)
    '''

    EQUALS = 1 << 0
    NOT_EQUALS = 1 << 2
    NOT_LIKE = 1 << 3
    NOT_LIKE_END = 1 << 4
    NOT_LIKE_START = 1 << 5
    NOT_IN = 1 << 6
    LIKE = 1 << 7
    LIKE_START = 1 << 8
    LIKE_END = 1 << 9
    IN = 1 << 10
    LESS_THAN = 1 << 11
    LESS_EQUALS = 1 << 12
    GREATER_THAN = 1 << 13
    GREATER_EQUALS = 1 << 14
    INT_RANGE_G_L = 1 << 15
    INT_RANGE_GE_LE = 1 << 16
    INT_RANGE_G_LE = 1 << 17
    INT_RANGE_GE_L = 1 << 18
    DATE_BETWEEN = 1 << 19

    @staticmethod
    def _int_chker(val):
        if isinstance(val, int):
            return True
        val = str(val).strip()
        if val.isdigit():
            return True
        if val.lstrip("-").isdigit():
            return True
        return False

    @staticmethod
    def _float_chker(val):
        if isinstance(val, float):
            return True
        val = str(val).strip()
        if val.count(".") == 1 and val.replace(".", "").isdigit():
            return True
        if val.count(".") == 1 and val.replace(".", "").lstrip("-").isdigit():
            return True
        return False

    @staticmethod
    def parse(search_str):
        # 先判断什么符号都没有的情况
        # region &s.field = abc => field = abc
        if search_str.find("!") == -1 and \
                        search_str.find("*") == -1 and \
                        search_str.find("~") == -1:
            return (SearchConditionParser.EQUALS,
                    search_str,
                    "{f} = '" + search_str + "'",
                    "{f} = ?",
                    (search_str,),
                    u"{f} 等于 {v}")
        # endregion
        search_str = search_str.strip()
        # 以感叹号开头的
        # region &s.field = !abc => field <> abc
        if search_str.startswith("!"):
            search_val = search_str[1:]
            if search_val.find("*") == -1 and search_val.find("~") == -1:
                return (SearchConditionParser.NOT_EQUALS,
                        search_val,
                        "{f} <> '" + search_val + "'",
                        "{f} <> ?",
                        (search_val,),
                        u"{f} 不等于 {v}")
        # endregion
        # region &s.field =!*abc* => field not like '%abc%'
        if search_str.startswith("!*") and search_str.endswith("*"):
            search_val = search_str[2:-1]
            return (SearchConditionParser.NOT_LIKE,
                    search_val,
                    "{f} not like '%" + search_val + "%'",
                    "{f} not like ?",
                    ('%' + search_val + '%',),
                    u"{f} 不包含 {v}")
        # endregion
        # region &s.field = !*abc => field not like '%abc'
        if search_str.startswith("!*") and not search_str.endswith("*"):
            search_val = search_str[2:]
            return (SearchConditionParser.NOT_LIKE_END,
                    search_val,
                    "{f} not like '%" + search_val + "'",
                    "{f} not like ?",
                    ('%' + search_val,),
                    u"{f} 不以 {v} 结尾")
        # endregion
        # region &s.field = !abc* => field not like 'abc%'
        if search_str.startswith("!") and search_str.endswith("*"):
            search_val = search_str[1:-1]
            return (SearchConditionParser.NOT_LIKE_START,
                    search_val,
                    "{f} not like '" + search_val + "%'",
                    "{f} not like ?",
                    (search_val + '%',),
                    u"{f} 不以 {v} 开头")
        # endregion
        # region &s.field = !~1,2,3~ =>相当于not in(...),实际将转化为 field<>1 or field<>2 or filed<>3
        if search_str.startswith("!~") and search_str.endswith("~"):
            search_val = search_str[2:-1]
            vals = []
            sql = []
            param_sql = []
            mapping = []
            for val in search_val.split(","):
                vals.append(val)
                sql.append("{f} <> '%s'" % val)
                param_sql.append("{f} <> ?")
                mapping.append(val)
            return (SearchConditionParser.NOT_IN,
                    search_val,
                    " and ".join(sql),
                    " and ".join(param_sql),
                    tuple(mapping),
                    u"{f} 不等于 %s" % u" 或 ".join(vals))
        # endregion
        # 带星号通配符的
        # region &s.field = *abc* => field like '%abc%'
        if search_str.startswith("*") and search_str.endswith("*"):
            search_val = search_str[1:-1]
            return (SearchConditionParser.LIKE,
                    search_val,
                    "{f} like '%" + search_val + "%'",
                    "{f} like ?",
                    ('%' + search_val + '%',),
                    u"{f} 包含 {v}")
        # endregion
        # region &s.field = abc* => field like 'abc%'
        if search_str.endswith("*") and \
                not search_str.startswith("*") and \
                not search_str.startswith("!*") and \
                not search_str.startswith("!"):
            search_val = search_str[:-1]
            return (SearchConditionParser.LIKE_START,
                    search_val,
                    "{f} like '" + search_val + "%'",
                    "{f} like ?",
                    ('' + search_val + '%',),
                    u"{f} 以 {v} 开头")
        # endregion
        # region &s.field = *abc => field like '%abc'
        if search_str.startswith("*") and not search_str.endswith("*"):
            search_val = search_str[1:]
            return (SearchConditionParser.LIKE_END,
                    search_val,
                    "{f} like '%" + search_val + "'",
                    "{f} like ?",
                    ('%' + search_val,),
                    u"{f} 以 {v} 结尾")
        # endregion
        # 以波浪线为范围的
        # region &s.field = ~1~ or ~1,2,3~ => 相当于in(...),实际将转化为 field=1 or field=2 or filed=3
        if search_str.startswith("~") and search_str.endswith("~"):
            search_val = search_str[1:-1]
            vals = []
            sql = []
            param_sql = []
            mapping = []
            for val in search_val.split(","):
                vals.append(val)
                sql.append("{f} = '%s'" % val)
                param_sql.append("{f} = ?")
                mapping.append(val)
            return (SearchConditionParser.IN,
                    search_val,
                    " or ".join(sql),
                    " or ".join(param_sql),
                    tuple(mapping),
                    u"{f} 等于 %s" % u" 或 ".join(vals))
        # endregion
        # region &s.field = ~1 => field<1 小于
        if search_str.startswith("~") and not search_str.startswith("~=") and not search_str.endswith("~"):
            search_val = search_str[1:]
            if SearchConditionParser._int_chker(search_val) or SearchConditionParser._float_chker(search_val):
                return (SearchConditionParser.LESS_THAN,
                        search_val,
                        "{f} < " + search_val,
                        "{f} < ?",
                        (search_val,),
                        u"{f} 小于 {v}")
        # endregion
        # region &s.field = ~=1 => field<=1 小于等于
        if search_str.startswith("~=") and not search_str.endswith("~"):
            search_val = search_str[2:]
            if SearchConditionParser._int_chker(search_val) or SearchConditionParser._float_chker(search_val):
                return (SearchConditionParser.LESS_EQUALS,
                        search_val,
                        "{f} <= " + search_val,
                        "{f} <= ?",
                        (search_val,),
                        u"{f} 小于等于 {v}")
        # endregion
        # region &s.field = 1~ => field>1 大于
        if search_str.endswith("~") and \
                not search_str.endswith("=~") and \
                not search_str.startswith("~") and \
                not search_str.startswith("!~"):
            search_val = search_str[:-1]
            if SearchConditionParser._int_chker(search_val) or SearchConditionParser._float_chker(search_val):
                return (SearchConditionParser.GREATER_THAN,
                        search_val,
                        "{f} > " + search_val,
                        "{f} > ?",
                        (search_val,),
                        u"{f} 大于 {v}")
        # endregion
        # region &s.field = 1=~ => field>1 大于等于
        if search_str.endswith("=~"):
            search_val = search_str[:-2]
            if SearchConditionParser._int_chker(search_val) or SearchConditionParser._float_chker(search_val):
                return (SearchConditionParser.GREATER_EQUALS,
                        search_val,
                        "{f} >= " + search_val,
                        "{f} >= ?",
                        (search_val,),
                        u"{f} 大于等于 {v}")
        # endregion
        # region &s.field = 0~1 => field<0 and field>1
        if search_str.find("~") != -1 and \
                not search_str.startswith("~") and \
                not search_str.endswith("~") and \
                        search_str.find("=") == -1 and \
                        search_str.find("~~") == -1:
            search_val_arr = search_str.split("~")
            if len(search_val_arr) == 2:
                if (SearchConditionParser._int_chker(search_val_arr[0]) or \
                            SearchConditionParser._float_chker(search_val_arr[0])) and \
                        (SearchConditionParser._int_chker(search_val_arr[1]) or \
                                 SearchConditionParser._float_chker(search_val_arr[1])):
                    return (SearchConditionParser.INT_RANGE_G_L,
                            "%s,%s" % (search_val_arr[0], search_val_arr[1]),
                            "{f} > " + search_val_arr[0] + " and {f} < " + search_val_arr[1],
                            "{f} > ? and {f} < ?",
                            (search_val_arr[0], search_val_arr[1]),
                            u"{f} 大于 {v} 小于 {v1}")
        # endregion
        # region &s.field = 0=~=1 => field>=0 and field<=1
        if search_str.find("=~=") != -1:
            search_val_arr = search_str.split("=~=")
            if len(search_val_arr) == 2:
                if (SearchConditionParser._int_chker(search_val_arr[0]) or \
                            SearchConditionParser._float_chker(search_val_arr[0])) and \
                        (SearchConditionParser._int_chker(search_val_arr[1]) or \
                                 SearchConditionParser._float_chker(search_val_arr[1])):
                    return (SearchConditionParser.INT_RANGE_GE_LE,
                            "%s,%s" % (search_val_arr[0], search_val_arr[1]),
                            "{f} >= " + search_val_arr[0] + " and {f} <= " + search_val_arr[1],
                            "{f} >= ? and {f} <= ?",
                            (search_val_arr[0], search_val_arr[1]),
                            u"{f} 大于等于 {v} 小于等于 {v1}")
        # endregion
        # region &s.field = 0~=1 => field>0 and field=<1
        if search_str.find("~=") != -1:
            search_val_arr = search_str.split("~=")
            if len(search_val_arr) == 2:
                if (SearchConditionParser._int_chker(search_val_arr[0]) or \
                            SearchConditionParser._float_chker(search_val_arr[0])) and \
                        (SearchConditionParser._int_chker(search_val_arr[1]) or \
                                 SearchConditionParser._float_chker(search_val_arr[1])):
                    return (SearchConditionParser.INT_RANGE_G_LE,
                            "%s,%s" % (search_val_arr[0], search_val_arr[1]),
                            "{f} > " + search_val_arr[0] + " and {f} <= " + search_val_arr[1],
                            "{f} > ? and {f} <= ?",
                            (search_val_arr[0], search_val_arr[1]),
                            u"{f} 大于 {v} 小于等于 {v1}")
        # endregion
        # region &s.field = 0=~1 => field>=0 and field<1
        if search_str.find("=~") != -1:
            search_val_arr = search_str.split("=~")
            if len(search_val_arr) == 2:
                if (SearchConditionParser._int_chker(search_val_arr[0]) or \
                            SearchConditionParser._float_chker(search_val_arr[0])) and \
                        (SearchConditionParser._int_chker(search_val_arr[1]) or \
                                 SearchConditionParser._float_chker(search_val_arr[1])):
                    return (SearchConditionParser.INT_RANGE_GE_L,
                            "%s,%s" % (search_val_arr[0], search_val_arr[1]),
                            "{f} >= " + search_val_arr[0] + " and {f} < " + search_val_arr[1],
                            "{f} >= ? and {f} < ?",
                            (search_val_arr[0], search_val_arr[1]),
                            u"{f} 大于等于 {v} 小于 {v1}")
        # endregion
        # region &s.field = 1~~1 => 1 between 1 用于时间
        if search_str.find("~~") != -1:
            search_val_arr = search_str.split("~~")
            if len(search_val_arr) == 2:
                date_regx = "^\s*([12]\d{3})-(0{0,1}[0-9]|1{0,1}[012])-([012]{0,1}\d|3[01])\s+([01]{0,1}[0-9]|2[0-3]):[0-5]{0,1}[0-9]:[0-5]{0,1}[0-9]\s*$"
                if re.match(date_regx, search_val_arr[0]) and re.match(date_regx, search_val_arr[1]):
                    return (SearchConditionParser.DATE_BETWEEN,
                            "%s,%s" % (search_val_arr[0], search_val_arr[1]),
                            "({f} between '" + search_val_arr[0] + "' and '" + search_val_arr[1] + "')",
                            "({f} between ? and ?)",
                            (search_val_arr[0], search_val_arr[1]),
                            u"{f} 从 {v} 到 {v1}")
        # endregion

        return (0, "", "", "", tuple(), "")


class SearchItemInfo(object):
    def __init__(self, field, is_show, value):
        self.field = field
        self.is_show = is_show
        self.value = urllib.unquote(str(value))
        sep_pos = self.value.find("|")
        if sep_pos == -1:
            self.text = field
            self.search_str = self.value
        else:
            self.text = self.value[0:sep_pos]
            self.search_str = self.value[sep_pos:].lstrip("|")  # 切掉左边的第一个|
            if self.search_str.rfind("|") != -1:
                self.search_str = self.search_str[0:self.search_str.rfind("|")]

        self.type, self.search_val, self.sql_str, self.where_str, self.mapping, self.info = SearchConditionParser.parse(
                self.search_str)

        v, v1 = ("", "")
        if self.type == SearchConditionParser.INT_RANGE_G_L or \
                        self.type == SearchConditionParser.INT_RANGE_G_LE or \
                        self.type == SearchConditionParser.INT_RANGE_GE_L or \
                        self.type == SearchConditionParser.INT_RANGE_GE_LE or \
                        self.type == SearchConditionParser.DATE_BETWEEN:

            if self.type == SearchConditionParser.DATE_BETWEEN:
                arr = self.search_str.split("~~")
            elif self.type == SearchConditionParser.INT_RANGE_G_L:
                arr = self.search_str.split("~")
            elif self.type == SearchConditionParser.INT_RANGE_G_LE:
                arr = self.search_str.split("~=")
            elif self.type == SearchConditionParser.INT_RANGE_GE_L:
                arr = self.search_str.split("=~")
            elif self.type == SearchConditionParser.INT_RANGE_GE_LE:
                arr = self.search_str.split("=~=")
            v = arr[0]
            v1 = arr[1]
        else:
            v = self.search_val
            v1 = ""
        self.sql_str = self.sql_str.format(f=field, v=v, v1=v1)
        self.where_str = self.where_str.format(f=field, v=v, v1=v1)
        self.info = self.info.format(f=self.text, v=v, v1=v1)


def sort_str_parse(args_str):
    '''
    规则是:st.field=title|0&s.field1=title|1
    field只能是字母数字下划线组合
    st.表示是搜索条件,field是指参与排序的字段名,第一条|线的左边是titile(可省略),0表示asc正序排列,1表示desc倒序排列
    st.id=标识符|0：以字段id正序排列(asc),别名为:标识符
    sd.price=价格|1: 以字段price倒序排列(desc),别名为:价格
    sd.datetime=1: 以字段price倒序排列(desc),别名为:datetime
    如果有重复的值,以最后一个值为准
    :param args_str:搜索字符串,也就是url的request.querystring部分
    :return:[('field_name', 'title', 0), [('field_name', 'title', 0), [('field_name', 'title', 0)]
    '''
    if not args_str:
        return []
    sharp_pos = args_str.find("#")
    if sharp_pos != -1:
        args_str = args_str[0:sharp_pos]
    args_str = "&" + args_str.split("?")[-1].strip("&")  # 将字符串转换为标准的  &a=1&a=2&a=3模式
    # 用正则表达式获取到所有s.word.0=1,s.word.1=2,s.word=3
    args_list = re.findall("[&]+st\.([^=\.]*)\s*=\s*([^\|&]*)\|*([10])", args_str)
    search_group = OrderedDict()
    for word, sort_type, val in args_list:
        search_group[word] = (word.strip(), sort_type, val)
    return search_group.values()


class SortItemInfo(object):
    ASC = 0
    DESC = 1

    def __init__(self, field, title, sort_type):
        self.field = field
        self.text = title
        self.sort_type = SortItemInfo.ASC if sort_type == "0" else SortItemInfo.DESC
        self.sort_str = ("%s asc" if sort_type == "0" else "%s desc") % self.field
        pass


class SearchAdapter(object):
    sql_str = property(
        fget=lambda self: "" if len(self.sql_str_list) == 0 else "(%s)" % ") and (".join(self.sql_str_list))
    where_str = property(
        fget=lambda self: "" if len(self.where_str_list) == 0 else  "(%s)" % ") and (".join(self.where_str_list))
    sort_str = property(fget=lambda self: " , ".join(self.sort_str_list))

    def __init__(self, url,allow_fields=None):
        #allow_fields这里提一个过滤的机制,只有允许的参数才会被添加进去
        self.items = {}  # 所有 SearchItem
        self.sorts = []  # 所有 SortItem
        self.search_field_list = []
        self.sort_field_list = []
        self.sql_str_list = []
        self.where_str_list = []
        self.sort_str_list = []
        self.mapping = tuple()
        self.has_any_show = False
        for word, is_show, val in search_str_parse(url):
            if allow_fields:
                if word not in allow_fields:
                    continue
            if not word.replace("_", "").isalnum():  # 只能由数字和字母组成
                continue
            search_info = SearchItemInfo(word, is_show, val)
            self.sql_str_list.append(search_info.sql_str)
            self.where_str_list.append(search_info.where_str)
            self.mapping = self.mapping + search_info.mapping
            if search_info.is_show: self.has_any_show = True
            self.search_field_list.append(search_info.field)
            self.items[search_info.field] = search_info

        for word, title, sort_type in sort_str_parse(url):
            print "work",word
            if allow_fields:
                if word not in allow_fields:
                    continue
            if not word.replace("_", "").isalnum():  # 只能由数字和字母组成
                continue
            sort_info = SortItemInfo(word, title, sort_type)
            self.sort_str_list.append(sort_info.sort_str)
            self.sort_field_list.append(sort_info.field)
            self.sorts.append(sort_info)


if __name__ == "__main__":
    print search_str_parse("s.word.0=123123&s.word1.1=asdfasd&&s.word1=*asdfasd&&&&&")
    print SearchAdapter("s.word.0=123123&s.word1.1=asdfasd&&s.word1=*asdfasd&&&&&st.word=1").sort_str
