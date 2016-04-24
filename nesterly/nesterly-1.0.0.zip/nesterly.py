'''这是函数功能是空格输出需要输出的内容'''
def print_lol(listed,indent=0,level=0,fn=sys.stdout):
    '''参数意义：列表，是否缩进，第一个缩进多少，指定是输出到其他还是默认的标准输出，也就是输出到屏幕'''
    for i in listed:
        if isinstance(i,list):
            print_lol(listed,indent,level,fn)
        else:
            if indent:
                for q in range(level):
                    print('\t'.end='',file=fn)
            print(i,file=fn)
