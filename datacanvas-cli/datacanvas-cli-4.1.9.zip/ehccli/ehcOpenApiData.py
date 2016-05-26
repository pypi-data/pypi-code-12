import sys
import optparse
import json

class ehcOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]


    def ehcList(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            "--status",
            dest="Status",
            help="input status(optional,default:running)",
            metavar="STATUS"
        )
        (options,args) = parser.parse_args()
        status = options.Status
        return status


    def ehcStatus(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Ehcid",
            help="input edsId",
            metavar="EDSID"
        )
        (options,args) = parser.parse_args()
        if options.Ehcid == None:
            print 'please input ehcid!'
            sys.exit()
        else:
            ehcid = options.Ehcid

        return ehcid

    def nameByIp(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--ip",
            dest="Ip",
            help="input ip",
            metavar="IP"
        )
        (options,args) = parser.parse_args()
        if options.Ip == None:
            print 'please input ip!'
            sys.exit()
        else:
            ip = options.Ip
        return ip

    def submit(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input resource id",
            metavar="ID"
        )
        parser.add_option(
            "-e",
            "--edsid",
            dest="Ehcid",
            help="input edsid",
            metavar="EDSID"
        )
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="input type(optional,default:shell)",
            metavar="TYPE"
        )
        parser.add_option(
            "-l",
            "--title",
            dest="Title",
            help="input title",
            metavar="TITLE"
        )
        parser.add_option(
            "-g",
            "--tags",
            dest="Tags",
            help="input tags",
            metavar="TAGS"
        )
        parser.add_option(
            "-c",
            "--conf",
            dest="Conf",
            help="input conf",
            metavar="CONF"
        )
        parser.add_option(
            "-d",
            "--typeid",
            dest="Typeid",
            help="input typeid",
            metavar="TYPEID"
        )
        parser.add_option(
            "-f",
            "--edsname",
            dest="Ehcname",
            help="input edsname",
            metavar="EDSNAME"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input id!'
            sys.exit()
        if options.Ehcid == None:
            print 'please input edsid!'
            sys.exit()
        if options.Title == None:
            print 'please input title!'
            sys.exit()
        if options.Tags == None:
            print 'please input tags!'
            sys.exit()
        if options.Conf == None:
            print 'please input conf!'
            sys.exit()
        if options.Typeid == None:
            print 'please input typeid!'
            sys.exit()
        if options.Ehcname== None:
            print 'please input edsname!'
            sys.exit()

        id = options.Id
        ehcid = options.Ehcid
        type = options.Type
        title = options.Title
        tags = options.Tags
        cof = options.Conf
        typeid = options.Typeid
        ehcname = options.Ehcname
        jsonObj = {'id':id,'ehcid':ehcid,'type':type,'title':title,'tags':tags,'cof':cof,'typeid':typeid,'ehcname':ehcname}
        data = json.dumps(jsonObj)
        return data

    def createEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="input name",
            metavar="NAME"
        )
        parser.add_option(
            "-d",
            "--describe",
            dest="Describe",
            help="input describe",
            metavar="DESCRIBE"
        )
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="input type(optional,default:aliyun)",
            metavar="TYPE"
        )
        parser.add_option(
            "-z",
            "--zone",
            dest="Zone",
            help="input zone(optional,default:cn-beijing-a)",
            metavar="ZONE"
        )
        parser.add_option(
            "-r",
            "--region",
            dest="Region",
            help="input region(optional,default:cn-beijing)",
            metavar="REGION"
        )
        parser.add_option(
            "-p",
            "--slave_num",
            dest="Slave_num",
            help="input slave_num(optional,default:0)",
            metavar="SLAVE_NUM"
        )
        parser.add_option(
            "-s",
            "--slave_type",
            dest="Slave_type",
            help="input slave_type(optional,default:ecs.m1.medium)",
            metavar="SLAVE_TYPE"
        )
        parser.add_option(
            "-m",
            "--master_type",
            dest="Master_type",
            help="input master_type(optional,default:ecs.m1.medium)",
            metavar="MASTER_TYPE"
        )
        (options,args) = parser.parse_args()
        if options.Name == None:
            print 'please input name!'
            sys.exit()
        else:
            name = options.Name

        if options.Describe == None:
            print 'please input describe!'
            sys.exit()
        else:
            describe = options.Describe

        if options.Type == None:
            type = 'aliyun'
        else:
            type = options.Type

        if options.Zone == None:
            zone = 'cn-beijing-a'
        else:
            zone = options.Type

        if options.Region == None:
            region = 'cn-beijing'
        else:
            region = options.region

        if options.Slave_num == None:
            slave_num = '0'
        else:
            slave_num = options.slave_num

        if options.Slave_type == None:
            slave_type = 'ecs.m1.medium'
        else:
            slave_type = options.Slave_type

        if options.Master_type == None:
            master_type = 'ecs.m1.medium'
        else:
            master_type = options.Master_typey

        jsonObj = {'name':name,'description':describe,'type':type,'zone':zone,'region':region,'slave_num':slave_num,'slave_type':slave_type,'master_type':master_type}
        data = json.dumps(jsonObj)
        print data
        return data

    def deleteEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-e",
            "--eds_id",
            dest="Ehc_id",
            help="input eds_id",
            metavar="EDS_ID"
        )
        (options,args) = parser.parse_args()
        if options.Ehc_id == None:
            print 'please input correct eds_id'
            sys.exit()
        else:
            ehc_id = options.Ehc_id

        return ehc_id

    def listTables(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="input type(optional;default:PostgreSQL;allow:PostgreSQL, MySQL)",
            metavar="TYPE"
        )
        parser.add_option(
            "-u",
            "--user",
            dest="User",
            help="input user",
            metavar="USER"
        )
        parser.add_option(
            "-p",
            "--password",
            dest="Password",
            help="input password",
            metavar="PASSWORD"
        )
        parser.add_option(
            "-c",
            "--connect_string",
            dest="Connect_string",
            help="input connect_string(jdbc:postgresql://52.74.0.70:5432/datacanvas )",
            metavar="CONNECT_STRING"
        )
        parser.add_option(
            "-s",
            "--schema",
            dest="Schema",
            help="input schema(optional)",
            metavar="SCHEMA"
        )
        (options,args) = parser.parse_args()

        List = ['PostgreSQL','MySQL']
        if options.Type == None:
            type = 'PostgreSQL'
        elif options.Type not in List:
            print 'Please input correct TableType!'
            sys.exit(-1)
        else:
            type = options.Type

        if options.User == None:
            print 'please input correct user!'
            sys.exit()
        else:
            user = options.User

        if options.Password == None:
            print 'please input correct password!'
            sys.exit()
        else:
            password = options.Password

        if options.Connect_string == None:
            print 'please input correct connect_string!'
            sys.exit()
        else:
            connect_string = options.Connect_string

        schema = options.Schema

        a=[type,user,password,connect_string,schema]
        return a

    def rebootEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input correct id!'
            sys.exit()
        else:
            id = options.Id

        return id

    def sqlQuery(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-l",
            "--lang",
            dest="Lang",
            help="input lang",
            metavar="LANG"
        )
        parser.add_option(
            "-d",
            "--db",
            dest="Db",
            help="input db",
            metavar="DB"
        )
        parser.add_option(
            "-q",
            "--query",
            dest="Query",

            help="input query ; demo: 'SELECT COUNT(*) FROM datacanva_t',"" is neccesary! ",
            metavar="QUERY"
        )
        parser.add_option(
            "-o",
            "--host",
            dest="Host",
            help="input host",
            metavar="HOST"
        )
        parser.add_option(
            "-n",
            "--edsname",
            dest="Ehcname",
            help="input edsname",
            metavar="EDSNAME"
        )
        parser.add_option(
            "-i",
            "--edsid",
            dest="Ehcid",
            help="input edsid",
            metavar="EDSID"
        )
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="input type",
            metavar="TYPE"
        )
        (options,args) = parser.parse_args()
        if options.Lang == None:
            print 'please input correct lang!'
            sys.exit()
        else:
            lang = options.Lang

        if options.Db == None:
            print 'please input correct db!'
            sys.exit()
        else:
            db = options.Db

        if options.Query == None:
            print 'please input correct query!'
            sys.exit()
        else:
            query = options.Query

        if options.Host == None:
            print 'please input correct host!'
            sys.exit()
        else:
            host = options.Host

        if options.Ehcname == None:
            print 'please input correct edsname!'
            sys.exit()
        else:
            ehcname = options.Ehcname

        if options.Ehcid == None:
            print 'please input correct edsid'
            sys.exit()
        else:
            ehcid = options.Ehcid

        if options.Type == None:
            print 'please input correct type!'
            sys.exit()
        else:
            type = options.Type

        jsonObj = {'lang':lang,'db':db,'query':query,'host':host,'ehcname':ehcname,'ehc_id':ehcid,'type':type}
        data = json.dumps(jsonObj)

        return data

    def sqlStatus(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input id",
            metavar="ID"
        )
        parser.add_option(
            "-o",
            "--host",
            dest="Host",
            help="input host",
            metavar="HOST"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input correct id!'
            sys.exit()
        else:
            id = options.Id

        if options.Host == None:
            print 'please input correct host!'
            sys.exit()
        else:
            host = options.Host

        a = [id,host]
        return a

    def startEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input correct id!'
            sys.exit()
        else:
            id = options.Id
        return id

    def stopEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input correct id!'
            sys.exit()
        else:
            id = options.Id
        return id

    def terminateEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input correct id!'
            sys.exit()
        else:
            id = options.Id
        return id

    def updateEhc(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="input id",
            metavar="ID"
        )
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="input name",
            metavar="NAME"
        )
        parser.add_option(
            "-d",
            "--describe",
            dest="Describe",
            help="input describe",
            metavar="DESCRIBE"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input correct id!'
            sys.exit()
        else:
            id = options.Id

        if options.Name == None:
            print 'please input correct name!'
            sys.exit()
        else:
            name = options.Name

        if options.Describe == None:
            print 'please input correct describe!'
            sys.exit()
        else:
            describe = options.Describe

        jsonObj = {'id':id,'name':name,'describe':describe}
        data = json.dumps(jsonObj)
        return data

class monitorOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]


    def monitorCpu(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-s",
            "--starttime",
            dest="Starttime",
            help="input starttime",
            metavar="STARTTIME"
        )
        parser.add_option(
            "-e",
            "--endtime",
            dest="Endtime",
            help="input endtime",
            metavar="ENDTIME"
        )
        (options,args) = parser.parse_args()
        starttime = options.Starttime
        if starttime == None:
            print 'please input starttime!'
            sys.exit(-1)
        endtime = options.Endtime
        if endtime == None:
            print'please input endtime!'
            sys.exit(-1)
        jsonObj = {'starttime':starttime,'endtime':endtime}
        data = json.dumps(jsonObj)
        return data

    def monitorMemory(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-s",
            "--starttime",
            dest="Starttime",
            help="input starttime",
            metavar="STARTTIME"
        )
        parser.add_option(
            "-e",
            "--endtime",
            dest="Endtime",
            help="input endtime",
            metavar="ENDTIME"
        )
        (options,args) = parser.parse_args()
        starttime = options.Starttime
        if starttime == None:
            print 'please input starttime!'
            sys.exit(-1)
        endtime = options.Endtime
        if endtime == None:
            print'please input endtime!'
            sys.exit(-1)
        jsonObj = {'starttime':starttime,'endtime':endtime}
        data = json.dumps(jsonObj)
        return data

    def monitorNetwork(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-s",
            "--starttime",
            dest="Starttime",
            help="input starttime",
            metavar="STARTTIME"
        )
        parser.add_option(
            "-e",
            "--endtime",
            dest="Endtime",
            help="input endtime",
            metavar="ENDTIME"
        )
        (options,args) = parser.parse_args()
        starttime = options.Starttime
        if starttime == None:
            print 'please input starttime!'
            sys.exit(-1)
        endtime = options.Endtime
        if endtime == None:
            print'please input endtime!'
            sys.exit(-1)
        jsonObj = {'starttime':starttime,'endtime':endtime}
        data = json.dumps(jsonObj)
        return data


class jobOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]


    def createJobFromOutside(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-p",
            "--projectid",
            dest="Projectid",
            help="Project id",
            metavar="PROJECTID"
        )
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="Job name",
            metavar="JOBNAME"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Job description",
            metavar="DESCRIPTION"
        )
        parser.add_option(
            "-u",
            "--userid",
            dest="Userid",
            help="User id",
            metavar="USERID"
        )
        parser.add_option(
            "-v",
            "--variable",
            dest="Variable",
            help="Project variable",
            metavar="VARIABLE"
        )
        parser.add_option(
            "-i",
            "--projectversionid",
            dest="Projectversionid",
            help="optional, Project versionId",
            metavar="PROJECTVERSIONID"
        )
        parser.add_option(
            "-f",
            "--notification",
            dest="Notification",
            help="Job success notification email, split by comma",
            metavar="NOTIFICATION"
        )
        parser.add_option(
            "-c",
            "--cc",
            dest="Cc",
            help="Job success cc email, split by comma",
            metavar="CC"
        )
        (options,args) = parser.parse_args()
        if options.Projectid == None:
            print 'please input projectid!'
            sys.exit(-1)
        else:
            projectid = options.Projectid

        if options.Name == None:
            print 'please input job name!'
            sys.exit(-1)
        else:
            name = options.Name

        if options.Description == None:
            print 'please input description!'
            sys.exit(-1)
        else:
            description = options.Description

        if options.Userid == None:
            print 'please input user id!'
            sys.exit(-1)
        else:
            userid = options.Userid

        if options.Variable == None:
            print 'please input variable!'
            sys.exit(-1)
        else:
            variable = options.Variable

        projectversionid = options.Projectversionid

        if options.Notification == None:
            print 'please input Job success cc email, split by comma!'
            sys.exit(-1)
        else:
            notification = options.Notification

        if options.Cc == None:
            print 'please input Job success notification email, split by comma!'
            sys.exit(-1)
        else:
            cc = options.Cc

        jsonObj = {'projectId':projectid,'name':name,'description':description,'userId':userid,'variable':variable,'projectVersionId':projectversionid,'notification':notification,'cc':cc}
        data = json.dumps(jsonObj)
        return data

    def createJob(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Project id",
            metavar="PROJECTID"
        )
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="Job name",
            metavar="JOBNAME"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Job description",
            metavar="DESCRIPTION"
        )
        parser.add_option(
            "-v",
            "--variable",
            dest="Variable",
            help="Project variable",
            metavar="VARIABLE"
        )
        parser.add_option(
            "-p",
            "--projectversionid",
            dest="Projectversionid",
            help="optional, Project versionId",
            metavar="PROJECTVERSIONID"
        )
        parser.add_option(
            "-f",
            "--notification",
            dest="Notification",
            help="Job success notification email, split by comma",
            metavar="NOTIFICATION"
        )
        parser.add_option(
            "-c",
            "--cc",
            dest="Cc",
            help="Job success cc email, split by comma",
            metavar="CC"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input project id!'
            sys.exit(-1)
        else:
            id = options.Id

        if options.Name == None:
            print 'please input job name!'
            sys.exit(-1)
        else:
            name = options.Name

        if options.Description == None:
            print 'please input description!'
            sys.exit(-1)
        else:
            description = options.Description

        if options.Variable == None:
            print 'please input variable!'
            sys.exit(-1)
        else:
            variable = options.Variable

        projectversionid = options.Projectversionid

        if options.Notification == None:
            print 'please input Job success cc email, split by comma!'
            sys.exit(-1)
        else:
            notification = options.Notification

        if options.Cc == None:
            print 'please input Job success notification email, split by comma!'
            sys.exit(-1)
        else:
            cc = options.Cc

        jsonObj = {'name':name,'description':description,'variable':variable,'projectVersionId':projectversionid,'notification':notification,'cc':cc}
        data = json.dumps(jsonObj)
        a = [id,data]
        return a

    def jobStatus(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Job id",
            metavar="JOBID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input job id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id

    def onlyStatus(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Job id",
            metavar="JOBID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input job id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id

class moduleOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]

    def createModule(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="Module name",
            metavar="MODULENAME"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Module description",
            metavar="DESCRIPTION"
        )

        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="Module type",
            metavar="TYPE"
        )
        parser.add_option(
            "-a",
            "--tags",
            dest="Tags",
            help="Module tags",
            metavar="TAGS"
        )
        parser.add_option(
            "-u",
            "--udfs",
            dest="Udfs",
            help="Module udfs file",
            metavar="UDFS"
        )
        parser.add_option(
            "-f",
            "--files",
            dest="Files",
            help="Module files",
            metavar="FILES"
        )
        parser.add_option(
            "-p",
            "--params",
            dest="Param",
            help="Module params",
            metavar="PARAMS"
        )
        parser.add_option(
            "-i",
            "--inputs",
            dest="Inputs",
            help="Module inputs",
            metavar="INPUTS"
        )
        parser.add_option(
            "-o",
            "--outputs",
            dest="Outputs",
            help="Module outputs",
            metavar="OUTPUTS"
        )
        parser.add_option(
            "-c",
            "--code",
            dest="Code",
            help="Module logic code",
            metavar="Code"
        )
        (options,args) = parser.parse_args()
        if options.Name == None:
            print 'please input module name!'
            sys.exit(-1)
        else:
            name = options.Name

        if options.Description == None:
            print 'please input description!'
            sys.exit(-1)
        else:
            description = options.Description

        if options.Type == None:
            print 'please input module type!'
            sys.exit(-1)
        else:
            type = options.Type

        if options.Tags == None:
            print 'please input module tags!'
            sys.exit(-1)
        else:
            tags = options.Tags

        if options.Udfs == None:
            print 'please input Module udfs file!'
            sys.exit(-1)
        else:
            udfs = options.Udfs

        if options.File == None:
            print 'please input Module files!'
            sys.exit(-1)
        else:
            file = options.File

        if options.Params == None:
            print 'please input Module parans!'
            sys.exit(-1)
        else:
            params = options.Params

        if options.Inputs == None:
            print 'please input Module inputs!'
            sys.exit(-1)
        else:
            inputs = options.Inputs

        if options.Outputs == None:
            print 'please input Module outputs!'
            sys.exit(-1)
        else:
            outputs = options.Outputs

        if options.Code == None:
            print 'please input Module logic code!'
            sys.exit(-1)
        else:
            code = options.Code


        jsonObj = {'name':name,'description':description,'type':type,'tags':tags,'udfs':udfs,'file':file,'params':params,'inputs':inputs,'outputs':outputs,'code':code}
        data = json.dumps(jsonObj)
        return data


    def moduleDelete(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Module id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input module id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id

    def moduleList(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-p",
            "--page",
            dest="Page",
            help="optional, default 1, start page",
            metavar="PAGE"
        )
        parser.add_option(
            "-n",
            "--num",
            dest="Num",
            help="optional, default 50, num each page have",
            metavar="NUM"
        )
        parser.add_option(
            "-t",
            "--tags",
            dest="Tags",
            help="optional, use tags fileter, split by comma",
            metavar="TAGS"
        )

        parser.add_option(
            "-k",
            "--keyword",
            dest="Keyword",
            help="optional, used to filter by name and description",
            metavar="KEYWORD"
        )
        parser.add_option(
            "-w",
            "--order_key",
            dest="Order_key",
            help="optional, used to set data order",
            metavar="ORDER_KEY"
        )
        parser.add_option(
            "-x",
            "--order_by",
            dest="Order_by",
            help="optional, data order direction",
            metavar="ORDER_BY"
        )
        (options,args) = parser.parse_args()
        if options.Page == None:
            page = 1
        else:
            page = options.Page

        if options.Num == None:
            num = 50
        else:
            num = options.Num

        tags = options.Tags
        keyword = options.Keyword
        order_key = options.Order_key
        order_by =options.Order_by
        a = [page,num,tags,keyword,order_key,order_by]
        return a

    def ModuleVersionList(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="module id",
            metavar="ID"
        )
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="module type, 0 -- common module, 1 -- datasource",
            metavar="TYPE"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input module id!'
            sys.exit(-1)
        else:
            id = options.Id

        if options.Type == None:
            print 'please input module type!'
            sys.exit(-1)
        else:
            type = options.Type

        a = [id,type]
        return a

    def updateModule(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="module id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input module id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id


class privilegeOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]

    def CheckRule(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            "--resourcetype",
            dest="Resourcetype",
            help="Input Resourcetype",
            metavar="RESOURCETYPE"
        )
        parser.add_option(
            "-o",
            "--operate",
            dest="Operate",
            help="Input operate",
            metavar="OPERATE"
        )
        parser.add_option(
            "-i",
            "--resourceid",
            dest="Resourceuid",
            help="Input Resourceid",
            metavar="RESOURCEID"
        )
        (options,args) = parser.parse_args()
        if options.Resourcetype == None:
            print 'please input resourcetype!'
            sys.exit(-1)
        else:
            resourcetype = options.Resourcetype

        if options.Operate == None:
            print 'please input operate!'
            sys.exit(-1)
        else:
            operate = options.Operate

        resourceid = options.Resourceid

        a = [resourcetype,operate,resourceid]
        return a

    def GetInstanceOperates(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            "--resourcetype",
            dest="Resourcetype",
            help="Input Resourcetype",
            metavar="RESOURCETYPE"
        )
        parser.add_option(
            "-i",
            "--resourceid",
            dest="Resourceuid",
            help="Input Resourceid",
            metavar="RESOURCEID"
        )
        (options,args) = parser.parse_args()
        if options.Resourcetype == None:
            print 'please input resourcetype!'
            sys.exit(-1)
        else:
            resourcetype = options.Resourcetype

        if options.Resourceid == None:
            print 'please input resourceid!'
            sys.exit(-1)
        else:
            resourceid = options.Resourceid
        a = [resourcetype,resourceid]
        return a

    def GroupDetail(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Input id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id

    def ListResourceTypes(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="Input type",
            metavar="TYPE"
        )
        (options,args) = parser.parse_args()

        if options.Type not in ['Project','Module']:
            print "type must be 'Project'or'Module'!"
            sys.exit(-1)
        else:
            type = options.Type

        return type

    def RoleDetail(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Input id",
            metavar="ID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id



class userOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]

    def deleteUser(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--userid",
            dest="Userid",
            help="User id",
            metavar="USERID"
        )
        (options,args) = parser.parse_args()
        if options.Userid == None:
            print 'please input user id!'
            sys.exit(-1)
        else:
            userid = options.Userid
        return userid

    def userLogin(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        parser.add_option(
            "-p",
            "--password",
            dest="Password",
            help="User password",
            metavar="PASSWORD"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            username = options.Username

        if options.Password == None:
            print 'please input user password!'
            sys.exit(-1)
        else:
            password = options.Password

        jsonObj = {'account':username,'password':password}
        data = json.dumps(jsonObj)
        return data

    def setDefaultUserKey(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            username = options.Username
        return username

    def userKeyCreate(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        parser.add_option(
            "-k",
            "--userkey",
            dest="Userkey",
            help="User key",
            metavar="USERKEY"
        )
        parser.add_option(
            "-s",
            "--secret",
            dest="Secret",
            help="User secret",
            metavar="SECRET"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            username = options.Username
        if options.Userkey == None:
            print 'please input user key!'
            sys.exit(-1)
        else:
            userkey = options.Userkey
        if options.Secret == None:
            print 'please input user secret!'
            sys.exit(-1)
        else:
            secret = options.Secret

        jsonObj = {'name':username,'key':userkey,'secret':secret}
        data = json.dumps(jsonObj)
        return data

    def userKeyDelete(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            name = options.Username
        return name


    def userKeyDetail(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            name = options.Username
        return name

    def userKeyUpdate(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        parser.add_option(
            "-k",
            "--userkey",
            dest="Userkey",
            help="User key",
            metavar="USERKEY"
        )
        parser.add_option(
            "-s",
            "--secret",
            dest="Secret",
            help="User secret",
            metavar="SECRET"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            name = options.Username
        if options.Userkey == None:
            print 'please input user key!'
            sys.exit(-1)
        else:
            userkey = options.Userkey
        if options.Secret == None:
            print 'please input user secret!'
            sys.exit(-1)
        else:
            secret = options.Secret

        jsonObj = {'key':userkey,'secret':secret}
        data = json.dumps(jsonObj)
        a = [name,data]
        return a

    def userRegister(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--username",
            dest="Username",
            help="User name",
            metavar="USERNAME"
        )
        parser.add_option(
            "-p",
            "--password",
            dest="Password",
            help="User password",
            metavar="PASSWORD"
        )
        parser.add_option(
            "-e",
            "--email",
            dest="Email",
            help="User email",
            metavar="EMAIL"
        )
        (options,args) = parser.parse_args()
        if options.Username == None:
            print 'please input user name!'
            sys.exit(-1)
        else:
            username = options.Username

        if options.Password == None:
            print 'please input user password!'
            sys.exit(-1)
        else:
            password = options.Password
        if options.Email == None:
            print 'please input user email!'
            sys.exit(-1)
        else:
            email = options.Email
        jsonObj = {'name':username,'email':email,'password':password}
        data = json.dumps(jsonObj)
        return data

    def userUpdate(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--userid",
            dest="Userid",
            help="Optional, User id",
            metavar="USERID"
        )
        parser.add_option(
            "-p",
            "--password",
            dest="Password",
            help="Optional, New password",
            metavar="PASSWORD"
        )
        parser.add_option(
            "-e",
            "--email",
            dest="Email",
            help="new email",
            metavar="EMAIL"
        )
        (options,args) = parser.parse_args()
        id =options.Userid
        password = options.Password
        email = options.Email
        jsonObj = {'password':password,'email':email}
        data = json.dumps(jsonObj)
        a = [id,data]
        return  a

    def sendPhoneVerifySms(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-p",
            "--phone",
            dest="Phone",
            help="phone number",
            metavar="PHONE"
        )
        (options,args) = parser.parse_args()
        if options.Phone == None:
            print 'please input phone'
            sys.exit(-1)
        else:
            phone = options.Phone
        jsonObj = {'phone':phone}
        data = json.dumps(jsonObj)
        return data


class projectOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]

    def createProject(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="Project name",
            metavar="PROJECTNAME"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Project description",
            metavar="DESCRIPTION"
        )
        (options,args) = parser.parse_args()
        if options.Name == None:
            print 'please input project name!'
            sys.exit(-1)
        else:
            name = options.Name
        if options.Description == None:
            print 'please input project description!'
            sys.exit(-1)
        else:
            description = options.Description
        jsonObj ={'name':name,'description':description}
        data = json.dumps(jsonObj)
        return data

    def deleteProject(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Project id",
            metavar="PROJECTID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input project id!'
            sys.exit(-1)
        else:
            id = options.Id
        return id

    def projectList(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-p",
            "--page",
            dest="Page",
            help="(Optional) Start page",
            metavar="PAGE"
        )
        parser.add_option(
            "-n",
            "--num",
            dest="Num",
            help="(Optional) project num in one page",
            metavar="NUM"
        )
        parser.add_option(
            "-o",
            "--orderkey",
            dest="Orderkey",
            help="(Optional) Order key",
            metavar="ORDERKEY"
        )
        parser.add_option(
            "-b",
            "--orderby",
            dest="Orderby",
            help="(Optional) Order by",
            metavar="ORDERBY"
        )
        parser.add_option(
            "-m",
            "--mine",
            dest="Mine",
            help="(Optional) Used to filter mine project",
            metavar="MINE"
        )
        parser.add_option(
            "-k",
            "--keyword",
            dest="Keyword",

            help="(Optional) project Filter keyword",
            metavar="KEYWORD"
        )
        (options,args) = parser.parse_args()
        if options.Page == None:
            page = 1
        else :
            page = options.Page

        if options.Num == None:
            num = 10
        else :
            num = options.Num

        if options.Orderkey == None:
            orderkey = "createtime"
        else :
            orderkey = options.orderkey

        if options.Orderby == None:
            orderby = "DESC"
        else :
            orderby = options.Orderby

        if options.Mine == None:
            mine = "true"
        else :
            mine = options.Mine

        a=[page,num,orderkey,orderby,mine]
        return a

    def setupWorkspace(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-p",
            "--projectid",
            dest="Projectid",
            help="Project id",
            metavar="PROJECTID"
        )
        parser.add_option(
            "-l",
            "--locations",
            dest="Locations",
            help="Module locations",
            metavar="LOCATIONS"
        )
        parser.add_option(
            "-c",
            "--connections",
            dest="Connections",
            help="Module connections",
            metavar="CONNECTIONS"
        )
        parser.add_option(
            "-v",
            "--variable",
            dest="Variable",
            help="Project variables",
            metavar="VARIABLE"
        )
        parser.add_option(
            "-e",
            "--enariables",
            dest="Envariables",
            help="Project envariables",
            metavar="ENVARIABLES"
        )
        (options,args) = parser.parse_args()
        jsonObj = {'projectId':options.Projectid,'locations':options.Locations,'connections':options.Connections,'variable':options.Variable,'envvariables':options.Envariables}
        data = json.dumps(jsonObj)
        return data

    def updateProject(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Projectid",
            help="Project id",
            metavar="PROJECTID"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Project description (optional)",
            metavar="DESCRIPTION"
        )
        parser.add_option(
            "-p",
            "--private",
            dest="Private",
            help="Project private(boolean)",
            metavar="PRIVATE"
        )
        (options,args) = parser.parse_args()
        if options.Projectid == None:
            print 'please input project id!'
            sys.exit(-1)
        else:
            id = options.Projectid

        description = options.Description
        private = options.Private
        jsonObj = {'description':description,'private':private}
        data = json.dumps(jsonObj)
        a = [id,data]
        return a

class resourceOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]

    def resourceCopy(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Resource id",
            metavar="RESOURCEID"
        )
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="Resource name",
            metavar="RESOURCENAME"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input resource id!'
            sys.exit(-1)
        else:
            id = options.Id

        if options.Name == None:
            print 'please input resource name!'
            sys.exit(-1)
        else:
            name = options.Name
        jsonObj = {'name':name}
        data = json.dumps(jsonObj)
        a = [id,data]
        return a


    def resourceCreate(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-a",
            "--alias",
            dest="Alias",
            help="Resource alias",
            metavar="ALIAS"
        )
        parser.add_option(
            "-n",
            "--name",
            dest="Name",
            help="Resource name",
            metavar="RESOURCENAME"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Resource description",
            metavar="Description"
        )
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="Resource type",
            metavar="RESOURCETYPE"
        )
        parser.add_option(
            "-l",
            "--privacylevel",
            dest="Privacylevel",
            help="Resource privacylevel",
            metavar="PRIVACYLEVEL"
        )
        parser.add_option(
            "-p",
            "--params",
            dest="Params",
            help="Resource params",
            metavar="PARAMS"
        )
        (options,args) = parser.parse_args()
        if options.Alias == None:
            print 'please input resource alias!'
            sys.exit(-1)
        else:
            alias = options.Alias

        if options.Name == None:
            print 'please input resource name!'
            sys.exit(-1)
        else:
            name = options.Name

        if options.Description == None:
            print 'please input resource description!'
            sys.exit(-1)
        else:
            description = options.Description

        if options.Type == None:
            print 'please input resource type!'
            sys.exit(-1)
        else:
            type = options.Type

        if options.Privacylevel == None:
            print 'please input resource privacylevel!'
            sys.exit(-1)
        else:
            privacylevel = options.Privacylevel

        if options.Params == None:
            print 'please input resource params!'
            sys.exit(-1)
        else:
            params = options.Params

        jsonObj = {'name':name,'alias':alias,'description':description,'resourceType':type,'privacyLevel':privacylevel,'params':params}
        data = json.dumps(jsonObj)
        return data

    def resourceSpecifyTypeParams(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="Resource type",
            metavar="RESOURCETYPE"
        )
        (options,args) = parser.parse_args()
        if options.Type == None:
            print 'please input resource type!'
            sys.exit(-1)
        else:
            type = options.Type

        return type

    def resourceUpdate(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Resource id",
            metavar="RESOURCEID"
        )
        parser.add_option(
            "-a",
            "--alias",
            dest="Alias",
            help="Resource alias",
            metavar="ALIAS"
        )
        parser.add_option(
            "-d",
            "--description",
            dest="Description",
            help="Resource description",
            metavar="Description"
        )
        parser.add_option(
            "-t",
            "--type",
            dest="Type",
            help="Resource type",
            metavar="RESOURCETYPE"
        )
        parser.add_option(
            "-l",
            "--privacylevel",
            dest="Privacylevel",
            help="Resource privacylevel",
            metavar="PRIVACYLEVEL"
        )
        parser.add_option(
            "-p",
            "--params",
            dest="Params",
            help="Resource params",
            metavar="PARAMS"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input resource id!'
            sys.exit(-1)
        else:
            id = options.Id

        if options.Alias == None:
            print 'please input resource alias!'
            sys.exit(-1)
        else:
            alias = options.Alias

        if options.Description == None:
            print 'please input resource description!'
            sys.exit(-1)
        else:
            description = options.Description

        if options.Type == None:
            print 'please input resource type!'
            sys.exit(-1)
        else:
            type = options.Type

        if options.Privacylevel == None:
            print 'please input resource privacylevel!'
            sys.exit(-1)
        else:
            privacylevel = options.Privacylevel

        if options.Params == None:
            print 'please input resource params!'
            sys.exit(-1)
        else:
            params = options.Params

        jsonObj = {'alias':alias,'description':description,'resourceType':type,'privacyLevel':privacylevel,'params':params}
        data = json.dumps(jsonObj)
        a = [id,data]
        return a

    def deleteOneResource(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Resource id",
            metavar="RESOURCEID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input resource id!'
            sys.exit(-1)
        else:
            id = options.Id

        return id

    def startOneResource(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Resource id",
            metavar="RESOURCEID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input resource id!'
            sys.exit(-1)
        else:
            id = options.Id

        return id

    def stopOneResource(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Resource id",
            metavar="RESOURCEID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input resource id!'
            sys.exit(-1)
        else:
            id = options.Id

        return id

    def terminateOneResource(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-i",
            "--id",
            dest="Id",
            help="Resource id",
            metavar="RESOURCEID"
        )
        (options,args) = parser.parse_args()
        if options.Id == None:
            print 'please input resource id!'
            sys.exit(-1)
        else:
            id = options.Id

        return id

class queryOpenApiHandler:
    def __init__(self):
        self.args = sys.argv[1:]

    def query_m(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-o",
            "--host",
            dest="Host",
            help="Host",
            metavar="HOST"
        )
        parser.add_option(
            "-p",
            "--port",
            dest="Port",
            help="Port",
            metavar="PORT"
        )
        parser.add_option(
            "-e",
            "--engine",
            dest="Engine",
            help="Engine",
            metavar="ENGINE"
        )
        parser.add_option(
            "-d",
            "--db",
            dest="Db",
            help="Db",
            metavar="DB"
        )
        parser.add_option(
            "-q",
            "--query",
            dest="Query",
            help="Query",
            metavar="QUERY"
        )
        (options,args) = parser.parse_args()
        if options.Host == None:
            print 'please input sql host!'
            sys.exit(-1)
        else:
            host = options.Host

        if options.Port == None:
            port = 18789
        else:
            port = options.Host


        if options.Engine == None :
            print "Engine must be 'hive' or 'mpp' !"
            sys.exit(-1)
        elif options.Engine not in ['hive','mpp']:
            print "Engine must be 'hive' or 'mpp' !"
            sys.exit(-1)
        else:
            engine = options.Engine

        if options.Db == None:
            print 'please input db!'
            sys.exit(-1)
        else:
            db = options.Db

        if options.Query == None:
            print 'please input query!'
            sys.exit(-1)
        else:
            query = options.Query

        ip = [host,port]
        db_engine_map = { "mpp" : "pg", "hive" : "hive"}
        que = {"lang":db_engine_map[engine], "db": db, "query":query}
        post_data = json.dumps(que)
        message = [ip,post_data]
        return message

    def createTable(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-o",
            "--host",
            dest="Host",
            help="Host",
            metavar="HOST"
        )
        parser.add_option(
            "-p",
            "--port",
            dest="Port",
            help="Port",
            metavar="PORT"
        )
        parser.add_option(
            "-e",
            "--engine",
            dest="Engine",
            help="Engine",
            metavar="ENGINE"
        )
        parser.add_option(
            "-d",
            "--db",
            dest="Db",
            help="Db",
            metavar="DB"
        )
        parser.add_option(
            "-c",
            "--createtable",
            action ='append',
            nargs = 3,
            dest="Createtable",
            help="Createrable(tablename field type)",
            metavar="CREATETABLE"
        )
        (options,args) = parser.parse_args()
        if options.Host == None:
            print 'please input sql host!'
            sys.exit(-1)
        else:
            host = options.Host

        if options.Port == None:
            port = 18789
        else:
            port = options.Host


        if options.Engine == None :
            print "Engine must be 'hive' or 'mpp' !"
            sys.exit(-1)
        elif options.Engine not in ['hive','mpp']:
            print "Engine must be 'hive' or 'mpp' !"
            sys.exit(-1)
        else:
            engine = options.Engine

        if options.Db == None:
            print 'please input db!'
            sys.exit(-1)
        else:
            db = options.Db

        if options.Createtable == None:
            print 'please input createtable query!'
            sys.exit(-1)
        else:
            table_mes = options.Createtable
            n = 0
            table_m_len = len(table_mes)
            a = table_m_len
            table_name_list = []
            table_file_list = []
            table_type_list = []

            while n <= a-1:
                table_v = table_mes[n]
                table_name = table_v[0]
                table_name_list.append(table_name)
                file_name = table_v[1]
                table_file_list.append\
                    (file_name)
                type_c = table_v[2]
                table_type_list.append(type_c)
                n=n+1
            m = 0
            while m <= a-1:
                create_mes = '%s %s,'%(table_file_list[m],table_type_list[m])
                mes = 'CREATE TABLE %s ('%table_name_list[0]
                create_sql1 = mes + create_mes
                create_sql2 = create_sql1 + create_mes
                m=m+1
            sql = create_sql2[:-1] +')'


            if engine == 'mpp':
                query = sql
            else:
                query = sql

        ip = [host,port]
        db_engine_map = { "mpp" : "pg", "hive" : "hive"}
        que = {"lang":db_engine_map[engine], "db": db, "query":query}
        post_data = json.dumps(que)
        message = [ip,post_data]
        return message

    def deleteTable(self):
        parser = optparse.OptionParser()
        parser.add_option(
            "-o",
            "--host",
            dest="Host",
            help="Host",
            metavar="HOST"
        )
        parser.add_option(
            "-p",
            "--port",
            dest="Port",
            help="Port",
            metavar="PORT"
        )
        parser.add_option(
            "-e",
            "--engine",
            dest="Engine",
            help="Engine",
            metavar="ENGINE"
        )
        parser.add_option(
            "-d",
            "--db",
            dest="Db",
            help="Db",
            metavar="DB"
        )
        parser.add_option(
            "-d",
            "--deletetable",
            action ='append',
            dest="Deletetable",
            help="Query",
            metavar="QUERY"
        )
        (options,args) = parser.parse_args()

        if options.Host == None:
            print 'please input sql host!'
            sys.exit(-1)
        else:
            host = options.Host

        if options.Port == None:
            port = 18789
        else:
            port = options.Host

        if options.Engine == None :
            print "Engine must be 'hive' or 'mpp' !"
            sys.exit(-1)
        elif options.Engine not in ['hive','mpp']:
            print "Engine must be 'hive' or 'mpp' !"
            sys.exit(-1)
        else:
            engine = options.Engine

        if options.Db == None:
            print 'please input db!'
            sys.exit(-1)
        else:
            db = options.Db

        if options.Deletetable == None:
            print 'please input deletetable query!'
            sys.exit(-1)
        else:
            table_mes = options.Deletetable
            sql = 'DROP TABLE %s'%table_mes
            if engine == 'mpp':
                query = sql
            else:
                query = sql

        ip = [host,port]
        db_engine_map = { "mpp" : "pg", "hive" : "hive"}
        que = {"lang":db_engine_map[engine], "db": db, "query":query}
        post_data = json.dumps(que)
        message = [ip,post_data]
        return message