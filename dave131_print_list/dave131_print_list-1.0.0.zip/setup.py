from distutils.core import setup #从python发布工具中导入"setup"函数

setup(
    name         = 'dave131_print_list',
    version      ='1.0.0',
    py_modules   =['dave131_print_list'],#将模块的元数据与setup函数的参数关联
    author       ='LiYuan',
    author_email ='364498159@qq.com',
    url          ='qq.com',
    description  ='a simple printer of nester lists',
    )
