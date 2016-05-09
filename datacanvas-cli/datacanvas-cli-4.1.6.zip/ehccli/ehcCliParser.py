import sys
import ehcCliHelp


class ehcCliParser:
    def __init__(self):
     self.args = sys.argv[1:]
     self.helper = ehcCliHelp.ehcCliHelp()

    def getCliCmd(self):
        if self.args.__len__() >= 1:
            return self.args[0].lower()
        else:
            self.helper.showEhcCliCmdHelp()
            sys.exit(-1)

    def getCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showEhcCliCmdOperation()
            sys.exit(-1)

    def getehcCliConfig(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showEhcCliCmdOperation()
            sys.exit(-1)

    def getmonitorCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showMonitorCmdOperation()
            sys.exit(-1)

    def getJobCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showJobCmdOperation()
            sys.exit(-1)

    def getModuleCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showModuleCmdOperation()
            sys.exit(-1)

    def getPrivilegeCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showPrivilegeCmdOperation()
            sys.exit(-1)

    def getUserCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showUserCmdOperation()
            sys.exit(-1)

    def getProjectCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showProjectCmdOperation()
            sys.exit(-1)

    def getResourceCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showResourceCmdOperation()
            sys.exit(-1)

    def getQueryCliOperation(self):
        if self.args.__len__() >= 2:
            return self.args[1]
        else:
            self.helper.showQueryCmdOperation()
            sys.exit(-1)