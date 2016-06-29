#coding:utf8
import pandas as pd
import zhangte

class RankDf():

    def __init__(self):
        self.df = pd.read_excel("排名监控.xls")

    #批量查收录
    def get_index(self,df,i):
        #查收录
        index = df['收录'][i]
        #针对未收录页面进行更新,也要筛选!
        if index < 1:
            #查收录,如果今天没查过就查一下
            if df.日期[i] != str(zhangte.Base().today(0)):
                index =  zhangte.Baidu().index(self.url)
            #如有收录,就更新一下
            if index > 0:
                df['收录'][i] = index
        return df

    #批量查排名!
    def get_rank(self,df,i):

        #假如今天有查询过?

        #最后查询日期 对比看看是不是今天!如果不是,就查询!
        if df.日期[i] != str(zhangte.Base().today(0)):
            #如果是首页,简单查
            if df["类型"][i] == "首页":
                rank = zhangte.Baidu().rank(self.kw,self.url)[0]

            #如果是内页或是文章页面,复杂查
            else:
                rank = zhangte.Baidu().rank(self.kw,self.url,T=True)[0]

            print (rank,self.url)

            #如果有排名就更新
            if rank > 0:
                df['排名'][i] = rank
            else:
                df['排名'][i] = 200
        return df

    def RanksDf(self):
        #查询首页排名
        for i in self.df.index:
            #每查询一次,就重新导入
            df = pd.read_excel("排名监控.xls")
            df.排名.astype("int")  #数据类型转换一下


            self.kw = df['关键词'][i]
            self.url = df['域名'][i]

            df = self.get_rank(df,i)    #获取排名
            df = self.get_index(df,i)        #获取收录

            df.日期[i] = str(zhangte.Base().today(0))
            df.to_excel("排名监控.xls",index=False)

#集成mysql这个类
class importMysql(zhangte.Mysql):
    sql = """
    INSERT INTO `seo`.`百度排名监控` (`日期`, `关键词`, `排名`, `域名`, `收录`, `类型`, `归属`, `项目`)
    VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");
    """
    def __init__(self,*args,**kwargs):
        super(importMysql,self).__init__(*args,**kwargs)
        self.df = pd.read_excel("排名监控.xls")


    def importsql(self):
        df = self.df
        #如果未导入,就开始导入!
        if self.panduan():
            for i in df.index:
                sql = self.sql.format(df["日期"][i],df["关键词"][i],df["排名"][i],df["域名"][i],
                    df["收录"][i],df["类型"][i],df["归属"][i],df["项目"][i])
                self.exeSQL(sql)



    #判断有没有插入!?
    def panduan(self):
        df = pd.read_sql("SELECT * FROM seo.百度排名监控;",self.conn)
        #如果今天存在最后3行里面,说明已经采集过!

        if str(zhangte.Base().today(0)) in list(df['日期'].tail(3)):
            print ("今天已经导入过,不导入了!")
            return False
        else:
            print ("今天还没有导入!开始导入!")
            return True


def main(db,**kwargs):
    a=RankDf()     #批量查排名
    while True:
        a.RanksDf()
        b = a.df["日期"] == str(zhangte.Base().today(0))
        if  True in  list(b):
            print ("全部查询完毕,开机导入!")
            break

    #导入到sql
    a = importMysql(db,**kwargs)
    a.importsql()




if __name__ == '__main__':
    main(db,**kwargs)

