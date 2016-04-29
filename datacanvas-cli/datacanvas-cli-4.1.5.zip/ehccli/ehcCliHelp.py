import platform
import ConfigParser

class ehcCliHelp:
    class color:
      if platform.system() == "Windows":
        purple = ''
        cyan = ''
        blue = ''
        green = ''
        yellow = ''
        red  = ''
        bold = ''
        underline = ''
        end = ''
      else:
        purple = '\033[95m'
        cyan = '\033[96m'
        blue = '\033[94m'
        green = '\033[92m'
        yellow = '\033[93m'
        red  = '\033[91m'
        bold = '\033[1m'
        underline = '\033[4m'
        end = '\033[0m'


    def showEhcCliCmdHelp(self):
        print self.color.bold+"NAME:"+self.color.end
        print "datacanvas-cli "
        print self.color.bold+"\nDESCRIPTION:"+self.color.end
        print "The datacanvas Command Line Interface is a unified tool to manage your datacanvas services. "
        print self.color.bold+"SYNOPSIS\n"+self.color.end
        print "datacanvas <command> <operation> [options and parameters]"
        print "datacanvas has supported command completion now. The detail you can check our site."
        print '****************************************************************'
        print self.color.bold+"You can change config as follow:"+self.color.end
        print self.color.bold+"o config : Your ip!" +self.color.end
        print self.color.bold+"o login : Login ,some api need login first!" +self.color.end

        print self.color.bold+"The commands: "+self.color.end
        print self.color.bold+"o user" +self.color.end
        print self.color.bold+"o eds" +self.color.end
        print self.color.bold+"o job" +self.color.end
        print self.color.bold+"o module" +self.color.end
        print self.color.bold+"o privilege" +self.color.end
        print self.color.bold+"o project" +self.color.end
        print self.color.bold+"o resource" +self.color.end


    def showEhcCliCmdOperation(self):
        print self.color.bold+"ehcOperation:"+self.color.end

        print 'The operations as follow will help you use eds:'
        print self.color.bold+"o edslist"+self.color.end
        print self.color.bold+"o edsstatus"+self.color.end
        print self.color.bold+"o namebyip"+self.color.end
        print self.color.bold+"o createeds"+self.color.end
        print self.color.bold+"o deleteeds"+self.color.end
        print self.color.bold+"o listtables"+self.color.end
        print self.color.bold+"o rebooteds"+self.color.end
        print self.color.bold+"o sqlquery"+self.color.end
        print self.color.bold+"o sqlstatus"+self.color.end
        print self.color.bold+"o starteds"+self.color.end
        print self.color.bold+"o stopeds"+self.color.end
        print self.color.bold+"o terminateeds"+self.color.end
        print self.color.bold+"o updateeds"+self.color.end

        print "The ehc Command Line Interface is a unified tool to manage your ehc services. "

    def showMonitorCmdOperation(self):
        print self.color.bold+"monitorOperation:"+self.color.end

        print 'The operations as follow will help you use monitor:'
        print self.color.bold+"o monitorcpu"+self.color.end
        print self.color.bold+"o monitormemory"+self.color.end
        print self.color.bold+"o monitornetwork"+self.color.end
        print self.color.bold+"o monitorheap"+self.color.end
        print self.color.bold+"o monitorhdfs"+self.color.end
        print self.color.bold+"o monitorslavelive"+self.color.end
        print self.color.bold+"o monitoralert"+self.color.end
        print self.color.bold+"o monitoralertnum"+self.color.end
        print self.color.bold+"o monitorhosts"+self.color.end
        print self.color.bold+"o monitorservices"+self.color.end


    def showJobCmdOperation(self):
        print self.color.bold+"JobOperation:"+self.color.end

        print 'The operations as follow will help you use job:'
        print self.color.bold+"o createjob"+self.color.end
        print self.color.bold+"o jobstatus"+self.color.end

    def showModuleCmdOperation(self):
        print self.color.bold+"moduleOperation:"+self.color.end

        print 'The operations as follow will help you use module:'
        print self.color.bold+"o createmodule"+self.color.end
        print self.color.bold+"o moduledelete"+self.color.end
        print self.color.bold+"o modulecreateparams"+self.color.end
        print self.color.bold+"o modulelist"+self.color.end
        print self.color.bold+"o moduletags"+self.color.end
        print self.color.bold+"o moduleversionlist"+self.color.end
        print self.color.bold+"o searchmbyotype"+self.color.end
        print self.color.bold+"o updatemodule"+self.color.end

    def showPrivilegeCmdOperation(self):
        print self.color.bold+"privilegeOperation:"+self.color.end

        print 'The operations as follow will help you use privilege:'
        print self.color.bold+"o checkrule"+self.color.end
        print self.color.bold+"o getinstanceoperates"+self.color.end
        print self.color.bold+"o gettimestamp"+self.color.end
        print self.color.bold+"o groupdetail"+self.color.end
        print self.color.bold+"o listgroups"+self.color.end
        print self.color.bold+"o listresourcetypes"+self.color.end
        print self.color.bold+"o listrole"+self.color.end
        print self.color.bold+"o roledetail"+self.color.end


    def showUserCmdOperation(self):
        print self.color.bold+"userOperation:"+self.color.end

        print 'The operations as follow will help you use User:'
        print self.color.bold+"o deleteuser"+self.color.end
        print self.color.bold+"o gentoken"+self.color.end
        print self.color.bold+"o gettoken"+self.color.end
        print self.color.bold+"o userlogin"+self.color.end
        print self.color.bold+"o userlogout"+self.color.end
        print self.color.bold+"o setdefaultuserkey"+self.color.end
        print self.color.bold+"o userkeycreate"+self.color.end
        print self.color.bold+"o userkeydefault"+self.color.end
        print self.color.bold+"o userkeydetail"+self.color.end
        print self.color.bold+"o userkeydelete"+self.color.end
        print self.color.bold+"o userkeylist"+self.color.end
        print self.color.bold+"o userkeyupdate"+self.color.end
        print self.color.bold+"o userlist"+self.color.end
        print self.color.bold+"o userregister"+self.color.end
        print self.color.bold+"o userupdate"+self.color.end
        print self.color.bold+"o sendphoneverifysms"+self.color.end
        print self.color.bold+"o uploadavatar"+self.color.end

    def showProjectCmdOperation(self):
        print self.color.bold+"projectOperation:"+self.color.end

        print 'The operations as follow will help you use Project:'
        print self.color.bold+"o createproject"+self.color.end
        print self.color.bold+"o deleteproject"+self.color.end
        print self.color.bold+"o projectlist"+self.color.end
        print self.color.bold+"o setupworkspace"+self.color.end
        print self.color.bold+"o updateproject"+self.color.end

    def showResourceCmdOperation(self):
        print self.color.bold+"ResourceOperation:"+self.color.end

        print 'The operations as follow will help you use resource:'
        print self.color.bold+"o hiveresourcelist"+self.color.end
        print self.color.bold+"o resourcecopy"+self.color.end
        print self.color.bold+"o resourcecreate"+self.color.end
        print self.color.bold+"o lifecycletypelist"+self.color.end
        print self.color.bold+"o resourcelist"+self.color.end
        print self.color.bold+"o privacylevellist"+self.color.end
        print self.color.bold+"o specifytypeparams"+self.color.end
        print self.color.bold+"o resourcetypelist"+self.color.end
        print self.color.bold+"o resourceupdate"+self.color.end
        print self.color.bold+"o deleteoneresource"+self.color.end
        print self.color.bold+"o startoneresource"+self.color.end
        print self.color.bold+"o stoponeresource"+self.color.end
        print self.color.bold+"o terminateoneresource"+self.color.end

    def showQueryCmdOperation(self):
        print self.color.bold+"QueryOperation:"+self.color.end

        print 'The operations as follow will help you use query:'
        print self.color.bold+"o query"+self.color.end
        print self.color.bold+"o createtable"+self.color.end
        print self.color.bold+"o deletetable"+self.color.end