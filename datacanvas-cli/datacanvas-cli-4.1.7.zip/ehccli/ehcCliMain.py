import sys
import ehcCliParser
import ehcOpenApiData
import ehcExtensionCliHandler
import ehcCliHelp

class ehcCommandLine:
    def __init__(self):
        self.parser = ehcCliParser.ehcCliParser()
        self.helper = ehcCliHelp.ehcCliHelp()
        self.handler = ehcOpenApiData.ehcOpenApiHandler()
        self.extensionHandler = ehcExtensionCliHandler.ehcExtensionCliHandler()
        self.args = sys.argv[1:]

    def main(self):
        cmd = self.parser.getCliCmd()
        extensionCmdList = self.extensionHandler.getAllExtensionCommands()
        if cmd in extensionCmdList:
            self.handlerExtensionCmd(cmd)
        else:
            self.helper.showEhcCliCmdHelp()


    def handlerExtensionCmd(self,cmd):
        self.extensionHandler.handlerExtensionCmd(cmd)