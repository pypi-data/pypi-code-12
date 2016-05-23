"""这是一个用于测试Python打包流程的程序,里面包含了一个print_lol的函数.这个函数的作用就是打印嵌套的列表"""
import sys


def print_lol(the_list,indent=False, level=0,file_out=sys.stdout):
    """递归打印列表中的所有数据,可打印嵌套的列表,the_list:需要打印的内容 indent:默认为false,不启动缩进 level:首行缩进级别 file_out:默认为sys.stdout"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,file=file_out)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end = '',file=file_out)
            print(each_item,file=file_out)
            
