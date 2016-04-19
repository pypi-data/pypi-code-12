#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
run spider in two different ways

it can run in single spider ,selected from BYR,Lagou,Zhilian,51Job or
run in multiprocessing


Default,the data that spider crawls will be stored into json file ,of course,you can
store into MySQL,excel or redis by setting store type.

"""

import os
from multiprocessing import Pool,Manager

from byr import BYR_Spider
from lagou import LG_Spider
from zhilian import ZL_Spider
from job51 import Job51_Spider
from dajie import DJ_Spider

from baseclass.utils.store_data import Job_Data
from baseclass.utils.setcolor import *


class Spider():

    spiders = {
        'byr':BYR_Spider('byr','X-Requested-With','Host','Referer'),
        'lagou':LG_Spider('lagou'),
        'zhilian':ZL_Spider('zhilian'),
        '51job':Job51_Spider('51job','Host','Cookie'),
         'dajie':DJ_Spider('dajie','X-Requested-With','Host','Referer','Cookie')
               }

    def __init__(self,keyword,store_type='json'):
        self.keyword = keyword
        self.store_type = store_type

    def get_single_data(self,spiname):
        self.spider = self.spiders[spiname]
        data = self.spider.pages_parse(self.keyword)
        return data

    def single_run(self,spiname):
        db = Job_Data(self.store_type)
        for data in self.get_single_data(spiname):
			db.store(data)

    def single_print(self,spiname):
        for data in self.get_single_data(spiname):
            for item in data:
                for key,value in item.items():
                    print "%s : %s" %(key,value),
                print '\n'

    def multi_run(self,spiname):
        print spiname
        self.single_run(spiname)

    def print_output(self,spiname):
        #In Linux,it will print data with colored
        for data in self.get_single_data(spiname):
            for item in data:
                for key,value in item.items():
                    if not isinstance(key,unicode):
                        key = key.encode('utf8')
                    if not isinstance(value,unicode):
                        value = value.encode('utf8')
                    if os.name == 'posix':
                        try:
                            print '{0}:{1}'.format(red(key),value),
                        except UnicodeEncodeError :
                            key,value = key.encode('utf8'),value.encode('utf8')
                            print '{0}:{1}'.format(key,value)
                        else:
                            print '{0}:{1}'.format(key,value),
                    else:
                        try:
                            print '{0}:{1}'.format(key,value),
                        except UnicodeEncodeError :
                            key,value = key.encode('utf8'),value.encode('utf8')
                            print '{0}:{1}'.format(key,value)
                print '\n'

    def get_data(self,spiname):
        select = raw_input('you want put data into terminal or json(write ter or json):')
        if select == 'terminal':
            self.print_output(spiname)
        elif select == 'json':
            self.single_run(spiname)
        else:
            print 'your input is incorrect,it must be terminal or json'



def crawl(spi,lock,store_type):
    #get the spider object,when storing data,it will
    spider = Spider('python',store_type)
    #when storing data to json or database,should set lock in order to protecting the data
    lock.acquire()
    try:
        spider.multi_run(spi)
    finally:
        #the subprocess must release the resource whatever it has finished successfully or not.
        lock.release()


def producer(store_type='json'):
    """
    In this spider,we can use multiprocessing to crawl job data from
    several different website.
    It can save a lot time by using multiprocessing.and this usage is
    very simple,efficient and pythonic.
    :param:store_type, the format you store the data ,it can be MySQL,json file,excel and redis.

    """
    lock = Manager().Lock()
    p = Pool()
    sites = ['zhilian', '51job','byr','lagou','dajie']
    for site in sites:
        p.apply_async(crawl,args=(site,lock,store_type))
    p.close()
    p.join()


if __name__=="__main__":
	spider = Spider('python')
	spider.single_run("lagou")
	#producer(store_type='MySQL')





