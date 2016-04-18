#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'WHB'



from baseclass.base_spider import Base_Spider



class ZL_Spider(Base_Spider):
    '''
    the website is qianchengwuyou,it is like lagou,
    no need ajax
    '''
    def __init__(self,website,*args):
        #no need any key except User-Agent
        super(ZL_Spider,self).__init__(website,args)

    def parse(self,url):
        soup = self.get_content(url)
        result = []
        tables = soup.find(id="newlist_list_content_table")
        if tables is not None:
            for table in list(tables.children):
                if table.name is None:
                    continue
                else:
                    item = {}
                    item['website'] = 'zhilian'
                    #print 'test',type(table),table.name
                    Trinfo = table.find('tr')
                    title = Trinfo.find('td','zwmc')
                    if title is not None:
                        item['link'] = title.find('a')['href']
                        item['title'] = title.find('a').text
                    Comp = Trinfo.find('td','gsmc')
                    if Comp is None:
                        continue
                    else:
                        item['homepage'] = Comp.find('a')['href']
                        item['company'] = Comp.find('a').text
                    intro = Trinfo.find('td','gzdd')
                    #item[u'介绍'] = intro.text if intro is not None else ''
                    date = Trinfo.find('td','gxsj')
                    item['date'] = date.text if date is not None else ''
                  #  for key in item:
                     #   print key,item[key]
                    result.append(item)
        return [item for item in result if item]

    def pages_parse(self,keyword):
        for page in xrange(1,2):
            url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=&kw=%s&sm=0&sg=654c99887ed049479fb08d6530323db0&p=%d&isfilter=0&fl=530&isadv=0&sb=1'%(keyword,page)
            data = self.parse(url)
            yield data



