import sys
import ehcCliParser
import ehcCliHelp
import ehcCliConfig
import ehcOpenApiData
import ehcCliRequests
import json
import requests
import getpass
from prettytable import PrettyTable

class ehcExtensionCliHandler():
    def __init__(self):
        self.parser = ehcCliParser.ehcCliParser()
        self.helper = ehcCliHelp.ehcCliHelp()
        self.config = ehcCliConfig.ehcCliConfig()


        self.apiHandler = ehcOpenApiData.ehcOpenApiHandler()
        self.monitorApi = ehcOpenApiData.monitorOpenApiHandler()
        self.jobApi = ehcOpenApiData.jobOpenApiHandler()
        self.moduleApi = ehcOpenApiData.moduleOpenApiHandler()
        self.privilegeApi = ehcOpenApiData.privilegeOpenApiHandler()
        self.userApi = ehcOpenApiData.userOpenApiHandler()
        self.projectApi = ehcOpenApiData.projectOpenApiHandler()
        self.resourceApi = ehcOpenApiData.resourceOpenApiHandler()
        self.queryApi = ehcOpenApiData.queryOpenApiHandler()

        self.ehcCliRequests = ehcCliRequests.ehcCliRequests()
        self.monitorRequests = ehcCliRequests.monitorRequests()
        self.jobRequests = ehcCliRequests.jobRequests()
        self.moduleRequests = ehcCliRequests.moduleRequests()
        self.privilegeRequests = ehcCliRequests.privilegeRequests()
        self.userRequests = ehcCliRequests.UserRequests()
        self.projectRequests = ehcCliRequests.ProjectRequests()
        self.resourceRequests = ehcCliRequests.resourceRequests()
        self.queryRequests = ehcCliRequests.queryRequests()


        self.args = sys.argv[1:]

    def getAllExtensionCommands(self):
        cmdList = ['-h', '--help', 'help','config','login','eds','monitor','job','module','privilege','user','project','resource','query']
        return cmdList

    def handlerExtensionCmd(self,cmd):
        if cmd in ['help', '-h', '--help']:
            self.helper.showEhcCliCmdHelp()

        elif cmd == 'config':
            print 'ip:http://%s'%(self.config.getAddress())
            a = raw_input('whether to change?(y/n)')
            if a.lower() == 'y':
                host = raw_input('Input your eds address[%s]:'%self.config.getAddress())
                self.config.ehcHost(host)

                sys.exit(1)
            elif a.lower() == 'n':
                sys.exit(1)
            else:
                print 'Please input correct command!'
                sys.exit(-1)

        elif cmd == 'login':
            name = raw_input('Your username:')
            password = getpass.getpass('Your password:')
            try:
                jsonObj = {'account':name,'password':password}
                data = json.dumps(jsonObj)
                host = self.config.getAddress()
                port = self.config.getPort()
                url = 'http://%s/user/login'%(host)
                header = {'Content-Type':'application/json'}
                r = requests.post(url,data = data,headers = header)
                print r.text
                a = r.cookies.get_dict().get('express:sess')
                b = r.cookies.get_dict().get('express:sess.sig')
                try:
                    _cookies = 'express:sess='+a+';express:sess.sig='+b+';'
                    self.config.ehcCookies(_cookies)
                    print 'login success!'
                    s = json.loads(r.text)
                    token = s['data']['token']
                    self.config.ehcToken(token)
                except:
                    print 'please input right message!'

            except requests.RequestException as e:
                print e
                sys.exit(-1)

        elif cmd == 'eds':
            self.handlerExtensionEhcOperation()

        elif cmd == 'monitor':
            self.handlerExtensionRatChetOperation()

        elif cmd == 'job':
            self.handlerExtensionJobOperation()

        elif cmd == 'module':
            self.handlerExtensionModuleOperation()

        elif cmd == 'privilege':
            self.handlerExtensionPrivilegeOperation()

        elif cmd == 'user':
            self.handlerExtensionUserOperation()

        elif cmd == 'project':
            self.handlerExtensionProjectOperation()

        elif cmd == 'resource':
            self.handlerExtensionResourceOperation()

        elif cmd == 'query':
            self.handlerExtensionQueryOperation()

    def handlerExtensionEhcOperation(self):
        operation = self.parser.getCliOperation()
        if operation == 'edslist':
            self.apiHandler.ehcList()
            self.ehcCliRequests.ehcListRequest()
        elif operation == 'edsstatus':
            self.apiHandler.ehcStatus()
            self.ehcCliRequests.ehcStatusRequest()
        elif operation == 'namebyip':
            self.apiHandler.nameByIp()
            self.ehcCliRequests.nameByIpRequest()
        elif operation == 'submit':
            self.apiHandler.submit()
            self.ehcCliRequests.submitRequest()
        elif operation == 'createeds':
            self.apiHandler.createEhc()
            self.ehcCliRequests.createEhcRequest()
        elif operation == 'deleteeds':
            self.apiHandler.deleteEhc()
            self.ehcCliRequests.deleteEhcRequest()
        elif operation == 'listtables':
            self.apiHandler.listTables()
            self.ehcCliRequests.listTablesRequest()
        elif operation == 'rebooteds':
            self.apiHandler.rebootEhc()
            self.ehcCliRequests.rebootEhcRequest()
        elif operation == 'sqlquery':
            self.apiHandler.sqlQuery()
            self.ehcCliRequests.sqlQueryRequest()
        elif operation == 'sqlstatus':
            self.apiHandler.sqlStatus()
            self.ehcCliRequests.sqlStatusRequest()
        elif operation == 'starteds':
            self.apiHandler.startEhc()
            self.ehcCliRequests.startEhcRequest()
        elif operation == 'stopeds':
            self.apiHandler.stopEhc()
            self.ehcCliRequests.stopEhcRequest()
        elif operation == 'terminateeds':
            self.apiHandler.terminateEhc()
            self.ehcCliRequests.terminateEhcRequest()
        elif operation == 'updateeds':
            self.apiHandler.updateEhc()
            self.ehcCliRequests.updateEhcRequest()
        else:
            self.helper.showEhcCliCmdHelp()

    def handlerExtensionJobOperation(self):
        operation = self.parser.getJobCliOperation()
        if operation == 'createjobfromoutside':
            self.jobApi.createJobFromOutside()
            self.jobRequests.createJobFromOutsideRequests()

        elif operation == 'createjob':
            self.jobApi.createJob()
            self.jobRequests.createJobRequests()

        elif operation == 'jobstatus':
            self.jobApi.jobStatus()
            self.jobRequests.jobStatusRequests()

        elif operation == 'onlystatus':
            self.jobApi.onlyStatus()
            self.jobRequests.onlyStatusRequests()

        else:
            self.helper.showJobCmdOperation()

    def handlerExtensionRatChetOperation(self):
        operation = self.parser.getmonitorCliOperation()
        if operation == 'monitorcpu':
            self.monitorApi.monitorCpu()
            self.monitorRequests.monitorCpuRequests()
        elif operation == 'monitormemory':
            self.monitorApi.monitorMemory()
            self.monitorRequests.monitorMemoryRequests()
        elif operation == 'monitornetwork':
            self.monitorApi.monitorNetwork()
            self.monitorRequests.monitorNetworkRequests()
        elif operation == 'monitorheap':

            self.monitorRequests.monitorHeapRequests()
        elif operation == 'monitorhdfs':

            self.monitorRequests.monitorHdfs_capacityRequests()
        elif operation == 'monitorslavelive':

            self.monitorRequests.monitorSlave_liveRequests()
        elif operation == 'monitoralert':

            self.monitorRequests.monitorAlertRequests()
        elif operation == 'monitoralertnum':

            self.monitorRequests.monitorAlert_numRequests()
        elif operation == 'monitorhosts':

            self.monitorRequests.monitorHostsRequests()
        elif operation == 'monitorservices':

            self.monitorRequests.monitorServicesRequests()
        else :
            self.helper.showMonitorCmdOperation()

    def handlerExtensionModuleOperation(self):
        operation = self.parser.getModuleCliOperation()
        if operation == 'createmodule':
            self.moduleApi.createModule()
            self.moduleRequests.createModuleRequests()
        elif operation == 'moduledelete':
            self.moduleApi.moduleDelete()
            self.moduleRequests.moduleDeleteRequests()
        elif operation == 'modulecreateparams':
            self.moduleRequests.moduleCreateParamsRequests()
        elif operation == 'modulelist':
            self.moduleApi.moduleList()
            self.moduleRequests.moduleListRequests()
        elif operation == 'moduletags':
            self.moduleRequests.moduleTagsRequests()
        elif operation == 'moduleversionlist':
            self.moduleApi.ModuleVersionList()
            self.moduleRequests.moduleVersionListRequests()
        elif operation == 'searchmbyotype':
            self.moduleRequests.searchModuleByOutputTypeRequests()
        elif operation == 'updatemodule':

            self.moduleRequests.updateModuleRequests()
        else:
            self.helper.showModuleCmdOperation()

    def handlerExtensionPrivilegeOperation(self):
        operation = self.parser.getPrivilegeCliOperation()
        if operation == 'checkrule':
            self.privilegeApi.CheckRule()
            self.privilegeRequests.CheckRuleRequests()
        elif operation == 'getinstanceoperates':
            self.privilegeApi.GetInstanceOperates()
            self.privilegeRequests.GroupDetailRequests()
        elif operation == 'gettimestamp':
            self.privilegeRequests.GetTimeStampRequests()
        elif operation == 'groupdetail':
            self.privilegeApi.GroupDetail()
            self.privilegeRequests.GroupDetailRequests()
        elif operation == 'listgroups':
            self.privilegeRequests.ListGroupsRequests()
        elif operation == 'listresourcetypes':
            self.privilegeApi.ListResourceTypes()
            self.privilegeRequests.ListResourceTypesRequests()
        elif operation == 'listrole':
            self.privilegeRequests.ListRoleRequests()
        elif operation == 'roledetail':
            self.privilegeApi.RoleDetail()
            self.privilegeRequests.RoleDetailRequests()
        else:
            self.helper.showPrivilegeCmdOperation()


    def handlerExtensionUserOperation(self):
        operation = self.parser.getUserCliOperation()
        if operation == 'deleteuser':
            self.userApi.deleteUser()
            self.userRequests.deleteUserRequests()
        elif operation == 'gentoken':
            self.userRequests.genTokenRequests()
        elif operation == 'gettoken':
            self.userRequests.getTokenRequests()
        elif operation == 'userlogin':
           self.userApi.userLogin()
           self.userRequests.loginRequests()
        elif operation == 'userlogout':
            self.userRequests.logoutRequest()
        elif operation == 'setdefaultuserkey':
            self.userApi.setDefaultUserKey()
            self.userRequests.setDefaultUserKeyRequests()
        elif operation == 'userkeycreate':
            self.userApi.userKeyCreate()
            self.userRequests.userKeyCreateRequests()
        elif operation == 'userkeydefault':
            self.userRequests.userKeyDefaultRequests()
        elif operation == 'userkeydelete':
            self.userApi.userKeyDelete()
            self.userRequests.userKeyDeleteRequests()
        elif operation == 'userkeydetail':
            self.userApi.userKeyDetail()
            self.userRequests.userKeyDetailRequests()
        elif operation == 'userkeylist':
            self.userRequests.userKeyListRequests()
        elif operation == 'userkeyupdate':
            self.userApi.userKeyUpdate()
            self.userRequests.userListRequests()
        elif operation == 'userlist':
            self.userRequests.userListRequests()
        elif operation == 'userregister':
            self.userApi.userUpdate()
            self.userRequests.userKeyUpdate()
        elif operation == 'sendphoneverifysms':
            self.userApi.sendPhoneVerifySms()
            self.userRequests.sendPhoneVerifySmsRequests()
        elif operation == 'uploadavatar':
            self.userRequests.uploadAvatarRequests()
        else:
            self.helper.showUserCmdOperation()

    def handlerExtensionProjectOperation(self):
        operation = self.parser.getProjectCliOperation()
        if operation == 'createproject':
            self.projectApi.createProject()
            self.projectRequests.createProjectRequests()
        elif operation == 'deleteproject':
            self.projectApi.deleteProject()
            self.projectRequests.deleteProjectRequests()
        elif operation == 'projectlist':
            self.projectApi.projectList()
            self.projectRequests.projectListRequests()
        elif operation == 'setupworkspace':
            self.projectApi.setupWorkspace()
            self.projectRequests.setupWorkSpaceRequests()
        elif operation == 'updateproject':
            self.projectApi.updateProject()
            self.projectRequests.updateProjectRequests()
        else:
            self.helper.showProjectCmdOperation()

    def handlerExtensionResourceOperation(self):
        operation = self.parser.getResourceCliOperation()
        if operation == 'hiveresourcelist':
            self.resourceRequests.hiveResourceListRequests()
        elif operation == 'resourcecopy':
            self.resourceApi.resourceCopy()
            self.resourceRequests.resourceCopyRequests()
        elif operation == 'resourcecreate':
            self.resourceApi.resourceCreate()
            self.resourceRequests.resourceCreateRequests()
        elif operation == 'lifecycletypelist':
            self.resourceRequests.resourceLifecycleTypeListRequests()
        elif operation == 'resourcelist':
            self.resourceRequests.resourceListRequests()
        elif operation == 'privacylevellist':
            self.resourceRequests.resourcePrivacyLevelListRequests()
        elif operation == 'specifytypeparams':
            self.resourceApi.resourceSpecifyTypeParams()
            self.resourceRequests.resourceSpecifyTypeParamsRequests()
        elif operation == 'resourcetypelist':
            self.resourceRequests.resourceTypeListRequests()
        elif operation == 'resourceupdate':
            self.resourceApi.resourceUpdate()
            self.resourceRequests.resourceUpdateRequests()
        elif operation == 'deleteoneresource':
            self.resourceApi.deleteOneResource()
            self.resourceRequests.deleteOneResource()
        elif operation == 'startoneresource':
            self.resourceApi.startOneResource()
            self.resourceRequests.startOneResource()
        elif operation == 'stoponeresource':
            self.resourceApi.stopOneResource()
            self.resourceRequests.stopOneResource()
        elif operation == 'terminateoneresource':
            self.resourceApi.terminateOneResource()
            self.resourceRequests.terminateOneResource()
        else:
            self.helper.showResourceCmdOperation()

    def handlerExtensionQueryOperation(self):
        operation = self.parser.getQueryCliOperation()
        if operation == 'query':
            self.queryApi.query_m()
            self.queryRequests.query()
            r = self.queryRequests.query()
            js = r.json()
            if js['code'] == -1:
                print 'error'
                print r.text
                return
            while True:
                ip = self.queryApi.query_m()
                host = ip[0]
                port = ip[1]
                def _get_result(host, port, uid):
                    url = "http://%s:%s/v1/status?id=%s" % (host, port, uid)
                    r = requests.get(url)
                    if r.ok:
                        return r.json()
                    return None
                status_json = _get_result(host, port, js['message'])
                if not status_json:
                    print "[ERROR] Invalid response: %s" % status_json.content
                    return
                if status_json['code'] == -1:
                    print "[ERROR] Query Failed: %s" % status_json['message']
                    return
                if status_json['code'] == 1 and status_json['dataSetList']:

                    def _echo_result(data_list):
                        table = PrettyTable([column['name'] for column in data_list['columnHeaders']])
                        for row in data_list['rows']:
                            table.add_row([column['value'] for column in row['row']])
                        print table

                    for data_set in status_json['dataSetList']:
                        _echo_result(data_set)
                    break

                elif status_json['message'] == 'Processing':
                    print "Query results now, status:%s" % status_json['message']
                else:
                    print "[ERROR] Invalid response: %s" % status_json
                return
            else:
                print"[ERROR] Query Failed: %s" % r.content
                return
            print 'Query DONE'

        elif operation == 'createtable':
            self.queryApi.createTable()
            self.queryRequests.createQuery()
        elif operation == 'deletetable':
            self.queryApi.deleteTable()
            self.queryRequests.deleteQuery()
        else:
            self.helper.showQueryCmdOperation()



