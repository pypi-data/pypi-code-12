#coding:utf-8

import os
import imp
import traceback

__author__ = 'Feng Lu'


def load_services(app, serv_name):
    """
    加载service
    @param name string:插件相对services的命名空间
    @return dict:
    """
    names = {}
    modules = []
    func = None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mod_dirs = [os.path.join(base_dir, "services")]
    for mod_dir in mod_dirs:
        if not os.path.isdir(mod_dir):
            continue
        for fn_ in os.listdir(mod_dir):
            if fn_.startswith('_'):
                continue
            if fn_.endswith('.py') and not fn_.startswith("_sys_"):
                extpos = fn_.rfind('.')
                if extpos > 0:
                    _name = fn_[:extpos]
                else:
                    _name = fn_
                names[_name] = os.path.join(mod_dir, fn_)
    for name in names:
        try:
            # 模块的加载mod_dirs一定是一个list类型数据，否则执行失败
            fn_, path, desc = imp.find_module(name, mod_dirs)
            mod = imp.load_module(name, fn_, path, desc)
        except:
            print traceback.format_exc()
            continue
        modules.append(mod)
    base_service = None
    for mod in modules:
        for attr in dir(mod):
            if attr.startswith('_'):
                continue
                # 将加载的模块存放到字典里面
            if callable(getattr(mod, attr)):
                obj = getattr(mod, attr)
                # 不加flask上下文这里执行不了
                with app.app_context():
                    if attr == "BaseService":
                        base_service = obj
                        continue
                    if not attr.endswith('Service') or attr.replace('Service', '').lower() != serv_name:
                        continue
                    try:
                        func = obj
                    except:
                        print traceback.format_exc()
                        continue
    if not func:
        app.logger.warn("service for %s is not found use baseService instead" % serv_name)
    return func or base_service