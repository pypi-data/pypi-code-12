import sys
import ehcOpenApiData
import requests
import ehcCliConfig


class ehcCliRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.ehcOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def ehcListRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            status = self.apiData.ehcList()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            if status == None:
                url = 'http://%s:%s/tf/ehc/list?status=running'%(address,port)
            else:
                url = 'http://%s:%s/tf/ehc/list?status=%s'%(address,port,status)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def ehcStatusRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            ehc_id = self.apiData.ehcStatus()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/status/:%s'%(address,port,ehc_id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def nameByIpRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            ip = self.apiData.nameByIp()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/namebyip?ip=%s'%(address,port,ip)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def submitRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            data = self.apiData.submit()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            url = 'http://%s:%s/tf/ehc/submit'%(address,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def createEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            data = self.apiData.createEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/create'%(address,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookies':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def deleteEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            ehc_id = self.apiData.deleteEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/del/%s'%(address,port,ehc_id)
            header = {'Content-Type':'application/json','Cookie':_cookies,'X-ACCESS-TOKEN':token}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def listTablesRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            a = self.apiData.listTables()
            type = a[0]
            user = a[1]
            password = a[2]
            connect_string = a[3]
            schema = a[4]
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            if a[4] == None:
                url = 'http://%s:%s/tf/ehc/listTables?type=%s&user=%s&password=%s&connect_string=%s'%(address,port,type,user,password,connect_string)
            else:
                url = 'http://%s:%s/tf/ehc/listTables?type=%s&user=%s&password=%s&connect_string=%s&schema%s'%(address,port,type,user,password,connect_string,schema)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            print url
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def rebootEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            id = self.apiData.rebootEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/reboot/%s'%(address,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def sqlQueryRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            data = self.apiData.sqlQuery()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/sql'%(address,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def sqlStatusRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            a = self.apiData.sqlStatus()
            id = a[0]
            host = a[1]
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/sql/%s?host=%s'%(address,port,id,host)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def startEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            id = self.apiData.startEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/start/%s'%(address,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def stopEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            id = self.apiData.stopEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/stop/%s'%(address,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def terminateEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            ehc_id = self.apiData.terminateEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/terminate/%s'%(address,port,ehc_id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def updateEhcRequest(self):
        try:
            token = self.ehcCliConfig.getToken()
            data = self.apiData.updateEhc()
            address = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/ehc/modify'%(address,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookies':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)


class monitorRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.monitorOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def monitorCpuRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            data = self.apiData.monitorCpu()
            url = 'http://%s:%s/ehc/monitor/cluster/cpu'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,params = data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorMemoryRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            data = self.apiData.monitorMemory()
            url = 'http://%s:%s/ehc/monitor/cluster/memory'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,params = data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorNetworkRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            data = self.apiData.monitorNetwork()
            url = 'http://%s:%s/ehc/monitor/cluster/network'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,params = data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorHeapRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/cluster/network'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorHdfs_capacityRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/cluster/hdfs_capacity'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorSlave_liveRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/cluster/slave_live'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorAlertRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/cluster/alert'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorAlert_numRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/cluster/alert_num'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorHostsRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/hosts'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def monitorServicesRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/ehc/monitor/services'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

class jobRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.jobOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def createJobFromOutsideRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            data = self.apiData.createJobFromOutside()
            url = 'http://%s:%s/tf/job/run/uid'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.post(url,data, headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def createJobRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            data = self.apiData.createJobFromOutside()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/job/run/%s'%(host,port,data[0])
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,data[1], headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def jobStatusRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            id = self.apiData.jobStatus()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/job/status/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url, headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def onlyStatusRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.jobStatus()
            url = 'http://%s:%s/tf/job/onlystatus/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url, headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

class moduleRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.moduleOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def createModuleRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            data = self.apiData.createModule()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/module'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.post(url,data,headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)
    def moduleDeleteRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.moduleDelete()
            url = 'http://%s:%s/tf/module:%s'%(host,port,id)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.delete(url,headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def moduleCreateParamsRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/params'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def moduleListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/module/list'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            r.cookies.set('express:sess', _cookies)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def moduleTagsRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/module/tags'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def moduleVersionListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            a= self.apiData.ModuleVersionList()
            id = a[0]
            type = a[1]
            url = 'http://%s:%s/tf/module/version/%s?type=%s'%(host,port,id,type)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def searchModuleByOutputTypeRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/module/byotype'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def updateModuleRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.updateModule()
            url = 'http://%s:%s/tf/module/%s'%(host,port,id)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.put(url,headers = header,)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

class privilegeRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.privilegeOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def CheckRuleRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            a = self.apiData.CheckRule()
            resourceType = a[0]
            operate = a[1]
            resourceId = a[2]
            _cookies = self.ehcCliConfig.getCookies()
            if resourceId == None:
                url = 'http://%s:%s/tf/privilege/checkRule?resourceType=%s&operate=%s'%(host,port,resourceType,operate)
            else:
                url = 'http://%s:%s/tf/privilege/checkRule?resourceType=%s&operate=%s&resourceId=%s'%(host,port,resourceType,operate,resourceId)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def GetInstanceOperatesRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            a = self.apiData.GetInstanceOperates()
            resourceType = a[0]
            resourceId = a[1]
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/privilege/instanceOperates?resourceType=%s&resourceId=%s'%(host,port,resourceType,resourceId)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def GetTimeStampRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/privilege/timestamp'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def GroupDetailRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.GroupDetail()
            url = 'http://%s:%s/tf/privilege/groups/%s'%(host,port,id)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def ListGroupsRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/privilege/groups'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def ListResourceTypesRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            type = self.apiData.ListResourceTypes()
            url = 'http://%s:%s/tf/privilege/resourceTypes?type=%s'%(host,port,type)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def ListRoleRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/privilege/roles'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def RoleDetailRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.RoleDetail()
            url = 'http://%s:%s/tf/privilege/roles/%s'%(host,port,id)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)



class UserRequests():
    def __init__(self):
        self.apiData = ehcOpenApiData.userOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def deleteUserRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            id = self.apiData.deleteUser()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/%s'%(host,port,id)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.delete(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def genTokenRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/gentoken'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def getTokenRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/token'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def loginRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
          # token = self.ehcCliConfig.getToken()
            data = self.apiData.userLogin()
            url = 'http://%s:%s/user/login'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.post(url,data = data,headers = header)
            try:
                a = r.cookies.get_dict().get('express:sess')
                b = r.cookies.get_dict().get('express:sess.sig')
                _cookies = 'express:sess='+a+';express:sess.sig='+b+';'
                self.ehcCliConfig.ehcCookies(_cookies)
                print r.text
            except:
                print 'please input right message!'
                print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def logoutRequest(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/logout'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.delete(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def setDefaultUserKeyRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            name = self.apiData.setDefaultUserKey()
            url = 'http://%s:%s/user/keys/default/%s'%(host,port,name)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userKeyCreateRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            data = self.apiData.userKeyCreate()
            url = 'http://%s:%s/user/keys'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.post(url,headers = header,data = data)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userKeyDefaultRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/keys/default'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userKeyDeleteRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            name = self.apiData.userKeyDelete()
            url = 'http://%s:%s/user/keys/%s'%(host,port,name)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.delete(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userKeyDetailRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            name = self.apiData.userKeyDetail()
            url = 'http://%s:%s/user/keys/%s'%(host,port,name)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userKeyListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/keys'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userKeyUpdate(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            a = self.apiData.userKeyUpdate()
            name = a[0]
            data = a[1]
            url = 'http://%s:%s/user/keys/%s'%(host,port,name)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userRegisterRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
          # token = self.ehcCliConfig.getToken()
            data = self.apiData.userRegister()
            url = 'http://%s:%s/user/keys'%(host,port)
            header = {'Content-Type':'application/json'}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def userUpdateRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            a = self.apiData.userUpdate()
            id = a[0]
            data = a[1]
            url = 'http://%s:%s/user/:%s'%(host,port,id)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.put(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def sendPhoneVerifySmsRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            id = self.apiData.sendPhoneVerifySms()
            url = 'http://%s:%s/user/sendsms'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def uploadAvatarRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            _cookies = self.ehcCliConfig.getCookies()
          # token = self.ehcCliConfig.getToken()
            url = 'http://%s:%s/user/upload'%(host,port)
            header = {'Content-Type':'application/json','Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

class ProjectRequests():
    def __init__(self):
        self.apiData = ehcOpenApiData.projectOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def createProjectRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            data = self.apiData.createProject()
            url = 'http://%s:%s/projects'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def deleteProjectRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.deleteProject()
            url = 'http://%s:%s/projects/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.delete(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def projectListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            a = self.apiData.projectList()
            page = a[0]
            num  = a[1]
            orderkey = a[2]
            orderby = a[3]
            mine = a[4]
            keyword = a[5]
            url = 'http://%s:%s/projects?page=%s&num=%s&orderkey=%s&orderby=%s&mine=%s&keyword=%s'%(host,port,page,num,orderkey,orderby,mine,keyword)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def setupWorkSpaceRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            data = self.apiData.setupWorkspace()
            url = 'http://%s:%s/projects/workspace'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def updateProjectRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            a = self.apiData.updateProject()
            id =a[0]
            data = a[1]
            url = 'http://%s:%s/projects/:%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.put(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)


class resourceRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.resourceOpenApiHandler()
        self.ehcCliConfig = ehcCliConfig.ehcCliConfig()

    def hiveResourceListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            url = 'http://%s:%s/tf/resource/hive'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceCopyRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            a = self.apiData.resourceCopy()
            id = a[0]
            data = a[1]
            url = 'http://%s:%s/tf/resource/copy/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceCreateRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            data = self.apiData.resourceCreate()
            url = 'http://%s:%s/tf/resource'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceLifecycleTypeListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()

            url = 'http://%s:%s/tf/resource/lifecycletype'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()

            url = 'http://%s:%s/tf/resource'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourcePrivacyLevelListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()

            url = 'http://%s:%s/tf/resource/privacylevel'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceSpecifyTypeParamsRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            type = self.apiData.resourceSpecifyTypeParams()
            url = 'http://%s:%s/tf/resource/params/%s'%(host,port,type)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceTypeListRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()

            url = 'http://%s:%s/tf/resource/type'%(host,port)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.get(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def resourceUpdateRequests(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            a = self.apiData.resourceUpdate()
            id = a[0]
            data = a[1]
            url = 'http://%s:%s/tf/resource/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,data,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def deleteOneResource(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.deleteOneResource()
            url = 'http://%s:%s/tf/resource/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.delete(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def startOneResource(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.startOneResource()
            url = 'http://%s:%s/tf/resource/start/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def stopOneResource(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.stopOneResource()
            url = 'http://%s:%s/tf/resource/stop/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def terminateOneResource(self):
        try:
            host = self.ehcCliConfig.getAddress()
            port = self.ehcCliConfig.getPort()
            token = self.ehcCliConfig.getToken()
            _cookies = self.ehcCliConfig.getCookies()
            id = self.apiData.terminateOneResource()
            url = 'http://%s:%s/tf/resource/terminate/%s'%(host,port,id)
            header = {'Content-Type':'application/json','X-ACCESS-TOKEN':token,'Cookie':_cookies}
            r = requests.post(url,headers = header)
            print r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

class queryRequests:
    def __init__(self):
        self.apiData = ehcOpenApiData.queryOpenApiHandler()

    def query(self):
        try:
            message = self.apiData.query_m()
            ip = message[0]
            url = 'http://%s:%s/v1/query'%(ip[0],ip[1])
            data = message[1]
            r = requests.post(url,data)
            return r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def createQuery(self):
        try:
            message = self.apiData.createTable()
            ip = message[0]
            url = 'http://%s:%s/v1/query'%(ip[0],ip[1])
            data = message[1]
            r = requests.post(url,data)
            return r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)

    def deleteQuery(self):
        try:
            message = self.apiData.deleteTable()
            ip = message[0]
            url = 'http://%s:%s/v1/query'%(ip[0],ip[1])
            data = message[1]
            r = requests.post(url,data)
            return r.text
        except requests.RequestException as e:
            print e
            sys.exit(-1)