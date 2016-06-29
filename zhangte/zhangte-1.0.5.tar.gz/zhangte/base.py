#coding:utf8
import re
import os
import datetime
from dateutil.parser import parse
import pymysql as MySQLdb


class Base():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    #去除掉所有的html标签
    def cuthtml(self,content,P=0):
        if P == 0:
            p2 = re.compile(r'</?\w+[^>]*>|</?(a|p style|blockquote)[^>]*>|(http.+?html)|&.*?;')
        else:
            p2 = re.compile(r'</?[^(/?p|br)]\w+[^>]*>|</?(a|p style|blockquote)[^>]*>|(http.+?html)|&.*?;')  #包含p,br等标签
        return p2.sub('',content) #去除所有的html代码

    #获取字典cookie的方法
    def get_cookies(self,cookie):
        '''
        处理cookie的函数,把cookie处理成字典
        '''

        cookies = {}
        for cookie in cookie.split('; '):
            cookie = cookie.split('=')
            cookies[cookie[0]]=cookie[1]
        return cookies


    #计算时间的函数
    def today(self,i = 0):
        return datetime.date.today() - datetime.timedelta(days=i)

    #传入第一天和第二天 返回一个整数的函数
    def day_cha(self,day1,day2):
        '''day1 和 day2都是要str格式,会返回一个整数,计算这2个的时间差'''
        return (parse(day1) - parse(day2)).days






#链接sql,并且一些简单的操作
class Mysql():

    def __init__(self,db,host="127.0.0.1",user="root",passwd="zhangte"):
        self.conn = MySQLdb.connect(host=host,user=user,passwd=passwd,port=3306,db = db,charset='utf8') #链接mysql
        self.cursor = self.conn.cursor() #创建游标

    #传入sql语句就执行
    def exeSQL(self,sql):
        '''把SQL语句传进去，直接进行提交'''
        try:
            print("exeSQL: " + sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except:
           self.conn.rollback()
        return self.cursor

    #关闭sql
    def closesql(self):
        return self.conn.close()



def curl(url,allow_redirects=True,timeout=30,**kwargs):
        '''
        1. 随机浏览器头
        2. 可以传入参数cookies,格式是cookies = cookie (注意,变量不要加s)
        3. 传入data参数,自动切换成post的方法
        4. 可以设置是不是要重定向 allow_redirects
        5. 也是可以设置超时时间,timeout
        6. 其他的使用方式和requests类似
        7. 遇到超时的网站会自动尝试链接2次
        '''

        from zhangte import ua
        import requests
        from requests.exceptions import ConnectTimeout,ConnectionError

        #如果没有自定义头,就我们来自定义,这个浏览器头有点问题,先观察一下
        # if "headers" not in kwargs:
        #     headers = ua.pc()
        headers ={
        "User-Agent":"'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'"
                    }
        #如果cookie存在参数里面,就对cookie进行处理
        if "cookies" in kwargs:
            if "; " in kwargs['cookies']:
                kwargs['cookies'] = Base().get_cookies(kwargs['cookies'])

        for i in range(3):
            try:
                if "data" not in kwargs:
                    return requests.session().get(url,headers = headers,allow_redirects=allow_redirects,timeout=timeout,**kwargs)
                else:
                    return requests.post(url,headers = headers,allow_redirects=allow_redirects,timeout=timeout,**kwargs)
            except ConnectTimeout as err:
                print ('链接超时,再次链接尝试')
                continue
            except ConnectionError as err:
                print ('链接错误(可能是国外网站)')
                break





if __name__ == '__main__':
    test()