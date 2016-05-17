# coding=utf-8
#task,生成任务,指的是生成一个文件或者目录的任务
'''
is_static :
    is_path:
    not is_path:
not is_static:

'''
class Task(object):
    def __init__(self):
        self.is_static=None
        self.src=None
        self.is_path=None
        self.out_path=None
        self.tpl=None
if __name__ == '__main__':
    pass