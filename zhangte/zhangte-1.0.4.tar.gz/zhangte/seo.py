#coding:utf8
import requests
from zhangte.base import *
from urllib.parse import quote
from bs4 import BeautifulSoup
from Levenshtein import *

# 获取到调用其的脚本的路径
# PATH = os.path.abspath(os.path.dirname(inspect.stack()[1][1]))

class Baidu(Base):


    serp_url_reg = re.compile('<a target="_blank" href=".+?" class="c-showurl".+?">(.+?)</a>|<span class="c-showurl">(.+?)</span>')     #获取搜索结果的url
    rn = 50 #查询排名多少的网站
    pn = 0  #第几页,假如是查询前100名,就写50,前150名,就写100
    VISITS_LOG_PATH = '/data/visits_log/'
    RANK_SCORE = [
        2.856,
        1.923,
        1.020,
        0.814,
        0.750,
        0.572,
        0.401,
        0.441,
        0.553,
        0.670,
    ]

    #百度实时推送
    def tui(self,domain,token,urls):
        '''百度实时推送,传入域名,token,以及urls(直接read出来的格式)'''
        api = "http://data.zz.baidu.com/urls?site={domain}&token={token}".format(domain=domain,token=token)
        headers = {'User-Agent': 'curl/7.12.1','Content-Type':'text/plain'}
        r = requests.post(api, headers=headers,data = urls)
        print (r.text)


    #百度搜索源代码
    def baidu_serp(self,kw,skip=False):
        ''' 获取SERP搜索源代码'''
        kw = quote(kw)
        while 1:
            url =  'https://www.baidu.com/s?wd=%s&rn=%s' % (kw,50)
            html = curl(url).text
            if '<img src="http://verify.baidu.com/' in html:
                if skip:
                    return None
                print ('captcha')
                time.sleep(600)
                continue
            else:
                break
        return html


    #百度搜索结果url
    def baidu_serp_urls(self,kw, skip=False,T=False):
        '''获取搜索结果的urls,如果有百度新闻的页面,可能排名会误差1位,一般都比较准
        T 参数,默认是False,默认不获取真实url,因为这样效率比较低
        当然如果是一些外推网址要查排名的话,肯定是需要获取真实url地址!
        '''
        html = self.baidu_serp(kw)
        soup = BeautifulSoup(html,"lxml")
        urls = []

        #获取真实的url
        if T:
            soups = soup.select("h3")
            for soup in soups:
                try:
                    url = soup.select("a")[0].get("href")
                    header = requests.head(url).headers
                    urls.append(header['location'])
                except:
                    urls.append(url)

        else:
            for soup in re.findall(self.serp_url_reg,html):
                for url in soup:
                    if url != "":
                        urls.append(re.sub(re.compile("&nbsp;|</?b>"),'',url))
        return urls


    #百度收录
    def index(self,url):
        """查询百度收录,收录1,未收录0"""
        html = self.baidu_serp(url)
        if '<div class="content_none">' in html:
            return 0
        else:
            return 1

    #百度排名
    def rank(self,kw, host=None,T=False,lp=None):
        if not host and not lp:
            return False
        else:
            urls = self.baidu_serp_urls(kw,T)
            if host:
                host = host.replace("http://","")
                for pos, url in enumerate(urls, 1):
                    if host in url:
                        return pos, url
                return -1, '-'
            elif lp:
                for pos, url in enumerate(urls, 1):
                    if '...' not in url:
                        if lp==url:
                            return pos
                    else:
                        start, end = url.split('...')
                        if lp.startswith(start) and lp.endswith(end):
                            return pos
                return -1

    #页面相似度检测
    def Similar(self,url,url2):
        from pyquery import PyQuery as pq
        html1 = pq(url1).text()
        html2 = pq(url2).text()
        print (ratio(html1, html2))