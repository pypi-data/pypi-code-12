# -*- coding: utf-8 -*-
#html代码相关的函数
import re
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup, NavigableString

def strip_tags(html, valid_tags=[],remove_tags=['script','style'],clear_property_tags=[]):
    soup = BeautifulSoup(html)
    for tag in soup.findAll(True):
        if not tag.name in valid_tags:
            s = ""
            for c in tag.contents:
                c=unicode(c)
                if c:
                    if not isinstance(c, NavigableString):
                        c = strip_tags(c, valid_tags,remove_tags)
                    if not tag.name in remove_tags:
                        if tag.name in clear_property_tags:
                            s += u"<%s>%s</%s>"%(tag.name,c,tag.name)
                        else:
                            s += unicode(c)

            tag.replaceWith(s)
    return soup


def html2js(content,format='string'):
    '''将html代码转换成js代码'''
    import re

    tab = '    '
    format = 'array'

    html = content\
           .replace('\r', '')\
           .replace('\n', '')\
           .replace('"', r'\"')\
           .replace('\'', r'\'')

    return html


def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?[\w+^(img)][^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    return s




def get_image_urls(content):
    '''得到html代码中的所有图片地址'''
    str=r'''<img\b[^<>]*?\bsrc[\s\t\r\n]*=[\s\t\r\n]*["']?[\s\t\r\n]*([^\s\t\r\n"'<>]*)[^<>]*?/?[\s\t\r\n]*>'''
    #str='src="(.*?)\.jpg"'
    reObj=re.compile(str,re.IGNORECASE)
    allMatch=reObj.findall(content)
    if allMatch:
        return allMatch
    else:
        return []


if __name__ == '__main__':
    str =u'''
    <div style="width:92%;margin-right:auto;margin-left:auto;margin-bottom:auto;"><div> &nbsp;</div> <div> <section class="135editor" data-color="rgb(128, 177, 53)" data-custom="rgb(128, 177, 53)" data-id="1482" style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; color: rgb(62, 62, 62); font-family: 微软雅黑; font-size: 16px; line-height: 25.6px; border: 0px none; word-wrap: break-word !important;"> <section style="margin: 0px; padding: 5px; max-width: 100%; box-sizing: border-box; word-wrap: break-word !important; border: 5px solid rgb(128, 177, 53);"> <section style="margin: 0px; padding: 15px 20px; max-width: 100%; box-sizing: border-box; word-wrap: break-word !important; border: 1px solid rgb(128, 177, 53);"> <p style="margin: 0px; padding: 0px; max-width: 100%; clear: both; min-height: 1em; color: rgb(128, 177, 53); text-align: center; border-bottom-width: 1px; border-bottom-style: solid; border-color: rgb(128, 177, 53); box-sizing: border-box !important; word-wrap: break-word !important;"> <span style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; font-size: 20px;"><strong style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important;">青岛地铁最新照片来袭！</strong></span></p> <section class="135brush" data-style="color:#A50003;text-align:center;font-size:18px" style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; word-wrap: break-word !important; color: rgb(128, 177, 53); text-align: center;"> <p style="margin: 0px; padding: 0px; max-width: 100%; clear: both; min-height: 1em; text-align: left; box-sizing: border-box !important; word-wrap: break-word !important;"> &nbsp;</p> <p style="margin: 0px; padding: 0px; max-width: 100%; clear: both; min-height: 1em; text-align: left; box-sizing: border-box !important; word-wrap: break-word !important;"> <span style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; color: rgb(0, 0, 0);">最近这段时间</span><span style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; color: rgb(0, 0, 0); line-height: inherit;">地铁M3线北段正在冷运行中，各种细节图也被万能的网友们频频曝出，这次连&ldquo;地铁票&rdquo;都被放出来了。矮马，真的好期待坐坐咱青岛银自己的地铁呢~</span></p> <div> &nbsp;</div> </section> </section> </section> <section style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; word-wrap: break-word !important; width: 0px; height: 0px; clear: both;"> &nbsp;</section> </section> </div> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">咱青岛地铁的车厢长这样，从这个角度看跟北京地铁相似度&asymp;<span style="font-family: 'Times New Roman';">100%</span>啊&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q2.jpg" style="border: 0px; max-width:100%;" <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q3.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">地铁车厢站点指示&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q3-50.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">再偷偷曝下地铁驾驶室&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q3-51.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">近日，网友<span style="font-family: 'Times New Roman';">@</span>青岛新摄会在微博上发布了一张疑似青岛地铁单程票，并发文称：&ldquo;有浓浓的青岛味，很温馨，期待坐乘！&rdquo;&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q4.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">千呼万唤的青岛地铁<span style="font-family: 'Times New Roman';">3</span>号线北段<span style="font-family: 'Times New Roman';">9</span>月已开始试运行，待各项运行指标达标后，将开始载客试运营，届时青岛将进入令人振奋的&ldquo;地铁时代&rdquo;。</span></p> <div> &nbsp;</div> <div> <p style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; clear: both; min-height: 1em; white-space: pre-wrap;"> &nbsp;</p> <section class="article135" style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; font-family: 微软雅黑;"> <section class="135editor" data-id="85671" style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; color: rgb(62, 62, 62); font-size: 16px; line-height: 25.6px; border: 0px none; text-align: center; word-wrap: break-word !important;"> <section style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; text-decoration: inherit; color: rgb(255, 255, 255); border-color: rgb(128, 177, 53); display: inline-block; word-wrap: break-word !important;"> <section style="margin: 0px; padding: 10px; max-width: 100%; box-sizing: border-box; word-wrap: break-word !important; line-height: 1.2em; border: 1px solid rgb(128, 177, 53);"> <p style="margin: 0px; padding: 0px; max-width: 100%; clear: both; min-height: 1em; text-align: left; box-sizing: border-box !important; word-wrap: break-word !important;"> <span style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; font-size: 24px; color: rgb(146, 208, 80);"><strong style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box !important; word-wrap: break-word !important; color: inherit;">青岛地铁360&deg;大曝光</strong></span></p> <div> &nbsp;</div> </section> </section> <section style="margin: 0px; padding: 0px; max-width: 100%; box-sizing: border-box; word-wrap: break-word !important; width: 0px; height: 0px; clear: both;"> &nbsp;</section> </section> </section> </div> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">刷卡进站的地方长这样&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q4-50.jpg" style="border: 0px; max-width:100%;" <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q4-51.jpg" style="border: 0px; max-width:100%;" <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q4-52.jpg" style="border: 0px; max-width:100%;" <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q5.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">进站后的大厅长这样&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q5-50.jpg" style="border: 0px; max-width:100%;" <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q5-51.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">里面安装了电梯&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q6.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">青岛地铁候站区长这样&darr;&darr;&darr;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <img alt="" src="http://bdapp.bandao.cn/bandao/uploads/allimg/151016/114-151016154Q6-50.jpg" style="border: 0px; max-width:100%;" <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-size:20px;"><strong><span style="font-family: 宋体;">点<span style="font-family: 'Times New Roman';">zan</span>，企盼早日坐上青岛牌地铁！</span></strong></span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">&nbsp;</span></p> <p style="margin: 5px 0px; line-height: 24px; color: rgb(0, 0, 0); font-family: sans-serif; font-size: 16px;"> <span style="font-family: 宋体; font-size: 17px;">感谢图片作者<span style="font-family: 'Times New Roman';">@</span>青雨不无情、<span style="font-family: 'Times New Roman';">@</span>青岛新摄会</span></p> <div> &nbsp;</div> </div>
     '''
    print('source=',str)

    data=strip_tags(str)
    print(data.contents)
