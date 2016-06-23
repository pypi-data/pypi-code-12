# -*- coding: utf-8 -*-
#文件操作相关的函数
import datetime,time,random
import os,math
from django.conf import settings


def get_new_upload_dir():
    '创建新的上传目录,返回格式/2011/08/12'
    d = datetime.datetime.now()
    return d.strftime('%Y/%m/%d/')

def get_new_filename(filename,default_ext='.jpg'):
    '返回新的文件名,利用Unix时间戳'
    f,ext=os.path.splitext(filename)
    if not ext:
        ext=default_ext
    return '%s%s%s'%(int(float(time.time()*1000)),random.randint(0,99),ext)

def get_file_ext(filename):
    '''得到文件的扩展名'''
    f,ext=os.path.splitext(filename)
    ext = ext.replace('.','')
    return ext

def get_file_size(filename,unit='kb'):
    '''得到文件大小，单位可以是GB，MB，KB，其它单位均为B'''
    size=0
    unit=unit.lower()
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        if unit=='kb':
            size=size/1024
        elif unit=='mb':
            size=math.floor(size*100/1024/1024)/100
        elif unit=='gb':
            size=math.floor(size*100/1024/1024/1024)/100

    return size

def get_new_upload_file_info(file):
    '''
    根据已有文件信息返回上传文件信息,其中需要用到django的settings.py里定义一个UP_DIR的变量，指定上传文件的路径
    '''
    #获取上传文件的相对路径信息
    path= get_new_upload_dir()

    up_dir = settings.UP_DIR+'date/'
    up_url = settings.UP_URL + 'date/'
    #获取上传文件的真实路径信息
    real_path = os.path.join(up_dir,path).replace('\\','/')
    #如果真实路径不存在,则创建
    if not os.path.exists(real_path):
        os.makedirs(real_path)
        #获取新文件名称
    filename = get_new_filename(file)
    #获取新文件的相对路径及名称
    new_file = os.path.join(path,filename).replace('\\','/')
    #小图片相对路径
    small_new_file = os.path.join(path,'s' + filename).replace('\\','/')
    #中图片相对路径
    middle_new_file = os.path.join(path,'m'+filename).replace('\\','/')
    #获取新文件的绝对路径及名称
    real_file = os.path.join(up_dir,new_file).replace('\\','/')
    #小图片绝对路径
    small_real_file = os.path.join(up_dir,small_new_file).replace('\\','/')
    #中图片绝对路径
    middle_real_file = os.path.join(up_dir,middle_new_file).replace('\\','/')

    new_file = up_url + new_file
    middle_new_file = up_url + middle_new_file
    small_new_file = up_url + small_new_file

    return {
        'new_file' : new_file,
        'real_file' : real_file,
        'small_new_file':small_new_file,
        'small_real_file':small_real_file,
        'middle_new_file':middle_new_file,
        'middle_real_file':middle_real_file
        }