# coding=utf8
from sys import argv


def long_arg(header, method, * extra_args):
    temp = argv
    for i in temp:
        index = temp.index(i)
        if i == header and len(temp) - 1 > index and not temp[index + 1].startswith("--"):
            return method(temp[index + 1], * extra_args)
    return False

short = {
    '--upload': '-u',
    '--stat': '-s',
    '--list': '-l',
    '--access': '-A',
    '--secret': '-S',
    '--space': '-P',
    '--help': '-h',
    '--del': '-e',
    '--download': '-d',
    '--private': '-p',
    '--subdom': '-b',
    '--link': '-k',
    '--plink': '-pk',
    '--version': '-v'
    }

map_target = {
    '--upload': '选择要上传的文件',
    '--stat': '查看文件状态',
    '--list': '文件列表',
    '--access': '修改或查看access key',
    '--secret': '修改或查看secret key',
    '--space': '修改或查看当前空间名',
    '--help': '帮助',
    '--del': '删除云文件',
    '--download': '下载文件',
    '--private': '下载私有文件(若无法下载则返回下载链接)',
    '--subdom': '设置或查看当前空间默认域名(7xiy1.com1.z0.glb.clouddn.com)',
    '--link': '返回下载文件的下载链接',
    '--plink': '返回私有空间文件下载链接',
    '--version': '当前版本号'
    }


