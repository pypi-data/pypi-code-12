#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/1/23
"""
import sys,os

commandline = """
#!/usr/local/bin/Rscript
require(ggplot2)
require(ggthemes)
library(grid)
exampleFile = "%s"
countsTable <- read.delim( exampleFile, header=TRUE, stringsAsFactors=TRUE )
hei<-length(levels(countsTable$Function))
aa<-ggplot(countsTable)+geom_bar(aes(x=Function, fill=Function),show_guide =FALSE)+coord_flip()+facet_wrap(~ Cate)+ylab("Gene Number")+theme_few()+theme(axis.text.y=element_text(size=25,color="darkred",face="bold"))
png("%s.png", width=1024, height=24*hei,type="cairo")
ggplot_build(aa)
dev.off()
dev.new()
pdf("%s.pdf",width=15,height = hei/2)
ggplot_build(aa)
dev.off()


"""%(sys.argv[1],sys.argv[2],sys.argv[2])
SCRIPT = open(sys.argv[3],'w')
SCRIPT.write(commandline)
SCRIPT.close()
os.system("Rscript %s"%(sys.argv[3]))
