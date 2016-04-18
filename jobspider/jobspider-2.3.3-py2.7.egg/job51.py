#!/usr/bin/python
# -*- coding:utf-8 -*-


from baseclass.base_spider import Base_Spider
from baseclass.utils.setcolor import *


class Job51_Spider(Base_Spider):
    '''
    the website is qianchengwuyou,it is like lagou,
    no need ajax
    '''
    def __init__(self,website,*args):
        super(Job51_Spider,self).__init__(website,args)


    def parse(self,url):
        headers = {
            'Host': 'www.search.51job.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
            'Cookie': 'guid=14465584429375700076; slife=compfans%3D1%257C0%257C0%257C0; search=jobarea%7E%60010000%7C%21ord_field%7E%600%7C%21list_type%7E%600%7C%21recentSearch0%7E%602%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA01%A1%FB%A1%FA99%A1%FB%A1%FApython%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1452781332%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch1%7E%602%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA01%A1%FB%A1%FA99%A1%FB%A1%FAAnroid%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1452781220%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch2%7E%602%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA01%A1%FB%A1%FA99%A1%FB%A1%FApython%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1452780011%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch3%7E%602%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAAnroid%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1452781294%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21recentSearch4%7E%602%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FApython%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1452781317%A1%FB%A1%FA0%A1%FB%A1%FA%7C%21; guide=1; collapse_expansion=1; nolife=fromdomain%3D; ps=us%3DCzFUPVIyBi5RMQ1jBmtWewc1CzlVZVYtBjFUPwg3BXlbYlM8B2BXYwBmWz9XM1ZmV2RWYwQ0BWQANwUrXDAHVAtmVDhSVA%253D%253D; 51job=cenglish%3D0',
        }
        soup = self.get_content(url)
        #print soup
        try:
            resultlist = soup.find(id="resultList").find_all("div",class_='el')[1:]
        except AttributeError:
            print red('cookie may be invalid,pls check the cookie of webinfo.cfg')
        #print resultlist
        data = []
        for el in resultlist:
            item = {}
            #print el
            item['website'] = '51job'
            item['title']=el.find('p','t1').find('a').text
            item['link'] = el.find('p','t1').find('a')['href']
            item['company'] = el.find('span','t2').find('a').text
            item['homepage'] = el.find('span','t2').find('a')['href']
            item['salary'] = el.find('span','t4').text
            item['date'] = el.find('span','t5').text
            data.append(item)
        return data

    def pages_parse(self,keyword):
        for page in xrange(1,2):
            url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=010000%2C00&district=000000&funtype=0000&industrytype=00&issuedate=9&providesalary=99&' + \
                  'keyword=%s&keywordtype=0&curr_page=%d&lang=c&stype=2'%(keyword,page) + \
                  '&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=01&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&fromType=14&dibiaoid=0'
            data = self.parse(url)
            yield data





