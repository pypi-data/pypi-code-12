import sys
import os
import time

from threading import Thread

import karmadbg

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.dbgcore.dbgengine import DbgEngine, ConsoleDebugClient, LocalDebugServer


dbgEngine = None

class DebugClient(ConsoleDebugClient):

    def __init__(self):
        super(DebugClient,self).__init__()
        self.stopped = False

    def quit(self):
        print "debugger stopping..."
        self.stopped = True

    def dbgLoop(self):

        print "KarmaDbg console client. Version %s" % karmadbg.__version__ 

        global dbgEngine

        dbgControl = dbgEngine.getServer().getServerControl()

        while not self.stopped:
            prompt = dbgControl.getPrompt()
            str = raw_input(prompt)
            dbgControl.debugCommand(str)

def main():

    global dbgEngine

    dirname = os.path.dirname(karmadbg.__file__)
    defaultSettingFile = os.path.join( dirname, "settings", "default.xml" )
    homedir = os.path.join( os.path.expanduser("~"), ".karmadbg")
    userSettingsFile = os.path.join( homedir, "default.xml" )

    dbgSettings = DbgSettings()
    dbgSettings.loadSettings(defaultSettingFile)
    dbgSettings.loadSettings(userSettingsFile, policy='overwrite')

    dbgClient = DebugClient()
    dbgServer = LocalDebugServer()

    dbgEngine = DbgEngine( dbgClient, dbgServer, dbgSettings )

    dbgEngine.start();

    thread = Thread(target=dbgClient.dbgLoop )
    thread.start()

    while True:
        try:
            thread.join(1000000)
            break
        except KeyboardInterrupt:
            dbgEngine.getServer().getServerInterrupt().breakin()

    thread.join()


if __name__ == "__main__":
    main()

