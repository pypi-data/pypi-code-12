import xml.etree.ElementTree as xmltree

def getKey(xmlelem):

    if xmlelem.tag in [ "Action", "Widget", "Dialog"]:
        return getStrAttribute(xmlelem, "name")

    if xmlelem.tag in [ "MacroDir", "VarPrinterDir", "Extension"]:
        return getStrAttribute(xmlelem, "path")

    return hash(xmlelem)

class SettingElement(object):

    def __init__(self, defaultSettings = None, customSettings = None):
        self.defaultSettings = defaultSettings
        self.customSettings = customSettings

    def find(self, findStr):
        ds = None
        cs = None

        if None != self.customSettings: 
            cs = self.customSettings.find(findStr)

        if cs == None or not getBoolAttribute(cs, "replaceDefault"):
            if None != self.defaultSettings:
                ds = self.defaultSettings.find(findStr)

        return SettingElement(ds,cs)

    def findall(self, findStr):

        defLst = []
        cstLst = []
        if None != self.defaultSettings: defLst = self.defaultSettings.findall(findStr)
        if None != self.customSettings: cstLst = self.customSettings.findall(findStr)

        result = []
        for key, ds in ( (getKey(ds), ds) for ds in defLst):
            cs = next((cs for cs in cstLst if getKey(cs) == key), None)
            result.append( SettingElement(ds,cs) )
        for key, cs in ( (getKey(cs), cs) for cs in cstLst):
            ds = next((ds for ds in defLst if getKey(ds) == key), None)
            if not ds:
                result.append(SettingElement(None, cs))

        return result

    def get(self, name, default=None):
        if  None != self.customSettings:
            val = self.customSettings.get(name)
            if val: return val

        if  None != self.defaultSettings:
            val = self.defaultSettings.get(name)
            if val: return val

        return default


class DbgSettings(object):

    def __init__(self):
        self.rootxml = SettingElement()

    def loadDefaultSettings(self, fileName):
        try:
            self.rootxml.defaultSettings = xmltree.parse(fileName).getroot()
        except IOError:
           self.rootxml.defaultSettings = xmltree.fromstring('<Settings></Settings>')

    def loadCustomSettings(self, fileName):
        try:
            self.rootxml.customSettings = xmltree.parse(fileName).getroot()
        except IOError:
           self.rootxml.customSettings = xmltree.fromstring('<Settings></Settings>')

    def saveCustomSettings(self, fileName):
        try:
            self.rootxml.customSettings.write(fileName)
        except IOError:
            print "failed to save custom settings"

    @property
    def mainWindow(self):
        settingElem=self.rootxml.find("./MainWindow")
        return DbgMainWindowSettings(settingElem)

    @property
    def dbgEngExtensions(self):
        xmlelem=self.rootxml.find("./DbgEngExtensions")
        return [ DbgEngExtensionSetting(ext) for ext in xmlelem.findall("./Extension") ]

    @property
    def dbgEngExtensionsPath(self):
        return DbgEngExtensionPathSetting(self.rootxml.find("./DbgEngExtensionsPath"))

    @property
    def dbgEngSymPath(self):
        xmlelem=self.rootxml.find("./SymPath")
        return [ DbgEngSymbolsSetting(sympath) for sympath in xmlelem.findall("./Symbols") ]

    @property
    def MacroCommands(self):
        xmlelem=self.rootxml.find("./MacroCommands")
        return [ MacroCommandSetting(macrodir) for macrodir in xmlelem.findall("./MacroDir") ]

    @property
    def VarPrinters(self):
        xmlelem = self.rootxml.find("./VarPrinters")
        return [ VarPrinterSettings(dir) for dir in xmlelem.findall("./VarPrinters") ]

    @property
    def widgets(self):
        xmlelem=self.rootxml.find("./Widgets")
        return [ WidgetSettings(widget) for widget in xmlelem.findall("./Widget") ]

    @property
    def actions(self):
        xmlelem=self.rootxml.find("./Actions")
        return [ ActionSettings(action) for action in xmlelem.findall("./Action") ]

    @property
    def dialogs(self):
        xmlelem=self.rootxml.find("./Dialogs")
        return [ DialogSettings(action) for action in xmlelem.findall("./Dialog") ]

    @property
    def style(self):
        return DbgStyleSettings(self.rootxml.find("./Style"))

    @property
    def doccss(self):
        return DbgStyleSettings(self.rootxml.find("./DocCss"))

    @property
    def textCodec(self):
        xmlelem = self.rootxml.find("./TextCodec")
        return DbgTextCodecSettings(xmlelem) if xmlelem != None else None

    @property
    def mainMenu(self):
        return MainMenuSettings(self.rootxml.find("./MainMenu"))

    @property
    def guilayout(self):
        return DbgGuiLayoutSettings(self.rootxml.find("./GuiLayout"))
   

class DbgMainWindowSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def width(self):
        return getIntAttribute( self.xmlelem, "width", 800 )

    @property
    def height(self):
        return getIntAttribute( self.xmlelem , "height", 600 )

    @property
    def title(self):
        return getStrAttribute( self.xmlelem , "title", "Window Title" )


class MainMenuSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")

    @property
    def menuItems(self):
        return [ MenuItemSettings(item) for item in self.xmlelem.findall("./MenuItem") ]


class MenuItemSettings(object):

    def __init__(self,xmlelem):
        self.xmlelem=xmlelem

    @property
    def name(self):
        return getStrAttribute( self.xmlelem , "name")

    @property
    def actionName(self):
        return getStrAttribute( self.xmlelem , "actionName")

    @property
    def displayName(self):
        return getStrAttribute( self.xmlelem , "displayName")
        
    @property
    def separator(self):
        return getBoolAttribute(self.xmlelem, "separator")

    @property
    def toggleWidget(self):
        return getStrAttribute(self.xmlelem, "toggleWidget")

    @property
    def menuItems(self):
        return [ MenuItemSettings(item) for item in self.xmlelem.findall("./MenuItem") ]

class DbgStyleSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def fileName(self):
        return getStrAttribute(self.xmlelem, "fileName") if self.xmlelem != None else ""

    @property
    def text(self):
        return getStrAttribute(self.xmlelem, "text") if self.xmlelem != None else ""

class DbgGuiLayoutSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def fileName(self):
        return getStrAttribute(self.xmlelem, "fileName") if self.xmlelem != None else ""

    @property
    def saveOnClose(self):
        return getBoolAttribute(self.xmlelem, "saveOnClose")

class DbgTextCodecSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name") if self.xmlelem != None else ""

class DbgEngExtensionPathSetting(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def dir(self):
        return getStrAttribute(self.xmlelem, "dir") if self.xmlelem != None else ""

class DbgEngExtensionSetting(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name", self.path )

    @property
    def path(self):
        return getStrAttribute(self.xmlelem, "path")

    @property
    def startup(self):
        return getBoolAttribute(self.xmlelem, "startup")

class DbgEngSymbolsSetting(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name", self.path )

    @property
    def path(self):
        return getStrAttribute(self.xmlelem, "path")


class MacroCommandSetting(object):
    
    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def path(self):
        return getStrAttribute(self.xmlelem, "path")

class VarPrinterSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def path(self):
        return getStrAttribute(self.xmlelem, "path")

class WidgetSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")

    @property
    def behaviour(self):
        return getStrAttribute(self.xmlelem, "behaviour")

    @property
    def visible(self):
        return getBoolAttribute(self.xmlelem, "visible")

    @property
    def invisible(self):
        return getBoolAttribute(self.xmlelem, "invisible")

    @property
    def title(self):
        return getStrAttribute(self.xmlelem, "title")

class DialogSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")


class ActionSettings(object):
    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
        return getStrAttribute(self.xmlelem, "name")

    @property
    def displayName(self):
        return getStrAttribute(self.xmlelem, "displayName", self.name )

    @property
    def shortcut(self):
        return getStrAttribute(self.xmlelem, "shortcut")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def funcName(self):
        return getStrAttribute(self.xmlelem, "funcName")

    @property
    def toggleWidget(self):
        return getStrAttribute(self.xmlelem, "toggleWidget")

    @property
    def showDialog(self):
        return getStrAttribute(self.xmlelem, "showDialog")

    @property
    def showModal(self):
        return getStrAttribute(self.xmlelem, "showModal")

    @property
    def checkable(self):
        return getBoolAttribute(self.xmlelem, "checkable")

def getIntAttribute(xmlelem,name,default=0):
    try:
        val = xmlelem.get( name, default )
        return int(val)
    except ValueError:
        pass

    try:
        return int(val,16)
    except ValueError:
        pass

    return default

def getStrAttribute(xmlelem,name,default=""):
    return str( xmlelem.get( name, default ) )

def getBoolAttribute(xmlelem, name, default=False):
    val=xmlelem.get(name)
    if val==None:
        return default
    return val.lower()=="true"

