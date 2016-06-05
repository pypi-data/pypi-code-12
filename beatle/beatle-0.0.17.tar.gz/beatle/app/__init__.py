# -*- coding: utf-8 -*-

from utils import import_once
from utils import isclass
from utils import cached_type
from utils import join_access
from utils import access_dict
from utils import store_access
from clipboard import clipboard

# import event identifiers
from proCxxGUI import ID_NEW_WORKSPACE
from proCxxGUI import ID_NEW_PROJECT
from proCxxGUI import ID_OPEN_PROJECT
from proCxxGUI import ID_IMPORT_PROJECT
from proCxxGUI import ID_SAVE_PROJECT
from proCxxGUI import ID_SAVE_WORKSPACE
from proCxxGUI import ID_CUT
from proCxxGUI import ID_EDIT_CONTEXT
from proCxxGUI import ID_EDIT_PROPERTIES
from proCxxGUI import ID_COPY
from proCxxGUI import ID_PASTE
from proCxxGUI import ID_DELETE
from proCxxGUI import ID_UNDO
from proCxxGUI import ID_REDO
from proCxxGUI import ID_COPY
from proCxxGUI import ID_EDIT_USER_SECTIONS
from proCxxGUI import ID_EDIT_OPEN
from proCxxGUI import ID_EDIT_CONTEXT
from proCxxGUI import ID_CLOSE_WORKSPACE
from proCxxGUI import ID_CLOSE_PROJECT


from proCxxGUI import NavigatorPane
from proCxxGUI import NewFolder
from proCxxGUI import NewProject
from proCxxGUI import ImportProject
from proCxxGUI import Import
from proCxxGUI import NewWorkspace
from proCxxGUI import TasksPane
from proCxxGUI import Preferences
from proCxxGUI import BuildTools
from proCxxGUI import BuildBinaries
from proCxxGUI import NewNote
from proCxxGUI import NewFile
from proCxxGUI import codeNavigator
from proCxxGUI import FullScreen
from proCxxGUI import Wait
from proCxxGUI import Working
from proCxxGUI import FindText
from proCxxGUI import FindInFiles
from proCxxGUI import PdfViewPane
from mainWindow import mainWindow

#from bmpTools import dumpBitmap
from bmpTools import PrefixBitmapList
from bmpTools import SuffixBitmapList
from bmpTools import GetBitmapMaxSize
from main import proCxx
from resources import GetBitmap
from splash import AppSplashScreen

from ui import edit
from ui import append_menuitem_copy
from ui import clone_mnu
from ui import set_menu_handlers
from ui import unset_menu_handlers
