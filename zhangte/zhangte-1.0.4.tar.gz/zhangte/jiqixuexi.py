#coding:utf8
import numpy
import pandas
import jieba
import re
from .base import *


class NLP(Base):
    fuhao="，。\n"

    def get_stopwords(self):
        '''获取停用词'''
        return pandas.read_csv(
        "StopwordsCN.txt",
        encoding='utf8',
        index_col=False,
        quoting=3,
        sep="\t"
    )


    #余弦值计算函数( 传入2个向量)
    def cosineDist(self,col1, col2):
        return numpy.sum(col1 * col2)/(
            numpy.sqrt(numpy.sum(numpy.power(col1, 2))) *
            numpy.sqrt(numpy.sum(numpy.power(col2, 2)))
        )


    #字符串分割
    def fenge(self,content):
        list1 = re.split(r'[%s\s]\s*' % self.fuhao, content)
        #更改抓取时间
        while '' in list1:
            list1.remove('')
        return list1


    def FenciAndCutStopwords(self,subCorpos):
        #分词且去除停用词
        sub = []
        segments = []
        for j in range(len(subCorpos)):
            segs = jieba.cut(subCorpos[j])
            for seg in segs:
                if len(seg.strip())>1:
                    sub.append(subCorpos[j])    #目标段落 & 目标文章
                    segments.append(seg)        #对应分词
        segmentDF = pandas.DataFrame({'sub':sub, 'segment':segments})
        return segmentDF[~segmentDF.segment.isin(self.stopwords.stopword)]


    def summay(self,content):
        #获取停用词
        self.stopwords = self.get_stopwords()

        #把内容进行分割
        subCorpos = [content] + self.fenge(content)


        #分词且去除停用词
        segmentDF = self.FenciAndCutStopwords(subCorpos)

        #按文章进行词频统计
        segStat = segmentDF.groupby(
                    by=["sub", "segment"]
                )["segment"].agg({
                    "计数":numpy.size
                }).reset_index().sort(
                    columns=["计数"],
                    ascending=False
                )

        #进行文本向量计算
        textVector = segStat.pivot_table(
            index='segment',
            columns='sub',
            values='计数',
            fill_value=0
        )

        target = textVector.ix[:, textVector.apply(numpy.sum)==textVector.apply(numpy.sum).max()]
        textVector = textVector.ix[:, textVector.apply(numpy.sum)!=textVector.apply(numpy.sum).max()]

        distance = textVector.apply(lambda col: self.cosineDist(target.ix[:, 0], col))

        tagis = distance.order(ascending=False)[0:1].index
        return tagis[0]

