#-*- coding:utf-8 -*-
__version__='0.1'
from robot.api import logger
import re
import datetime,time
import random
class OlymKeywords(object):

    def split_data(self,value,fh=" "):
        '''
        切分数据,返回数组,例如:
        str=3.14.15

        |split data|str|

        return ['3','14','15']
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

        | re search | abcd | a | d                                           | # 返回结果是bc

        '''
        m=re.search( Ls+'(.*?)'+Rs,str)
        if m is not None:
            return m.group(1)
            logger.debug('return'+m.group(1))
        else:
            logger.info(str+' 没有结果,请检查上下边界')

    def Get_Time_Modified(self,addnumber='0'):
        '''
        获得当前日期. 可以通过参数加减日期

        :param addnumber: 加减天数, 默认是今天

        :return: str

        '''
        d1 = datetime.date.today()
        d2=d1+datetime.timedelta(int(addnumber))
        return d2

    def Get_Timestamp(self):
        '''
        获得时间戳

        :return: str , 保证数字唯一
        如: 1464921407
        '''
        res=time.time()
        return str(int(res))

    def Random_Num(self,start=1,stop=10000,times=1):
        '''
        随机产生一个随机数

        :param start 随机数最小值 默认是1

        :param stop  随机数最大值 默认是10000

        :param times 倍数,用于凑整随机, 默认是1

        :return: str
        如:

        Random Num | start=1 | stop=10 | times=100  返回 100 ~ 1000 的随机 返回结果为 100 或 200 等
        '''
        num=random.randint(int(start),int(stop))
        num=num*times
        logger.debug('生成随机数:'+str(num))
        return num

    def Random_Choice(self,sequence):
        '''
        随机选择有序类型(如数组)中的某一个值

        :param sequence 有序类型.
        :return 根据你传的参数决定类型
        如:

        Random Choice | ['a','b','c']  返回 a,b,c中的随机一个

        Random Choice | hello    返回h,e,l,l,o 中的随机一个
        '''
        res=random.choice(sequence)
        return res


if __name__ == '__main__':
    test=OlymKeywords().Random_Choice('helllo')
    print test