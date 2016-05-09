#-*- coding:utf-8 -*-
__version__='0.1'
from robot.api import logger
import re
class OlymKeywords(object):

    def split_data(self,value,fh=" "):
        '''
        切分数据,返回数组,例如:
        str=3.14.15

        |data split|str|

        :return ['3','14','15']
        '''
        if not fh:
            fh=" ";
        return value.split(fh)

    def re_search(self,str,Ls,Rs):
        '''
        通过正则查询结果

        str 被切的数据
        Ls  左边界
        Rs  右边界
        如有多个只取第一个
        Examples:

        | data cut `|` abcd `|` a `|` d                                           | # 返回结果是bc

        '''
        m=re.search( Ls+'(.*?)'+Rs,str)
        if m is not None:
            return m.group(1)
            logger.debug('return'+m.group(1))
        else:
            logger.info(str+' 没有结果,请检查上下边界')

if __name__ == '__main__':
    test=OlymKeywords().data_cut('a12345678b','aw','b')
    print test