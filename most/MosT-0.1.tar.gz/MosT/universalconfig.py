# -*- coding: utf-8 -*-
__author__ = 'tangke'
import os
import ConfigParser

from bs4 import BeautifulSoup
import xlrd

from MosT.caseobject import CaseObject
from datacontext import DataContext


def read_database_config():
    config_path = absolute_file_name('database.xml')
    if os.path.exists(config_path):
        _soup = BeautifulSoup(open(config_path, 'r'), 'lxml')
        databases = _soup.find_all('database')
        for database in databases:
            if database.find('env').get_text() != DataContext.env:
                continue
            name = database.find('name')
            _temp_dict = {}
            for other_config in name.find_next_siblings():
                _temp_dict[other_config.name] = int(
                    other_config.get_text()) if other_config.get_text().isdigit() else other_config.get_text()
            DataContext.database_dict[name.get_text()] = _temp_dict
    else:
        raise Exception('不存在这样的数据库配置文件:' + str(config_path))


def read_request_obj():
    if os.path.exists(absolute_file_name('case.xlsx')):
        xls_path = absolute_file_name('case.xlsx')
    elif os.path.exists(absolute_file_name('case.xls')):
        xls_path = absolute_file_name('case.xls')
    else:
        raise Exception('不存在用例文件')
    xls_content = xlrd.open_workbook(xls_path)
    sheets = xls_content.sheets()
    column_names = sheets[0].row_values(0)
    for i in range(1, sheets[0].nrows):
        row_values = sheets[0].row_values(i)
        caseobject = CaseObject()
        for key, value in zip(column_names, row_values):
            setattr(caseobject, key, value)
        print 2
        DataContext.case_list.append(caseobject)


def read_global_config(env='test'):
    if os.path.exists(absolute_file_name('setting.conf')):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(absolute_file_name('setting.conf'))
        for key, value in config_parser.items(env):
            if not hasattr(DataContext, key):
                setattr(DataContext, key, value)
    else:
        raise Exception('不存在全局配置文件setting.conf')


def absolute_file_name(filename):
    return os.path.join(os.getcwd(), filename)


# if __name__ == '__main__':
#     # read_request_obj()
#     # print  DataContext.case_list[0].casename
#     read_global_config()
#     print DataContext.fronted_url
