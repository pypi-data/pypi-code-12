#coding:utf8

from bs4 import BeautifulSoup
import requests
try:
    from urllib.parse import urljoin
except:
    print("不支持python2,请切换python3.x版本")


#这段代码是python3用的!
#这是一段整站爬虫代码
def crawl(url,depth):
    urllist =[url]
    dizhi = urllist[0].split('.')[-2]
    all_data = []
    for i in range(depth):
        print ('正在抓取第%s层' % str(i+1) )
        newpages = set()
        for page in urllist:
            c= requests.get(page)
            soup=BeautifulSoup(c.text,'lxml')
            links=soup('a')
            for link in links:
                #如果href attrs的意思,是把所有的links弄成字典,那么如果href在里面的话,就把他接起来
                if ('href' in dict(link.attrs)):
                    #url 就把这个链接给拼接起来
                    url=urljoin(page,link['href'])
                #如果这个不到' 这个符号,就停止 (为什么要这样做?)
                if url.find("'")!=-1: continue

                #对于一些有#号的链接,就用#号分割,然后提取前面的就可以了
                url=url.split('#')[0]  # remove location portion
                if url[0:4]=='http':
                    if url not in urllist and dizhi in url:
                        # print ('成共添加',url,'数量:',len(newpages))
                        newpages.add(url)
        pages = newpages
        all_data.extend(list(newpages))    #把一抓取的数量添加进去
        print ('======')
    print ('本次5级抓取,共抓取 %s 个链接' % len(set(all_data)))
    return set(all_data)


def to_save(url,depth=30):
    try:
        all_data = crawl(url,depth)
        fl = open('urls.txt','w')
        for url in all_data:
            fl.write(url+'\n')
        fl.close()
    except:
        pass

if __name__ == '__main__':
    url = "http://www.zhangte.org"
    to_save(url)