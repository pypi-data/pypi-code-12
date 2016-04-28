#!/usr/bin/env python
#coding:utf-8
"""
  Author:  LPP --<Lpp1985@hotmail.com>
  Purpose:
  Created: 2015/1/2
"""
from Lib.Dependcy import *
from termcolor import colored
import time
import os
import pandas as pd
from optparse import OptionParser
from pyWorkFlow import WorkflowRunner
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-i", "--Sequence", action="store",
                  dest="Sequence",

                  help="Contig")
parser.add_option("-o", "--Output", action="store",
                  dest="Output",

                  help="OutputPath")
parser.add_option("-c", "--Config", action="store",
                  dest="Config",

                  help="Config File")

class Download_Ref(WorkflowRunner):
    def __init__(self,Id_All,Path):
        self.Path = Path
        self.Id_all = Id_All
        self.gbk_list  = []
        Make_path(self.Path  )
        self.fasta = "%s/total_ref.fa"%(self.Path)
        for each_reference in self.Id_all.split('; '):
            self.gbk_list.append(self.Path+'/'+each_reference+'.gbk')
    def workflow(self):

        print(
            colored(
                "Step 1 Download Reference into %s And Combine them"%(self.Path),
                "green"
            )
        )
        if os.path.exists( self.fasta ):
            return ""
        i=0
        dependcy = []
        for each_reference in self.Id_all.split('; '):

            i+=1

            self.addTask(
                "Download_ref%s"%(i),
                "nohup "+scripts_path+"/Download_reference.py -i %s -o %s >run.log 2>&1"%(each_reference,self.Path ),

            )

            dependcy.append( "Download_ref%s"%(i) )

        self.addTask(
            "Combine",
            "nohup  cat %s >%s"%(
                self.Path+'/*.fasta',
                self.fasta
                ) ,
            dependencies = dependcy
        )





class Circle_Contig(WorkflowRunner):
    def __init__(self,Contig,Output,Ver= False):
        self.Path = os.path.abspath(os.path.split(Output)[0])
        self.Output = Output
        Make_path(self.Path)
        self.Contig = Contig
        self.Ver = Ver

    def workflow(self):
        print(
            colored(
                "Step 2 Check Contig's Termpology result %s"%(self.Ver),
                "green"
            )
        )
        commandline = "nohup "+scripts_path+"Circula.py -i %s  -o %s  >run.log 2>71"%(self.Contig,self.Output)
        if os.path.exists(self.Output):
            return ""
        if self.Ver:
            commandline +="-v"
        self.addTask(
            "Check_Result",
            commandline
        )




class Split_Sequence(WorkflowRunner):
    """Split Chromosomes"""
    def __init__(self,Input,Path,Threshold,Strain):
        if not Path.endswith("/"):
            Path+='/'
        self.Path = Path
        Make_path(Path)
        self.Threshold = int(Threshold)
        self.Input = Input
        self.totalfna =Path+'/total.fna'
        self.Strain = Strain

    def workflow(self):

        print(
            colored("Sequence Split into Chromosome or Plasmid","green"  )
        )
        self.addTask("Split","nohup "+scripts_path+'/Fasta_split.py -i %s -o %s -t %s -n %s >run.log 2>&1 '%(
            self.Input,
            self.Path,
            self.Threshold,
            self.Strain
        )
                     )
        self.addTask(
            "Cat_all",
            "nohup cat %(path)s/*.fasta >%(path)s/total.fna 2>&1"%(
                {"path":self.Path}
                ),
            dependencies="Split"
        )

class RepeatMasker(WorkflowRunner):
    """Split Chromosomes"""
    def __init__(self,Input,Path):
        if not Path.endswith("/"):
            Path+='/'
        self.Path = Path
        Make_path(Path)
        self.Input = Input


    def workflow(self):

        print(
            colored("RepeatMakser Sequence","green"  )
        )
        if glob.glob(self.Path+"/*.html"):
            return ""
        self.addTask("Split","nohup "+config_hash["Tools"]["repeatmasker"]+" -pa 64 -norna -dir %s  -gff  -html %s  >run.oog 2>&1"%(
            self.Path,
            self.Input
        )
                     )


class Order_Adjust(WorkflowRunner):
    "Adjust Order"
    def __init__(self,Contig,Ref,Output):
        Path = os.path.split(Output)[0]
        Make_path(Path)
        self.Contig = Contig
        self.Ref = Ref
        self.Output = Output
    def workflow(self):
        print(colored("Step3 Order Adjust","green") )
        if glob.glob(self.Output):
            return ""
        self.addTask("Adjust","nohup "+scripts_path+'/Sequence_order_adjust.py -s %s -r %s -o %s >run.og 2>&1'%(
            self.Contig,
            self.Ref,
            self.Output
        )
                     )
class IS_Finder(WorkflowRunner):
    def __init__(self,Data,output):
        self.Data = Data
        prefix = os.path.basename(self.Data).rsplit(".",1)[0]
        self.Output = output+'/'+prefix+'/'+prefix+'_IS'
    def workflow(self):
        print(colored("%s Is ISFinding"%(self.Data),"green"  ))
        end_list = glob.glob(self.Output+'.xls')
        if end_list:
            return ""

        self.addTask("Isfind", 
                     command="nohup IsFinder.py  -i  %s -o %s >run.log 2>&1"%(self.Data,self.Output), 
                     cwd=os.path.split(self.Data)[0]
                     )	
class Draw_Graph(WorkflowRunner):
    def __init__(self,Gbk,Anno,outPath):
        self.Gbk = Gbk
        prefix = os.path.basename(self.Gbk).split(".")[0]
        outPath = os.path.abspath(outPath)+'/'
        Build_Dir(outPath)
        self.Output = outPath+prefix+'.png'
        self.Anno = Anno
    def workflow(self):
        print(colored("%s Is Drawing"%(self.Gbk),"green"  ))
        end_list = glob.glob(self.Output)
        if end_list:
            return ""
        self.addTask("Draw",
                     command="nohup "+scripts_path+"/Circular_Graph_Draw.py -g %s -o %s -a %s >run.log 2>&1"%(self.Gbk,self.Output ,self.Anno)
                     )

class AlignmentRun(WorkflowRunner):
    def __init__(self,protein,nucleotide,OutPath,Eval,Cog):
        self.Protein = protein
        self.Nuleotide = nucleotide
        self.Output = OutPath
        self.Eval = Eval
        self.Cog = Cog
    def workflow(self):
        print(colored("%s Is Annotating"%(self.Protein),"green"  ))
        self.addTask("Annotation",
                     command="nohup AnnotationPipe.py -p %s -n %s -e  %s -c %s  -o %s >run.log 2>&1"%(self.Protein,self.Nuleotide,self.Eval,self.Cog,self.Output)

                     )



class Phage_Finder(WorkflowRunner):
    def __init__(self,dataprefix,output):
        self.datainput = dataprefix
        self.output = output+'/'
    def workflow(self):
        print(colored("%s is Phage Finding"%(self.datainput) ,"green" ) )
        if os.path.exists(self.output):
            return ""
        self.addTask("PhageFinder",
                     command= "nohup Phage_Finder.py -i  %s -o  %s"%(  self.datainput,self.output  )



                     )




class Gene_Prediction(WorkflowRunner):
    def __init__(self,Contig,Genius,Spieces,Strain,Center,Prefix,OutPut,Plasmid, Evalue):
        self.Contig = Contig
        self.Commandline = Prokka_Commandline(Contig, Genius, Spieces, Strain, Center, Prefix, OutPut,  Plasmid, Evalue)

        self.gbk = OutPut+'/'+Prefix+'.gbk'
        self.Protein =OutPut+'/'+Prefix+'.faa'
        self.Gff = OutPut+'/'+Prefix+'.gff'
        self.Genome = OutPut+'/'+Prefix+'.fna'
        self.graph = OutPut+'/out.png'
        self.ffn = OutPut+'/'+Prefix+'.ffn'
        self.TotalDatabase = OutPut+'/'+Prefix+'.xlsx'
    def workflow(self):
        if os.path.isfile(self.TotalDatabase):
            return ""
        print(colored("%s is annotating"%(self.Contig),'blue') )
        self.addTask("Annotation",self.Commandline)

        # self.addWorkflowTask("Drawing",draw_flow,dependencies=["Annotation"])
        self.addTask("Database",

                     "nohup "+scripts_path+"/create_database.py " +" -d "+self.TotalDatabase +" -g "+ self.Gff+" -n "+self.ffn+" -p "+self.Protein +' -f %s'%(  self.Genome  ),
                     dependencies=["Annotation"]
                     )









class Data_prapare(WorkflowRunner):
    def __init__(self,Contig,OUTPUT):
        self.Contig = Contig
        if not OUTPUT.endswith('/'):
            OUTPUT+='/'
        self.Output = OUTPUT
        Get_Path(OUTPUT)
        Check_file([["",self.Contig]])
        self.refer_path = self.Output+"/reference/"
        self.circyle_path = self.Output+"/01-1.Circyled_contig/"
        self.adjusted_path = self.Output+"/01-2.Adjusted_contig/"        
        self.ref_fasta = ""
        self.splited_path = self.Output+"/01-3.Assembly_END/"
    def get_contigs(self):
        return glob.glob(os.path.abspath(self.splited_path)+'/*.fasta')
    def workflow(self):
        dependcy = []


        if config_hash["Reference"]["gbk"]:
            Id_All = config_hash["Reference"]["gbk"]
            down_flow = Download_Ref(Id_All, self.refer_path)
            self.addWorkflowTask("Download", down_flow)
            self.gbk_list = down_flow.gbk_list
            self.ref_fasta = down_flow.fasta
            dependcy.append("Download")

        if config_hash["Pipeline"]["checkassembly"].strip().lower()=="yes":
            Ver = True
        else:
            Ver = False
        cir_flow = Circle_Contig(self.Contig,self.circyle_path+"Circled.Contigs",Ver)
        self.addWorkflowTask("Circle",cir_flow,dependencies=dependcy)
        dependcy.append("Circle")
        adjusted_result = cir_flow.Output


        # Adjusted Result
        if config_hash["Reference"]["gbk"]:
            adjust_flow = Order_Adjust(adjusted_result, self.ref_fasta, self.adjusted_path+"assembly_end.fasta")
            self.addWorkflowTask("Adjusted",adjust_flow,dependencies= dependcy)
            adjusted_result = adjust_flow.Output
            dependcy.append("Adjusted")

        split_flow = Split_Sequence(adjusted_result, self.splited_path, config_hash["Threshold"]["genomesize"],config_hash["Taxon"]["strain"] )
        self.addWorkflowTask("Split",split_flow,dependencies=dependcy)
        dependcy.append("Split")
        print (colored(split_flow.totalfna,"red"))
        repeatmasker_flow = RepeatMasker(split_flow.totalfna, self.Output+"/02.RepeatMask/")
        self.addWorkflowTask("Repeat",repeatmasker_flow,dependencies=dependcy)






class Crispr_Run( WorkflowRunner   ):
    def __init__(self,Input,Path):
        self.prefix = os.path.basename( Input  ).rsplit(".",1)[0]
        self.Input = Input
        self.output = os.path.abspath( Path  )+'/'+self.prefix+'/'+self.prefix
    def workflow(self):
        print(colored("%s is Crispr Finding"%(self.prefix) ,"green" ) )
        if glob.glob(self.output+"_RAW.txt"):
            return ""
        self.addTask("Crispr",
                     command= "nohup CrisprRun.py  -g  %s -o  %s"%(  
                         self.Input,
                         self.output  
                         ),



                     )        


class Process_Run(WorkflowRunner):
    def __init__(self,Contig_list,OUTPUT):
        self.Contig_list = Contig_list
        self.Output = os.path.abspath(OUTPUT)
        Get_Path(OUTPUT)
        self.prediction_path  =  self.Output+"/03.Annotation/"
        self.geneinfo = self.prediction_path+'/Gene_Info.xls'
        self.annotation_path = self.Output+"/04.OtherDatabase/"
        self.total_result = self.annotation_path+'/Table/GeneFeature+Annotation.xlsx'
        self.IS_path = self.Output+"/05.InsertionSequence/"
        self.Phage_Path = self.Output+"/06.ProPhage/"


        self.Crispr_Path = self.Output+"/07.Crispr/"
        self.gibash = self.Output+'/gi.sh'
        self.GIPATH = self.Output+'/08.Genomic_Island/'
        os.system(" echo '' >%s"%(self.gibash))
    def RunGI(self):
        if not os.path.exists(self.GIPATH):

            os.system( " echo 'cd %s&& mv  Genomic_Island %s ' >>%s"%( 
                self.Output,
                self.GIPATH,
                self.gibash

            )  
                       ) 

            os.system(  "nohup bash "+ self.gibash  )
        os.remove(self.gibash)
    def OutGBK(self):
        return self.all_gbk
    def workflow(self):
        predependcy = []
        dependcy = []
        annodependcy = []
        annotation_path = self.annotation_path

        sequence_list = []


        # Gene Prediction
        all_pep = []
        all_ffn = []
        all_gbk=[]
        all_needGIHunter = []

        for each_contig in self.Contig_list:

            ###########Gene Prediction RUN！！！！！！#######################


            prefix = os.path.basename(each_contig).rsplit('.',1)[0]
            each_prediction_path = self.prediction_path+'/%s/'%(prefix)
            all_gbk.append(each_prediction_path+prefix+".gbk")
            category = os.path.basename(each_contig).rsplit(".",1)[0]
            genius = config_hash["Taxon"]["genius"]
            spieces = config_hash["Taxon"]["spieces"]
            strain = config_hash["Taxon"]["strain"]
            center = config_hash["Taxon"]["center"]


            if   "Plasmid" in category:
                plasmid = prefix
            else:
                all_needGIHunter.append([each_prediction_path+prefix,prefix])
                plasmid=''
            self.addWorkflowTask(
                "%s_prediction"%(prefix),
                Gene_Prediction(
                    each_contig,
                    genius,
                    spieces,
                    strain,
                    center,
                    prefix,
                    each_prediction_path,
                    plasmid,
                    config_hash["Threshold"]["e_value"]
                    ),
            )
            predependcy.append(
                "%s_prediction"%(prefix)
            )

            if category!="Plasmid":
                ####PhageFinder#############
                self.addWorkflowTask(
                    "%s_phage"%(prefix),
                    Phage_Finder(
                        each_prediction_path+prefix,
                        self.Phage_Path
                        ),
                    dependencies =["%s_prediction"%(prefix)]

                )

                dependcy.append(  "%s_phage"%(prefix) )  



                ##################Crispr##############################
                self.addWorkflowTask(
                    "%s_crispr"%(prefix),
                    Crispr_Run(
                        each_prediction_path+prefix+'.fna',
                        self.Crispr_Path

                    )

                    ,dependencies =["%s_prediction"%(prefix)]

                )
                dependcy.append(  "%s_crispr"%(prefix) ) 
            ######ISFinder###################################
            self.addWorkflowTask(
                "%s_IS"%(prefix),
                IS_Finder(each_prediction_path+prefix+".fna", self.IS_path),
                dependencies =["%s_prediction"%(prefix)]
            )
            dependcy.append(  "%s_IS"%(prefix) )     






            ################# Other Database################

            self.addWorkflowTask( "%s_annotation"%(prefix),
                                  AlignmentRun(each_prediction_path+prefix+".faa", 
                                               each_prediction_path+prefix+".ffn", 
                                               annotation_path, 
                                               config_hash["Threshold"]["e_value"], 
                                               config_hash["Threshold"]["cog"]
                                               ),
                                  dependencies =["%s_prediction"%(prefix)]
                                  )
            annodependcy.append(  "%s_annotation"%(prefix) )
            all_pep.append(each_prediction_path+prefix+".faa")
            all_ffn.append( each_prediction_path+prefix+".ffn"   )









        ######Combine Gene  Prediction Result###################
        self.addTask(

            "CombineResult",
            "nohup "+scripts_path+'/Prediction_XLS_Combine.py -i %s -o %s'%(self.prediction_path, self.geneinfo)
            ,dependencies=predependcy

        )
        dependcy.append("CombineResult")
        annodependcy.append( "CombineResult")






        #######################Combine Database Result########################
        self.addTask(

            "AnnotationALL",
            'nohup XLS_Combine.py -i %s -o %s -g %s'%(
                self.annotation_path+'/Detail/',
                self.annotation_path+'/Table/',
                self.geneinfo
            ) 
            ,dependencies=predependcy+annodependcy

        )  









        #######generate ptt and rnt####################
        self.addTask(
            "ptt_ntt",
            "nohup "+scripts_path+'ptt_rnt.py -i %s -o %s '%(
                self.total_result,
                self.prediction_path,
            ) 
            ,dependencies=["AnnotationALL"]

        ) 
        self.all_gbk = all_gbk





        ##################GIHunter Bash Generate###################

        for each_need_Data,outputprefix in all_needGIHunter:
            self.addTask(

                "%s_GIHunter"%(outputprefix),
                " echo 'cd %s &&GIHunter_Find.py  -i %s  -o %s ' >> %s"%(
                    self.Output,
                    each_need_Data ,
                    outputprefix,
                    self.gibash
                    ),

                dependencies=["ptt_ntt"],

                cwd=self.Output 


            )            
            dependcy.append("%s_GIHunter"%(outputprefix))





        self.all_pep = all_pep
        self.all_ffn = all_ffn
class Post_RUN(WorkflowRunner) :
    def __init__(self,gbk_list, output,geneinfo):
        self.Output = os.path.abspath(output)+'/'
        self.all_gbk = gbk_list

        self.AllPath = self.Output+"/09.AllResult/"
        self.AllResult = self.AllPath+"/AllResult.xlsx"
        self.geneinfo = geneinfo
        self.DrawPath = self.Output+"/10.CircleGraph/"
    def Result_Excel(self):
        try:
            data = pd.read_table(self.AllResult)
        except:
            data = pd.read_excel(self.AllResult)
        data.to_excel(self.AllResult)        
    def workflow(self):
        #ALL ResultCombine
        self.addTask(

            "ALLCOMBINE",
            "nohup "+scripts_path+"ALL_XLS_Combine.py  -i %s -o %s  -g %s"%(self.Output ,self.AllResult ,self.geneinfo )


        )   


        #Draw Graph
        for gbk in self.all_gbk:
            self.addWorkflowTask(
                "%s_Draw"%(os.path.basename(gbk).split('.')[0] ),
                Draw_Graph(gbk , self.AllResult, self.DrawPath),
                dependencies =["ALLCOMBINE"] 
            )














class Total_AnnoAll( WorkflowRunner ):
    def __init__(self,Output,total_ffn,total_pep):
        self.Output = Output
        self.TotalPep = self.Output+'/Total.faa'
        self.TotalFfn = self.Output+'/Total.ffn'
        FFN = open( self.TotalFfn,'w'  )
        PEP = open( self.TotalPep,'w'  )
        for e_f in total_ffn:
            FFN.write(  open(e_f).read()+'\n'   )
        for e_f in total_pep:
            PEP.write(  open(e_f).read()+'\n'   )  
        FFN.close()
        PEP.close()
    def workflow(self):
        self.addWorkflowTask( 
            "totalFinal_annotation",
            AlignmentRun(
                self.TotalPep, 
                self.TotalFfn, 
                self.Output, 
                config_hash["Threshold"]["e_value"], 
                config_hash["Threshold"]["cog"]
                ),
        )       


if __name__ == '__main__':
    (options, args) = parser.parse_args()
    Sequence = options.Sequence
    OUTPUT   = os.path.abspath(options.Output)
    Config   = options.Config
    os.environ["PATH"] = os.getenv("PATH")+'; '+scripts_path
    if not os.path.isfile(Config):
        raise Exception("File %s is not exist!!"%(Config))
    Get_Addtional_Config( Config )
    Config_Parse(general_config)
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)
    README = open(OUTPUT+'/Readme','w')

    README.write("""
该文件夹下包含所有的分析结果，包含：
    reference文件夹：             用于序列开环和Oric位置调整的参考序列
    01-1.Circyled_contig文件夹：  每一个Contig都进行了结构检查，在分析细菌的情况下，如果客户没有要求，则默认所有的序列为环状。该文件夹保存开环后的Contig
    01-2.Adjusted_contig：       在具有参考序列的情况下，依照参考序列进行序列位置调整，将第一个碱基位置按照参考蓄力的DNA复制起始位点进行调整
    01-3.Assembly_END：          进行位置调整后的Contig，这些序列用于后续分析。
    02.RepeatMask：              使用RepeatMasker和TRF等工具预测所有的重复序列，结果请参看.GFF文件和.Html文件。
    03.Annotation：              使用SignalIP，Prodigal等工具进行序列的基础分析注释。包括编码RNA，非编码RNA的预测，和给予Swissprot，Interproscan+PfamA的基本功能注释。
    04.OtherDatabase：           包含KEGG，Nr等多个数据库对预测结果进行比对和功能注释
    05.InsertionSequence:        使用ISFinder对所有插入原件进行了预测和注释
    06.ProPhage:                 对于染色体序列，使用PhageFinder进行了噬菌体前体的预测
    07.Crispr                    对于染色体序列，使用Piler-CR进行了Crispr序列和Spacer的预测，并根据Nt库对Spacer的来源进行了初步的预测。
    08.Gemomic_island             使用GIHunter预测了可能存在的Genomic Island，并将涉及的基因和蛋白进行了标注
    09.AllResult                  将所有的结果进行了合并，成为一个大表格，方便您查阅。如果基因组内的染色体个数大于1，我们会将所有的序列合并，并使用多个数据库进行统一注释，方便您的查看。
    10.CircleGraph                对所得到的结果画圈图进行可视化展示。







    """)

    data_prepare_flow = Data_prapare(Sequence,OUTPUT)

    error = data_prepare_flow.run()
    Contig_list = data_prepare_flow.get_contigs()

    annotation_flow = Process_Run(Contig_list, OUTPUT)
    error = annotation_flow.run()
    annotation_flow.RunGI()
    gbk_list = annotation_flow.OutGBK()

    post_flow = Post_RUN(gbk_list, OUTPUT, annotation_flow.geneinfo)
    post_flow.run()
    post_flow.Result_Excel()
    all_pep = annotation_flow.all_pep
    all_ffn = annotation_flow.all_ffn
    if len( all_pep ) >1:
        Total_AnnoAll(post_flow.AllPath, all_ffn, all_pep)
