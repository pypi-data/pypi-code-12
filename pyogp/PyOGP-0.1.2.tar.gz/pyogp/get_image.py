# todo need to codereview,
# todo need update bs version

# from boilerpipe.extract import Extractor
# from BeautifulSoup import BeautifulSoup as bs
#
# import re
# from PIL import Image
# from StringIO import StringIO
# import trollius
# from trollius import From
# import requests as r
#
# class ImageExtractor:
#
#     origin=''
#     response =''
#     loop = trollius.get_event_loop()
#
#     def __init__(self,response='',origin=''):
#         self.origin = origin
#         self.response = response
#
#         if self.origin != '':
#             if response =='':
#                 self.response = r.get(origin).text
#
#     def setresponse(response):
#         self.response= response
#
#     def setorigin(origin):
#         self.origin = origin
#
#     def _src_gather(self,src_list,tag_list):
#         img_src= list()
#         for li in src_list:
#             for att in li.attrs:
#                 att_tag, att_value = att
#                 for tag in tag_list:
#                     if tag in att_tag:
#                         if len(att_value) >0:
#                             img_src.append(self._image_path(li[att_tag]))
#         return img_src
#
#     def _image_path(self,path):
#         if 'http' not in path:
#             return '/'.join(self.origin.split('/')[0:3]) + path
#         else:
#             return path
#
#     def get_image(self):
#         if self.response == '':
#             print "No input data"
#             return ''
#         tag_list = ['src','img']
#         extractor = Extractor(extractor='ArticleExtractor', html=self.response)
#         dump = bs(extractor.getHTML())
#         head = dump.find('body').childGenerator().next()
#         tag,value = head.attrs[0]
#         real = bs(self.response).find(attrs={tag:value})
#         img_list = real.findAll(re.compile('^img'))
#         return self._src_gather(img_list,tag_list)
#
#
#     @trollius.coroutine
#     def _image_scrap(self,image_src, image_rank):
#         im = Image.open(StringIO(r.get(image_src).content))
#         size = im.size[0]*im.size[1]
#         image_rank.append([image_src] + [size])
#
#     def image_rank(self, img_list):
#         image_rank = list()
#         f  = trollius.wait([self._image_scrap(image_src,image_rank) for image_src in img_list])
#         self.loop.run_until_complete(f)
#         image_rank = sorted(image_rank,key=lambda x : x[1],reverse=True)
#         return image_rank
#
#
