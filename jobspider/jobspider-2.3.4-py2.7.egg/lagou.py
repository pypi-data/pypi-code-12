#!/usr/bin/python
# -*- coding:utf-8 -*-


from baseclass.base_spider import Base_Spider




class LG_Spider(Base_Spider):

    def __init__(self,sitename,*args):
        #do not add host
        super(LG_Spider,self).__init__(sitename,args)
	

    def parse(self,url):
        response = self.get_content(url,url_type='json')
        content = response['content']
        if hasattr(self,'total_pages'):
            self.total_pages = content["totalPageCount"]
        data_list = content['result']
        result = []
        for data in data_list:
            item = {}
            item['website'] = 'lagou'
            item['link'] = 'http://www.lagou.com/jobs/'+str(data['positionId'])+'.html'
            item['homepage'] =  'http://www.lagou.com/gongsi/'+str(data['companyId'])+'.html'
            item['title'] = data['positionName']
            item['company'] = data['companyName']
            item['salary'] = data['salary']
            item['date'] = data['createTime']
            result.append(item)
        return result



		

    def pages_parse(self,keyword):
        for page in xrange(1,2):
            if not isinstance(keyword,unicode):
                keyword = keyword.encode('utf8')
            url = 'http://www.lagou.com/jobs/positionAjax.json?px=new&gx=%E5%85%A8%E8%81%8C&city=%E5%8C%97%E4%BA%AC&first=true&'+'kd=%s&pn=%d'%(keyword,page)
            data = self.parse(url)
            yield data




if __name__ == "__main__":
    lg = LG_Spider('lagou')
    for item in lg.pages_parse('python'):
        print item


