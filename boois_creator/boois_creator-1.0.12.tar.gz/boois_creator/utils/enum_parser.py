#coding:utf-8
class EnumParser(object):
    @staticmethod
    def parse(txt):
        arr=txt.split("|")

        is_more=False
        fields=[]
        for i,val in enumerate(arr):
            if i==0 and val=="+":
                is_more=True
                continue
            one=val.split(":")
            if len(one)==3:
                fields.append((one[0],one[1],one[2]=="y"))
            elif len(one) == 2:
                fields.append((one[0], one[1],False))
            else:
                print "[WARNING] %s 语法错误,请检查" % val

        return is_more,fields
if __name__ == '__main__':
    print EnumParser.parse('''+|1:中文:y|2:英文:n|3:英文"''')
    print EnumParser.parse('''1:中文:y|2:英文:n|3:英文"''')
