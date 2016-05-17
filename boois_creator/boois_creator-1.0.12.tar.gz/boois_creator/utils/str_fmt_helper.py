# coding=utf-8
import re

#转驼峰法命名,第一个字母被转大写了  如cover_img  => CoverImg   一般用于类名
def camel(txt):
    if not txt:
        # print "=="
        return ""
    txt = re.sub("(_[a-z])", lambda t: t.group(1).lstrip("_").upper(), txt).lstrip("_")
    return txt[0].upper() + "".join(txt[1:])
#转驼峰法命名,第一个字母不转大写 如app_key=>appKey   一般用于java的变量
def camel_lower(txt):
    if not txt:
        # print "=="
        return ""
    return re.sub("(_[a-z])", lambda t: t.group(1).lstrip("_").upper(), txt).lstrip("_")
if __name__ == '__main__':
    print camel("a_bc_de")
    print camel("a")

