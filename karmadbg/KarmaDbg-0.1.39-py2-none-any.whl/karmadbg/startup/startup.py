import os
import pykd 

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.dbgcore.macro import registerMacrosInDir
from karmadbg.dbgcore.varprint import registerVarPrintersInDir

def startup():

    import karmadbg
    projdir =  os.path.dirname(karmadbg.__file__)
    defaultSettingFile =  os.path.join(projdir, "settings", "default.xml")

    configdir = os.getenv("KARMADBG_CONFIG", None)
    if not configdir:
        projectSettingFile =  os.path.join(projdir, "default.xml")
        if os.path.exists(projectSettingFile) :
            configdir = projdir

    if not configdir:
        configdir = os.path.join(  os.path.expandvars("$USERPROFILE"), ".karmadbg")

    userSettingsFile = os.path.join( configdir, "default.xml" )

    dbgSettings = DbgSettings()
    dbgSettings.loadDefaultSettings(defaultSettingFile)
    dbgSettings.loadCustomSettings(userSettingsFile)

    if hasattr(dbgSettings, "dbgEngExtensionsPath"):
        cmdStr = ".extpath " + dbgSettings.dbgEngExtensionsPath.dir
        print cmdStr
        pykd.dbgCommand(cmdStr)

    if hasattr(dbgSettings, "dbgEngExtensions") and len(dbgSettings.dbgEngExtensions) > 0:
        print ""
        print "loading DbgEng extensions:"
        for ext in dbgSettings.dbgEngExtensions:
            if ext.startup:
                cmdStr = ".load %s" % ext.path
                print cmdStr
                pykd.dbgCommand(cmdStr)

    if hasattr(dbgSettings, "dbgEngSymPath") and len(dbgSettings.dbgEngSymPath) > 0:
        print ""
        print "setup DbgEng symbols path:"
        for sym in dbgSettings.dbgEngSymPath:
            cmdStr = ".sympath+ %s" % sym.path
            print cmdStr
            pykd.dbgCommand(cmdStr)
        print ""


    if hasattr(dbgSettings, "MacroCommands"):
        for macrodir in dbgSettings.MacroCommands:
            path = macrodir.path.replace('$config', configdir)
            registerMacrosInDir(path)

    usermacrodir =  os.path.join(configdir, "macros")
    if os.path.exists( usermacrodir ):
         registerMacrosInDir(usermacrodir)

    if hasattr(dbgSettings, "VarPrinters"):
        for dir in dbgSettings.VarPrinters:
            path = dir.path.replace('$config', configdir)
            registerVarPrintersInDir(path)

    uservarprintersdir =  os.path.join(configdir, "varprinters")
    if os.path.exists( uservarprintersdir ):
         registerVarPrintersInDir(uservarprintersdir)

