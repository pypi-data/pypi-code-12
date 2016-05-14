# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version May 10 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.html2
import wxx
import wx.richtext
from wx.lib.pdfviewer import pdfViewer
import wx.aui
import wx.animate

ID_NEW_WORKSPACE = 1000
ID_NEW_PROJECT = 1001
ID_OPEN_WORKSPACE = 1002
ID_OPEN_PROJECT = 1003
ID_CLOSE_WORKSPACE = 1004
ID_CLOSE_PROJECT = 1005
ID_IMPORT_PROJECT = 1006
ID_SAVE_WORKSPACE = 1007
ID_SAVE_PROJECT = 1008
ID_QUIT = 1009
ID_UNDO = 1010
ID_REDO = 1011
ID_COPY = 1012
ID_CUT = 1013
ID_PASTE = 1014
ID_DELETE = 1015
ID_EDIT_OPEN = 1016
ID_EDIT_CONTEXT = 1017
ID_EDIT_USER_SECTIONS = 1018
ID_EDIT_PROPERTIES = 1019
ID_PREFERENCES = 1020

###########################################################################
## Class FontPreferences
###########################################################################

class FontPreferences ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer78 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer78.AddGrowableCol( 1 )
		fgSizer78.SetFlexibleDirection( wx.BOTH )
		fgSizer78.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText44 = wx.StaticText( self, wx.ID_ANY, u"Defaul text font:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44.Wrap( -1 )
		fgSizer78.Add( self.m_staticText44, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_fontPicker = wx.FontPickerCtrl( self, wx.ID_ANY, wx.NullFont, wx.DefaultPosition, wx.DefaultSize, wx.FNTP_DEFAULT_STYLE )
		self.m_fontPicker.SetMaxPointSize( 100 )
		fgSizer78.Add( self.m_fontPicker, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer78 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class NavigatorPane
###########################################################################

class NavigatorPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNSHADOW ) )
		self.SetBackgroundColour( wx.Colour( 0, 3, 135 ) )
		
		fgSizer193 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer193.AddGrowableCol( 0 )
		fgSizer193.AddGrowableRow( 1 )
		fgSizer193.SetFlexibleDirection( wx.BOTH )
		fgSizer193.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_url = wx.TextCtrl( self, wx.ID_ANY, u"aa", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.SIMPLE_BORDER )
		self.m_url.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 94, 90, False, "Arial" ) )
		self.m_url.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DDKSHADOW ) )
		self.m_url.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
		
		fgSizer193.Add( self.m_url, 0, wx.EXPAND, 5 )
		
		self.m_page = wx.html2.WebView.New(self)
		fgSizer193.Add( self.m_page, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer193 )
		self.Layout()
		
		# Connect Events
		self.m_url.Bind( wx.EVT_TEXT_ENTER, self.OnEnterUrl )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnEnterUrl( self, event ):
		event.Skip()
	

###########################################################################
## Class TasksPane
###########################################################################

class TasksPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 731,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer91 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer91.AddGrowableCol( 1 )
		fgSizer91.AddGrowableRow( 0 )
		fgSizer91.SetFlexibleDirection( wx.BOTH )
		fgSizer91.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_listCtrl2 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		fgSizer91.Add( self.m_listCtrl2, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer92 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer92.AddGrowableCol( 0 )
		fgSizer92.AddGrowableRow( 1 )
		fgSizer92.SetFlexibleDirection( wx.BOTH )
		fgSizer92.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer93 = wx.FlexGridSizer( 2, 4, 0, 0 )
		fgSizer93.AddGrowableCol( 1 )
		fgSizer93.AddGrowableCol( 3 )
		fgSizer93.SetFlexibleDirection( wx.BOTH )
		fgSizer93.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText50 = wx.StaticText( self, wx.ID_ANY, u"task", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText50.Wrap( -1 )
		fgSizer93.Add( self.m_staticText50, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl34 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer93.Add( self.m_textCtrl34, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText51 = wx.StaticText( self, wx.ID_ANY, u"status", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText51.Wrap( -1 )
		fgSizer93.Add( self.m_staticText51, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice20Choices = [ u"pending", u"doing", u"done", wx.EmptyString, wx.EmptyString, wx.EmptyString ]
		self.m_choice20 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice20Choices, 0 )
		self.m_choice20.SetSelection( 0 )
		fgSizer93.Add( self.m_choice20, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText52 = wx.StaticText( self, wx.ID_ANY, u"priority", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText52.Wrap( -1 )
		fgSizer93.Add( self.m_staticText52, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice21Choices = [ u"High", u"Normal", u"Low" ]
		self.m_choice21 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice21Choices, 0 )
		self.m_choice21.SetSelection( 1 )
		fgSizer93.Add( self.m_choice21, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText53 = wx.StaticText( self, wx.ID_ANY, u"type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText53.Wrap( -1 )
		fgSizer93.Add( self.m_staticText53, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice22Choices = [ u"BUG", u"CHANGE", u"IMPROVE" ]
		self.m_choice22 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice22Choices, 0 )
		self.m_choice22.SetSelection( 1 )
		fgSizer93.Add( self.m_choice22, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer92.Add( fgSizer93, 1, wx.EXPAND, 5 )
		
		sbSizer22 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Comments" ), wx.VERTICAL )
		
		self.m_richText16 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		sbSizer22.Add( self.m_richText16, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer92.Add( sbSizer22, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer91.Add( fgSizer92, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer91 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class BuildBinaries
###########################################################################

class BuildBinaries ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer102 = wx.FlexGridSizer( 5, 3, 0, 0 )
		fgSizer102.AddGrowableCol( 1 )
		fgSizer102.SetFlexibleDirection( wx.BOTH )
		fgSizer102.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText65 = wx.StaticText( self, wx.ID_ANY, u"C++ compiler:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText65.Wrap( -1 )
		fgSizer102.Add( self.m_staticText65, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl41 = wx.TextCtrl( self, wx.ID_ANY, u"g++", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer102.Add( self.m_textCtrl41, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_bpButton3 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer102.Add( self.m_bpButton3, 0, wx.ALL, 5 )
		
		self.m_staticText66 = wx.StaticText( self, wx.ID_ANY, u"shared libraries linker:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText66.Wrap( -1 )
		fgSizer102.Add( self.m_staticText66, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl411 = wx.TextCtrl( self, wx.ID_ANY, u"g++", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer102.Add( self.m_textCtrl411, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_bpButton31 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer102.Add( self.m_bpButton31, 0, wx.ALL, 5 )
		
		self.m_staticText67 = wx.StaticText( self, wx.ID_ANY, u"static libraries linker:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText67.Wrap( -1 )
		fgSizer102.Add( self.m_staticText67, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl4111 = wx.TextCtrl( self, wx.ID_ANY, u"ar", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer102.Add( self.m_textCtrl4111, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_bpButton311 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer102.Add( self.m_bpButton311, 0, wx.ALL, 5 )
		
		self.m_staticText651 = wx.StaticText( self, wx.ID_ANY, u"make:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText651.Wrap( -1 )
		fgSizer102.Add( self.m_staticText651, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl41111 = wx.TextCtrl( self, wx.ID_ANY, u"make", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer102.Add( self.m_textCtrl41111, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_bpButton3111 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer102.Add( self.m_bpButton3111, 0, wx.ALL, 5 )
		
		
		self.SetSizer( fgSizer102 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class PdfViewPane
###########################################################################

class PdfViewPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.TRANSPARENT_WINDOW )
		
		fgSizer52 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer52.AddGrowableCol( 0 )
		fgSizer52.AddGrowableRow( 0 )
		fgSizer52.SetFlexibleDirection( wx.BOTH )
		fgSizer52.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_pdfView = pdfViewer(self, wx.NewId(), wx.DefaultPosition,
		wx.DefaultSize,
		wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
		self.m_pdfView.SetExtraStyle( wx.WS_EX_PROCESS_IDLE|wx.WS_EX_PROCESS_UI_UPDATES )
		
		fgSizer52.Add( self.m_pdfView, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer52 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class BuildTools
###########################################################################

class BuildTools ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"C++ Build tools", pos = wx.DefaultPosition, size = wx.Size( 537,301 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer101 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer101.AddGrowableCol( 0 )
		fgSizer101.AddGrowableRow( 0 )
		fgSizer101.SetFlexibleDirection( wx.BOTH )
		fgSizer101.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer158 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer158.AddGrowableCol( 0 )
		fgSizer158.AddGrowableRow( 0 )
		fgSizer158.SetFlexibleDirection( wx.BOTH )
		fgSizer158.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_listbook2 = wx.Listbook( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.LB_RIGHT )
		self.m_panel21 = wx.Panel( self.m_listbook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer157 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer157.AddGrowableCol( 0 )
		fgSizer157.AddGrowableRow( 0 )
		fgSizer157.SetFlexibleDirection( wx.BOTH )
		fgSizer157.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_auinotebook4 = wx.aui.AuiNotebook( self.m_panel21, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_BOTTOM )
		
		fgSizer157.Add( self.m_auinotebook4, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.m_panel21.SetSizer( fgSizer157 )
		self.m_panel21.Layout()
		fgSizer157.Fit( self.m_panel21 )
		self.m_listbook2.AddPage( self.m_panel21, u"linux gnu", False )
		
		fgSizer158.Add( self.m_listbook2, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer159 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer159.AddGrowableRow( 3 )
		fgSizer159.SetFlexibleDirection( wx.BOTH )
		fgSizer159.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_bpButton49 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_NEW, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer159.Add( self.m_bpButton49, 0, wx.ALL, 5 )
		
		self.m_bpButton50 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_INFORMATION, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer159.Add( self.m_bpButton50, 0, wx.ALL, 5 )
		
		self.m_bpButton51 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton51.Enable( False )
		
		fgSizer159.Add( self.m_bpButton51, 0, wx.ALL, 5 )
		
		
		fgSizer158.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		fgSizer101.Add( fgSizer158, 1, wx.EXPAND, 5 )
		
		fgSizer155 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer155.AddGrowableCol( 1 )
		fgSizer155.SetFlexibleDirection( wx.BOTH )
		fgSizer155.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer155.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer6 = wx.StdDialogButtonSizer()
		self.m_sdbSizer6OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer6.AddButton( self.m_sdbSizer6OK )
		self.m_sdbSizer6Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer6.AddButton( self.m_sdbSizer6Cancel )
		m_sdbSizer6.Realize();
		
		fgSizer155.Add( m_sdbSizer6, 1, wx.EXPAND, 5 )
		
		
		fgSizer101.Add( fgSizer155, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer101 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_bpButton49.Bind( wx.EVT_BUTTON, self.OnAddBinariesProfile )
		self.m_bpButton50.Bind( wx.EVT_BUTTON, self.OnEditBinariesProfile )
		self.m_bpButton51.Bind( wx.EVT_BUTTON, self.OnDeleteBinariesProfile )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnAddBinariesProfile( self, event ):
		event.Skip()
	
	def OnEditBinariesProfile( self, event ):
		event.Skip()
	
	def OnDeleteBinariesProfile( self, event ):
		event.Skip()
	

###########################################################################
## Class NewFile
###########################################################################

class NewFile ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"NewFile", pos = wx.DefaultPosition, size = wx.Size( 260,120 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer125 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer125.AddGrowableCol( 0 )
		fgSizer125.AddGrowableRow( 0 )
		fgSizer125.SetFlexibleDirection( wx.BOTH )
		fgSizer125.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer126 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer126.AddGrowableCol( 1 )
		fgSizer126.SetFlexibleDirection( wx.BOTH )
		fgSizer126.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		self.m_staticText85 = wx.StaticText( self, wx.ID_ANY, u"File name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText85.Wrap( -1 )
		fgSizer126.Add( self.m_staticText85, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl56 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl56.SetMinSize( wx.Size( 150,-1 ) )
		
		fgSizer126.Add( self.m_textCtrl56, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		fgSizer125.Add( fgSizer126, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		fgSizer158 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer158.AddGrowableCol( 1 )
		fgSizer158.SetFlexibleDirection( wx.BOTH )
		fgSizer158.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer158.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer10 = wx.StdDialogButtonSizer()
		self.m_sdbSizer10OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer10.AddButton( self.m_sdbSizer10OK )
		self.m_sdbSizer10Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer10.AddButton( self.m_sdbSizer10Cancel )
		m_sdbSizer10.Realize();
		
		fgSizer158.Add( m_sdbSizer10, 1, wx.EXPAND, 5 )
		
		
		fgSizer125.Add( fgSizer158, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer125 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class NewFolder
###########################################################################

class NewFolder ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New folder", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer6 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.AddGrowableRow( 1 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer7 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer7.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textCtrl2, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		fgSizer6.Add( fgSizer7, 0, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer6.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer162 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer162.AddGrowableCol( 1 )
		fgSizer162.SetFlexibleDirection( wx.BOTH )
		fgSizer162.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer162.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
		self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
		m_sdbSizer2.Realize();
		
		fgSizer162.Add( m_sdbSizer2, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		
		fgSizer6.Add( fgSizer162, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer2OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class codeNavigator
###########################################################################

class codeNavigator ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.Point( -1,-1 ), size = wx.Size( 284,404 ), style = 0|wx.NO_BORDER|wx.WANTS_CHARS )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer131 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer131.AddGrowableCol( 0 )
		fgSizer131.AddGrowableRow( 0 )
		fgSizer131.SetFlexibleDirection( wx.BOTH )
		fgSizer131.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_treeCtrl3 = wx.TreeCtrl( self, wx.ID_ANY, wx.Point( 0,0 ), wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE )
		fgSizer131.Add( self.m_treeCtrl3, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		self.SetSizer( fgSizer131 )
		self.Layout()
		
		# Connect Events
		self.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_treeCtrl3.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_treeCtrl3.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelectedItem )
		self.m_treeCtrl3.Bind( wx.EVT_TREE_ITEM_EXPANDED, self.OnExpandItem )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnKeyDown( self, event ):
		event.Skip()
	
	
	def OnSelectedItem( self, event ):
		event.Skip()
	
	def OnExpandItem( self, event ):
		event.Skip()
	

###########################################################################
## Class Import
###########################################################################

class Import ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class NewNote
###########################################################################

class NewNote ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New note", pos = wx.DefaultPosition, size = wx.Size( 480,299 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer103 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer103.AddGrowableCol( 0 )
		fgSizer103.AddGrowableRow( 0 )
		fgSizer103.SetFlexibleDirection( wx.BOTH )
		fgSizer103.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer30 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )
		
		self.m_text = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		sbSizer30.Add( self.m_text, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer103.Add( sbSizer30, 1, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer156 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer156.AddGrowableCol( 1 )
		fgSizer156.SetFlexibleDirection( wx.BOTH )
		fgSizer156.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer156.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer7 = wx.StdDialogButtonSizer()
		self.m_sdbSizer7OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer7.AddButton( self.m_sdbSizer7OK )
		self.m_sdbSizer7Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer7.AddButton( self.m_sdbSizer7Cancel )
		m_sdbSizer7.Realize();
		
		fgSizer156.Add( m_sdbSizer7, 1, wx.EXPAND, 5 )
		
		
		fgSizer103.Add( fgSizer156, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer103 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer7OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewProject
###########################################################################

class NewProject ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Project", pos = wx.DefaultPosition, size = wx.Size( 433,427 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer4 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer4.AddGrowableCol( 0 )
		fgSizer4.AddGrowableRow( 0 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		self.m_auinotebook2 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_BOTTOM )
		self.m_panel5 = wx.Panel( self.m_auinotebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer65 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer65.AddGrowableCol( 0 )
		fgSizer65.AddGrowableRow( 1 )
		fgSizer65.SetFlexibleDirection( wx.BOTH )
		fgSizer65.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer5 = wx.FlexGridSizer( 5, 2, 0, 0 )
		fgSizer5.AddGrowableCol( 1 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText2 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		fgSizer5.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl1 = wx.TextCtrl( self.m_panel5, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer5.Add( self.m_textCtrl1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText3 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"Base directory:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		fgSizer5.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		fgSizer29 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer29.AddGrowableCol( 0 )
		fgSizer29.SetFlexibleDirection( wx.BOTH )
		fgSizer29.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_textCtrl9 = wx.TextCtrl( self.m_panel5, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		fgSizer29.Add( self.m_textCtrl9, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_bpButton3 = wx.BitmapButton( self.m_panel5, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FOLDER_OPEN, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer29.Add( self.m_bpButton3, 0, wx.ALL, 5 )
		
		
		fgSizer5.Add( fgSizer29, 1, wx.EXPAND, 5 )
		
		
		fgSizer65.Add( fgSizer5, 1, wx.EXPAND|wx.ALL, 5 )
		
		self.m_choicebook1 = wx.Choicebook( self.m_panel5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel18 = wx.Panel( self.m_choicebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer130 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer130.AddGrowableCol( 1 )
		fgSizer130.SetFlexibleDirection( wx.BOTH )
		fgSizer130.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText30 = wx.StaticText( self.m_panel18, wx.ID_ANY, u"Headers subdir.:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )
		fgSizer130.Add( self.m_staticText30, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl23 = wx.TextCtrl( self.m_panel18, wx.ID_ANY, u"include", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer130.Add( self.m_textCtrl23, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText31 = wx.StaticText( self.m_panel18, wx.ID_ANY, u"Sources subdir.:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )
		fgSizer130.Add( self.m_staticText31, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl24 = wx.TextCtrl( self.m_panel18, wx.ID_ANY, u"src", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer130.Add( self.m_textCtrl24, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox52 = wx.CheckBox( self.m_panel18, wx.ID_ANY, u"master include", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox52.SetValue(True)
		fgSizer130.Add( self.m_checkBox52, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl25 = wx.TextCtrl( self.m_panel18, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer130.Add( self.m_textCtrl25, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel18.SetSizer( fgSizer130 )
		self.m_panel18.Layout()
		fgSizer130.Fit( self.m_panel18 )
		self.m_choicebook1.AddPage( self.m_panel18, u"c++ project", True )
		self.m_panel19 = wx.Panel( self.m_choicebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_choicebook1.AddPage( self.m_panel19, u"python project", False )
		fgSizer65.Add( self.m_choicebook1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.m_panel5.SetSizer( fgSizer65 )
		self.m_panel5.Layout()
		fgSizer65.Fit( self.m_panel5 )
		self.m_auinotebook2.AddPage( self.m_panel5, u"General", True )
		self.m_panel6 = wx.Panel( self.m_auinotebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer69 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer69.AddGrowableCol( 0 )
		fgSizer69.AddGrowableRow( 1 )
		fgSizer69.SetFlexibleDirection( wx.BOTH )
		fgSizer69.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer68 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer68.AddGrowableCol( 1 )
		fgSizer68.SetFlexibleDirection( wx.BOTH )
		fgSizer68.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText33 = wx.StaticText( self.m_panel6, wx.ID_ANY, u"Author:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText33.Wrap( -1 )
		fgSizer68.Add( self.m_staticText33, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl251 = wx.TextCtrl( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer68.Add( self.m_textCtrl251, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText35 = wx.StaticText( self.m_panel6, wx.ID_ANY, u"Date:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )
		fgSizer68.Add( self.m_staticText35, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_datePicker1 = wx.DatePickerCtrl( self.m_panel6, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT|wx.DP_SHOWCENTURY )
		fgSizer68.Add( self.m_datePicker1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox53 = wx.CheckBox( self.m_panel6, wx.ID_ANY, u"Add license:", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer68.Add( self.m_checkBox53, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_choice16Choices = [ u"wxWidgets license", u"GNU GPL", u"GNU LGPL", u"FreeBSD", u"Creative Commons" ]
		self.m_choice16 = wx.Choice( self.m_panel6, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice16Choices, 0 )
		self.m_choice16.SetSelection( 0 )
		fgSizer68.Add( self.m_choice16, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer69.Add( fgSizer68, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer20 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel6, wx.ID_ANY, u"description" ), wx.VERTICAL )
		
		self.m_richText13 = wx.richtext.RichTextCtrl( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		sbSizer20.Add( self.m_richText13, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer69.Add( sbSizer20, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.m_panel6.SetSizer( fgSizer69 )
		self.m_panel6.Layout()
		fgSizer69.Fit( self.m_panel6 )
		self.m_auinotebook2.AddPage( self.m_panel6, u"Autoring", False )
		self.m_panel7 = wx.Panel( self.m_auinotebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer72 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer72.AddGrowableCol( 0 )
		fgSizer72.AddGrowableRow( 0 )
		fgSizer72.SetFlexibleDirection( wx.BOTH )
		fgSizer72.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer73 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer73.AddGrowableCol( 1 )
		fgSizer73.SetFlexibleDirection( wx.BOTH )
		fgSizer73.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText3111 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Project type:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3111.Wrap( -1 )
		fgSizer73.Add( self.m_staticText3111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice151Choices = [ u"unspecified", u"static library", u"dynamic library", u"executable", u"only code" ]
		self.m_choice151 = wx.Choice( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice151Choices, 0 )
		self.m_choice151.SetSelection( 3 )
		fgSizer73.Add( self.m_choice151, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText321 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Versión:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText321.Wrap( -1 )
		fgSizer73.Add( self.m_staticText321, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		fgSizer661 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer661.SetFlexibleDirection( wx.BOTH )
		fgSizer661.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_spinCtrl11 = wx.SpinCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer661.Add( self.m_spinCtrl11, 0, wx.ALL, 5 )
		
		self.m_spinCtrl21 = wx.SpinCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer661.Add( self.m_spinCtrl21, 0, wx.ALL, 5 )
		
		self.m_spinCtrl31 = wx.SpinCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer661.Add( self.m_spinCtrl31, 0, wx.ALL, 5 )
		
		
		fgSizer73.Add( fgSizer661, 1, wx.EXPAND, 5 )
		
		self.m_staticText43 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Build:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText43.Wrap( -1 )
		fgSizer73.Add( self.m_staticText43, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_checkBox54 = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"create makefile", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer73.Add( self.m_checkBox54, 0, wx.ALL, 5 )
		
		
		fgSizer72.Add( fgSizer73, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.m_panel7.SetSizer( fgSizer72 )
		self.m_panel7.Layout()
		fgSizer72.Fit( self.m_panel7 )
		self.m_auinotebook2.AddPage( self.m_panel7, u"Generation", False )
		
		fgSizer4.Add( self.m_auinotebook2, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer161 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer161.AddGrowableCol( 1 )
		fgSizer161.SetFlexibleDirection( wx.BOTH )
		fgSizer161.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer161.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer1 = wx.StdDialogButtonSizer()
		self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
		self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
		m_sdbSizer1.Realize();
		
		fgSizer161.Add( m_sdbSizer1, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		
		fgSizer4.Add( fgSizer161, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_textCtrl1.Bind( wx.EVT_TEXT, self.OnChangeProjectName )
		self.m_bpButton3.Bind( wx.EVT_BUTTON, self.OnChooseDir )
		self.m_choicebook1.Bind( wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging )
		self.m_checkBox52.Bind( wx.EVT_CHECKBOX, self.OnToggleMasterInclude )
		self.m_sdbSizer1OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnChangeProjectName( self, event ):
		event.Skip()
	
	def OnChooseDir( self, event ):
		event.Skip()
	
	def OnPageChanging( self, event ):
		event.Skip()
	
	def OnToggleMasterInclude( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class Preferences
###########################################################################

class Preferences ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Preferences", pos = wx.DefaultPosition, size = wx.Size( 477,287 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer77 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer77.AddGrowableCol( 0 )
		fgSizer77.AddGrowableRow( 0 )
		fgSizer77.SetFlexibleDirection( wx.BOTH )
		fgSizer77.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_auinotebook3 = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_BOTTOM )
		
		fgSizer77.Add( self.m_auinotebook3, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer164 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer164.AddGrowableCol( 1 )
		fgSizer164.SetFlexibleDirection( wx.BOTH )
		fgSizer164.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer164.Add( self.m_info, 0, wx.ALIGN_RIGHT, 5 )
		
		m_sdbSizer3 = wx.StdDialogButtonSizer()
		self.m_sdbSizer3OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer3.AddButton( self.m_sdbSizer3OK )
		self.m_sdbSizer3Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer3.AddButton( self.m_sdbSizer3Cancel )
		m_sdbSizer3.Realize();
		
		fgSizer164.Add( m_sdbSizer3, 1, wx.EXPAND, 5 )
		
		
		fgSizer77.Add( fgSizer164, 1, wx.EXPAND|wx.BOTTOM, 5 )
		
		
		self.SetSizer( fgSizer77 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_INIT_DIALOG, self.OnInitDialog )
		self.m_sdbSizer3OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnInitDialog( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class FullScreen
###########################################################################

class FullScreen ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.MAXIMIZE|wx.STAY_ON_TOP|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS|wx.WS_EX_TRANSIENT )
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class MainWindow
###########################################################################

class MainWindow ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"beatle", pos = wx.DefaultPosition, size = wx.Size( 1124,740 ), style = wx.DEFAULT_FRAME_STYLE|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.m_mgr = wx.aui.AuiManager()
		self.m_mgr.SetManagedWindow( self )
		
		self.m_menubar1 = wx.MenuBar( wx.MB_DOCKABLE )
		self.menuFile = wx.Menu()
		self.newWorkspace = wx.MenuItem( self.menuFile, ID_NEW_WORKSPACE, u"New workspace", u"create a new workspace", wx.ITEM_NORMAL )
		self.newWorkspace.SetBitmap( wx.Bitmap( u"app/res/workspace.xpm", wx.BITMAP_TYPE_ANY ) )
		self.menuFile.AppendItem( self.newWorkspace )
		
		self.newProject = wx.MenuItem( self.menuFile, ID_NEW_PROJECT, u"New project"+ u"\t" + u"Ctrl+N", u"create a new project", wx.ITEM_NORMAL )
		self.newProject.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_NEW, wx.ART_MENU ) )
		self.menuFile.AppendItem( self.newProject )
		
		self.menuFile.AppendSeparator()
		
		self.openWorkspace = wx.MenuItem( self.menuFile, ID_OPEN_WORKSPACE, u"Open workspace...", u"open an existing workspace", wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.openWorkspace )
		
		self.openProject = wx.MenuItem( self.menuFile, ID_OPEN_PROJECT, u"Open project ..."+ u"\t" + u"Ctrl+O", u"open an existing project", wx.ITEM_NORMAL )
		self.openProject.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_MENU ) )
		self.menuFile.AppendItem( self.openProject )
		
		self.menuMRU = wx.Menu()
		self.menuFile.AppendSubMenu( self.menuMRU, u"Open recent" )
		
		self.menuFile.AppendSeparator()
		
		self.m_menuItem26 = wx.MenuItem( self.menuFile, ID_CLOSE_WORKSPACE, u"close workspace", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.m_menuItem26 )
		
		self.m_menuItem27 = wx.MenuItem( self.menuFile, ID_CLOSE_PROJECT, u"close project", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.m_menuItem27 )
		
		self.menuFile.AppendSeparator()
		
		self.importProject = wx.MenuItem( self.menuFile, ID_IMPORT_PROJECT, u"import ...", u"import external project in current workspace", wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.importProject )
		
		self.menuFile.AppendSeparator()
		
		self.saveWorkspace = wx.MenuItem( self.menuFile, ID_SAVE_WORKSPACE, u"Save workspace", u"save current workspace", wx.ITEM_NORMAL )
		self.saveWorkspace.SetBitmap( wx.Bitmap( u"app/res/save_all.xpm", wx.BITMAP_TYPE_ANY ) )
		self.menuFile.AppendItem( self.saveWorkspace )
		
		self.saveProject = wx.MenuItem( self.menuFile, ID_SAVE_PROJECT, u"Save project"+ u"\t" + u"Ctrl+S", u"save current project", wx.ITEM_NORMAL )
		self.saveProject.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE, wx.ART_MENU ) )
		self.menuFile.AppendItem( self.saveProject )
		
		self.menuFile.AppendSeparator()
		
		self.quit = wx.MenuItem( self.menuFile, ID_QUIT, u"Quit"+ u"\t" + u"Ctrl+F4", u"exit application", wx.ITEM_NORMAL )
		self.quit.SetBitmap( wx.ArtProvider.GetBitmap( u"gtk-quit", wx.ART_MENU ) )
		self.menuFile.AppendItem( self.quit )
		
		self.m_menubar1.Append( self.menuFile, u"&Main" )
		
		self.menuEdit = wx.Menu()
		self.undo = wx.MenuItem( self.menuEdit, ID_UNDO, u"Undo"+ u"\t" + u"Ctrl+Z", u"undoes the last operation", wx.ITEM_NORMAL )
		self.undo.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_UNDO, wx.ART_TOOLBAR ) )
		self.menuEdit.AppendItem( self.undo )
		
		self.redo = wx.MenuItem( self.menuEdit, ID_REDO, u"Redo"+ u"\t" + u"Ctrl+Y", u"redoes the last operation", wx.ITEM_NORMAL )
		self.redo.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_REDO, wx.ART_TOOLBAR ) )
		self.menuEdit.AppendItem( self.redo )
		
		self.menuEdit.AppendSeparator()
		
		self.copy = wx.MenuItem( self.menuEdit, ID_COPY, u"Copy"+ u"\t" + u"Ctrl+C", u"copy the selected element", wx.ITEM_NORMAL )
		self.copy.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_MENU ) )
		self.menuEdit.AppendItem( self.copy )
		
		self.cut = wx.MenuItem( self.menuEdit, ID_CUT, u"Cut"+ u"\t" + u"Ctrl+X", u"cut the selected element", wx.ITEM_NORMAL )
		self.cut.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_CUT, wx.ART_MENU ) )
		self.menuEdit.AppendItem( self.cut )
		
		self.paste = wx.MenuItem( self.menuEdit, ID_PASTE, u"Paste"+ u"\t" + u"Ctrl+V", u"paste from clipboard", wx.ITEM_NORMAL )
		self.paste.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_PASTE, wx.ART_MENU ) )
		self.menuEdit.AppendItem( self.paste )
		
		self.menuEdit.AppendSeparator()
		
		self.delete = wx.MenuItem( self.menuEdit, ID_DELETE, u"Delete"+ u"\t" + u"Del", u"delete the selected element", wx.ITEM_NORMAL )
		self.delete.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_MENU ) )
		self.menuEdit.AppendItem( self.delete )
		
		self.menuEdit.AppendSeparator()
		
		self.editOpen = wx.MenuItem( self.menuEdit, ID_EDIT_OPEN, u"Open ...", u"open the selected element", wx.ITEM_NORMAL )
		self.editOpen.SetBitmap( wx.ArtProvider.GetBitmap( u"gtk-edit", wx.ART_MENU ) )
		self.menuEdit.AppendItem( self.editOpen )
		
		self.editContext = wx.MenuItem( self.menuEdit, ID_EDIT_CONTEXT, u"Select contexts ..."+ u"\t" + u"Ctrl+Shift+C", u"edit the  context of selected element", wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.editContext )
		
		self.editUserSections = wx.MenuItem( self.menuEdit, ID_EDIT_USER_SECTIONS, u"Edit user sections ...", u"edit the user sections", wx.ITEM_NORMAL )
		self.menuEdit.AppendItem( self.editUserSections )
		
		self.editProperties = wx.MenuItem( self.menuEdit, ID_EDIT_PROPERTIES, u"Properties ..."+ u"\t" + u"Ctrl+Enter", u"edit the properties of selected element", wx.ITEM_NORMAL )
		self.editProperties.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_INFORMATION, wx.ART_MENU ) )
		self.menuEdit.AppendItem( self.editProperties )
		
		self.menuEdit.AppendSeparator()
		
		self.preferences = wx.MenuItem( self.menuEdit, ID_PREFERENCES, u"Preferences", u"edit the application preferences", wx.ITEM_NORMAL )
		self.preferences.SetBitmap( wx.ArtProvider.GetBitmap( u"gtk-preferences", wx.ART_TOOLBAR ) )
		self.menuEdit.AppendItem( self.preferences )
		
		self.m_menubar1.Append( self.menuEdit, u"&Edit" )
		
		self.menuSearch = wx.Menu()
		self.find = wx.MenuItem( self.menuSearch, wx.ID_ANY, u"&Find ...", u"find any occurrence ", wx.ITEM_NORMAL )
		self.menuSearch.AppendItem( self.find )
		
		self.findInFiles = wx.MenuItem( self.menuSearch, wx.ID_ANY, u"Find in files ...", u"find any ocurrence in files", wx.ITEM_NORMAL )
		self.menuSearch.AppendItem( self.findInFiles )
		
		self.next = wx.MenuItem( self.menuSearch, wx.ID_ANY, u"Next"+ u"\t" + u"F3", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuSearch.AppendItem( self.next )
		
		self.previous = wx.MenuItem( self.menuSearch, wx.ID_ANY, u"previous"+ u"\t" + u"Shift+F3", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuSearch.AppendItem( self.previous )
		
		self.m_menubar1.Append( self.menuSearch, u"&Search" )
		
		self.menuView = wx.Menu()
		self.menuView.AppendSeparator()
		
		self.m_menuItem72 = wx.MenuItem( self.menuView, wx.ID_ANY, u"Reset perspective", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuView.AppendItem( self.m_menuItem72 )
		
		self.m_view_showToolbars = wx.MenuItem( self.menuView, wx.ID_ANY, u"show toolbars", u"Show all the current view toolbars", wx.ITEM_NORMAL )
		self.menuView.AppendItem( self.m_view_showToolbars )
		
		self.m_menubar1.Append( self.menuView, u"&View" )
		
		self.menuSettings = wx.Menu()
		self.compilerSettings = wx.MenuItem( self.menuSettings, wx.ID_ANY, u"build &tools ...", u"configure build tools", wx.ITEM_NORMAL )
		self.menuSettings.AppendItem( self.compilerSettings )
		
		self.m_menubar1.Append( self.menuSettings, u"S&ettings" )
		
		self.menuTools = wx.Menu()
		self.m_menubar1.Append( self.menuTools, u"&Tools" )
		
		self.menuHelp = wx.Menu()
		self.cppHelpURL = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"cpp reference ...", u"check online c++ reference", wx.ITEM_NORMAL )
		self.menuHelp.AppendItem( self.cppHelpURL )
		
		self.python2HelpURL = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"python 2 reference ...", u"check python online reference", wx.ITEM_NORMAL )
		self.menuHelp.AppendItem( self.python2HelpURL )
		
		self.beatsOfCodeURL = wx.MenuItem( self.menuHelp, wx.ID_ANY, u"online tutorials ...", u"check online tutorials", wx.ITEM_NORMAL )
		self.menuHelp.AppendItem( self.beatsOfCodeURL )
		
		self.m_menubar1.Append( self.menuHelp, u"&Help" )
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_auiToolBarFile = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_GRIPPER|wx.aui.AUI_TB_HORZ_LAYOUT )
		self.m_new_workspace = self.m_auiToolBarFile.AddTool( ID_NEW_WORKSPACE, u"new workspace", wx.Bitmap( u"app/res/workspace.xpm", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"new project", wx.EmptyString, None )
		
		self.m_new = self.m_auiToolBarFile.AddTool( ID_NEW_PROJECT, u"new project", wx.ArtProvider.GetBitmap( wx.ART_NEW, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"new project", wx.EmptyString, None )
		
		self.m_open = self.m_auiToolBarFile.AddTool( ID_OPEN_PROJECT, u"open project", wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"open project", wx.EmptyString, None )
		
		self.m_save_project = self.m_auiToolBarFile.AddTool( ID_SAVE_PROJECT, u"save project", wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"save current", wx.EmptyString, None )
		
		self.m_save_workspace = self.m_auiToolBarFile.AddTool( ID_SAVE_WORKSPACE, u"tool", wx.Bitmap( u"app/res/save_all.xpm", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"save workspace", wx.EmptyString, None )
		
		self.m_auiToolBarFile.Realize()
		self.m_mgr.AddPane( self.m_auiToolBarFile, wx.aui.AuiPaneInfo().Name( u"file_toolbar" ).Top().Caption( u"file" ).PinButton( True ).Gripper().Dock().Resizable().FloatingSize( wx.Size( -1,-1 ) ).DockFixed( False ).Row( 0 ).Position( 0 ).Layer( 10 ).ToolbarPane() )
		
		self.m_auiToolBarEdit = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_GRIPPER|wx.aui.AUI_TB_HORZ_LAYOUT )
		self.m_undo = self.m_auiToolBarEdit.AddTool( ID_UNDO, u"tool", wx.ArtProvider.GetBitmap( wx.ART_UNDO, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"undo last operation", wx.EmptyString, None )
		
		self.m_redo = self.m_auiToolBarEdit.AddTool( ID_REDO, u"tool", wx.ArtProvider.GetBitmap( wx.ART_REDO, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"redo last operation", wx.EmptyString, None )
		
		self.m_auiToolBarEdit.AddSeparator()
		
		self.m_copy = self.m_auiToolBarEdit.AddTool( ID_COPY, u"copy", wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"copy selected", wx.EmptyString, None )
		
		self.m_cut = self.m_auiToolBarEdit.AddTool( ID_CUT, u"cut", wx.ArtProvider.GetBitmap( wx.ART_CUT, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"cut selected", wx.EmptyString, None )
		
		self.m_paste = self.m_auiToolBarEdit.AddTool( ID_PASTE, u"paste", wx.ArtProvider.GetBitmap( wx.ART_PASTE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"paste from clipboard", wx.EmptyString, None )
		
		self.m_auiToolBarEdit.AddSeparator()
		
		self.m_delete = self.m_auiToolBarEdit.AddTool( ID_DELETE, u"delete", wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"delete selected", wx.EmptyString, None )
		
		self.m_auiToolBarEdit.Realize()
		self.m_mgr.AddPane( self.m_auiToolBarEdit, wx.aui.AuiPaneInfo().Name( u"edit_toolbar" ).Top().Caption( u"edit" ).PinButton( True ).Gripper().Dock().Resizable().FloatingSize( wx.Size( -1,-1 ) ).DockFixed( False ).Row( 0 ).Position( 1 ).Layer( 10 ).ToolbarPane() )
		
		self.m_statusBar1 = self.CreateStatusBar( 2, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.viewBook = wxx.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), wx.aui.AUI_NB_BOTTOM|wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_EXTERNAL_MOVE|wx.aui.AUI_NB_TAB_MOVE|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TOP|wx.aui.AUI_NB_WINDOWLIST_BUTTON )
		self.viewBook.SetMinSize( wx.Size( 300,-1 ) )
		
		self.m_mgr.AddPane( self.viewBook, wx.aui.AuiPaneInfo() .Name( u"views" ).Left() .Caption( u"views" ).CloseButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.Size( 120,300 ) ).DockFixed( False ).Row( 1 ).Position( 0 ).Layer( 4 ) )
		
		
		self.docBook = wxx.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB|wx.aui.AUI_NB_SCROLL_BUTTONS|wx.aui.AUI_NB_TAB_EXTERNAL_MOVE|wx.aui.AUI_NB_TAB_MOVE|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_TOP|wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.FULL_REPAINT_ON_RESIZE )
		self.m_mgr.AddPane( self.docBook, wx.aui.AuiPaneInfo() .Name( u"editors" ).Center() .Caption( u"editors" ).CloseButton( False ).MaximizeButton( True ).PinButton( True ).Dock().Resizable().FloatingSize( wx.Size( 120,300 ) ).DockFixed( False ).Row( 0 ).Layer( 0 ) )
		
		
		self.m_aux_panes = wx.Listbook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_TOP )
		self.m_mgr.AddPane( self.m_aux_panes, wx.aui.AuiPaneInfo() .Name( u"auxiliar" ).Bottom() .Caption( u"auxiliar panes" ).CloseButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.Size( -1,-1 ) ).DockFixed( False ).Row( 1 ).MinSize( wx.Size( 200,150 ) ).Layer( 2 ) )
		
		self.m_panel37 = wx.Panel( self.m_aux_panes, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer159 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer159.AddGrowableCol( 0 )
		fgSizer159.AddGrowableRow( 0 )
		fgSizer159.SetFlexibleDirection( wx.BOTH )
		fgSizer159.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		from app.ui.ctrl import pythonTextEntry
		self.m_pythonEntry = pythonTextEntry(self.m_panel37)
		fgSizer159.Add( self.m_pythonEntry, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel37.SetSizer( fgSizer159 )
		self.m_panel37.Layout()
		fgSizer159.Fit( self.m_panel37 )
		self.m_aux_panes.AddPage( self.m_panel37, u"console", True )
		self.m_panel30 = wx.Panel( self.m_aux_panes, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer243 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer243.AddGrowableCol( 0 )
		fgSizer243.AddGrowableRow( 0 )
		fgSizer243.SetFlexibleDirection( wx.BOTH )
		fgSizer243.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_toolLog = wx.TextCtrl( self.m_panel30, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		fgSizer243.Add( self.m_toolLog, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel30.SetSizer( fgSizer243 )
		self.m_panel30.Layout()
		fgSizer243.Fit( self.m_panel30 )
		self.m_aux_panes.AddPage( self.m_panel30, u"log", False )
		self.m_aux_output_pane = wx.Panel( self.m_aux_panes, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer2431 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer2431.AddGrowableCol( 0 )
		fgSizer2431.AddGrowableRow( 0 )
		fgSizer2431.SetFlexibleDirection( wx.BOTH )
		fgSizer2431.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.auxOutput = wx.TextCtrl( self.m_aux_output_pane, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CHARWRAP|wx.TE_MULTILINE|wx.TE_READONLY )
		fgSizer2431.Add( self.auxOutput, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_aux_output_pane.SetSizer( fgSizer2431 )
		self.m_aux_output_pane.Layout()
		fgSizer2431.Fit( self.m_aux_output_pane )
		self.m_aux_panes.AddPage( self.m_aux_output_pane, u"output", False )
		self.m_searchPane = wx.Panel( self.m_aux_panes, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer53 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer53.AddGrowableCol( 0 )
		fgSizer53.AddGrowableRow( 0 )
		fgSizer53.SetFlexibleDirection( wx.BOTH )
		fgSizer53.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_searchList = wx.ListCtrl( self.m_searchPane, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
		fgSizer53.Add( self.m_searchList, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_searchPane.SetSizer( fgSizer53 )
		self.m_searchPane.Layout()
		fgSizer53.Fit( self.m_searchPane )
		self.m_aux_panes.AddPage( self.m_searchPane, u"search", False )
		
		
		self.m_mgr.Update()
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnSalir )
		self.Bind( wx.EVT_MENU, self.OnNewWorkspace, id = self.newWorkspace.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.newProject.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.newProject.GetId() )
		self.Bind( wx.EVT_MENU, self.OnOpenWorkspace, id = self.openWorkspace.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.openProject.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.openProject.GetId() )
		self.Bind( wx.EVT_MENU, self.OnCloseWorkspace, id = self.m_menuItem26.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateCloseWorkspace, id = self.m_menuItem26.GetId() )
		self.Bind( wx.EVT_MENU, self.OnCloseProject, id = self.m_menuItem27.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateCloseProject, id = self.m_menuItem27.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.importProject.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.importProject.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.saveWorkspace.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.saveWorkspace.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.saveProject.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.saveProject.GetId() )
		self.Bind( wx.EVT_MENU, self.OnSalir, id = self.quit.GetId() )
		self.Bind( wx.EVT_MENU, self.OnEditUndo, id = self.undo.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateEditUndo, id = self.undo.GetId() )
		self.Bind( wx.EVT_MENU, self.OnEditRedo, id = self.redo.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateEditRedo, id = self.redo.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.copy.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.copy.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.cut.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.cut.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.paste.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.paste.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.delete.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.delete.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.editOpen.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.editOpen.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.editContext.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.editContext.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.editUserSections.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.editUserSections.GetId() )
		self.Bind( wx.EVT_MENU, self.redirectedToFocus, id = self.editProperties.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.redirectedToFocus4Enabled, id = self.editProperties.GetId() )
		self.Bind( wx.EVT_MENU, self.OnEditPreferences, id = self.preferences.GetId() )
		self.Bind( wx.EVT_MENU, self.OnFindInFiles, id = self.findInFiles.GetId() )
		self.Bind( wx.EVT_MENU, self.OnResetPerpective, id = self.m_menuItem72.GetId() )
		self.Bind( wx.EVT_MENU, self.OnSettingsBuildTools, id = self.compilerSettings.GetId() )
		self.Bind( wx.EVT_MENU, self.OnHelpCppReference, id = self.cppHelpURL.GetId() )
		self.Bind( wx.EVT_MENU, self.OnHelpPython2Reference, id = self.python2HelpURL.GetId() )
		self.Bind( wx.EVT_MENU, self.OnHelpBeatsOfCode, id = self.beatsOfCodeURL.GetId() )
		self.viewBook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnViewPageChanged )
		self.viewBook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.OnViewPageChanging )
		self.viewBook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnViewPageClosed )
		self.docBook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged )
		self.docBook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.OnPageChanging )
		self.docBook.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnClosePane )
		self.m_searchList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnSelectSearchItem )
	
	def __del__( self ):
		self.m_mgr.UnInit()
		
	
	
	# Virtual event handlers, overide them in your derived class
	def OnSalir( self, event ):
		event.Skip()
	
	def OnNewWorkspace( self, event ):
		event.Skip()
	
	def redirectedToFocus( self, event ):
		event.Skip()
	
	def redirectedToFocus4Enabled( self, event ):
		event.Skip()
	
	def OnOpenWorkspace( self, event ):
		event.Skip()
	
	
	
	def OnCloseWorkspace( self, event ):
		event.Skip()
	
	def OnUpdateCloseWorkspace( self, event ):
		event.Skip()
	
	def OnCloseProject( self, event ):
		event.Skip()
	
	def OnUpdateCloseProject( self, event ):
		event.Skip()
	
	
	
	
	
	
	
	
	def OnEditUndo( self, event ):
		event.Skip()
	
	def OnUpdateEditUndo( self, event ):
		event.Skip()
	
	def OnEditRedo( self, event ):
		event.Skip()
	
	def OnUpdateEditRedo( self, event ):
		event.Skip()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	def OnEditPreferences( self, event ):
		event.Skip()
	
	def OnFindInFiles( self, event ):
		event.Skip()
	
	def OnResetPerpective( self, event ):
		event.Skip()
	
	def OnSettingsBuildTools( self, event ):
		event.Skip()
	
	def OnHelpCppReference( self, event ):
		event.Skip()
	
	def OnHelpPython2Reference( self, event ):
		event.Skip()
	
	def OnHelpBeatsOfCode( self, event ):
		event.Skip()
	
	def OnViewPageChanged( self, event ):
		event.Skip()
	
	def OnViewPageChanging( self, event ):
		event.Skip()
	
	def OnViewPageClosed( self, event ):
		event.Skip()
	
	def OnPageChanged( self, event ):
		event.Skip()
	
	def OnPageChanging( self, event ):
		event.Skip()
	
	def OnClosePane( self, event ):
		event.Skip()
	
	def OnSelectSearchItem( self, event ):
		event.Skip()
	

###########################################################################
## Class FindText
###########################################################################

class FindText ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Find ", pos = wx.DefaultPosition, size = wx.Size( 331,118 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer68 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer68.AddGrowableCol( 0 )
		fgSizer68.AddGrowableRow( 0 )
		fgSizer68.AddGrowableRow( 2 )
		fgSizer68.SetFlexibleDirection( wx.BOTH )
		fgSizer68.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer68.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		fgSizer70 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer70.AddGrowableCol( 1 )
		fgSizer70.AddGrowableRow( 0 )
		fgSizer70.SetFlexibleDirection( wx.BOTH )
		fgSizer70.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText34 = wx.StaticText( self, wx.ID_ANY, u"search:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText34.Wrap( -1 )
		fgSizer70.Add( self.m_staticText34, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_search_string = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		fgSizer70.Add( self.m_search_string, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer68.Add( fgSizer70, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer68.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		fgSizer159 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer159.AddGrowableCol( 1 )
		fgSizer159.SetFlexibleDirection( wx.BOTH )
		fgSizer159.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer159.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer12 = wx.StdDialogButtonSizer()
		self.m_sdbSizer12OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer12.AddButton( self.m_sdbSizer12OK )
		self.m_sdbSizer12Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer12.AddButton( self.m_sdbSizer12Cancel )
		m_sdbSizer12.Realize();
		
		fgSizer159.Add( m_sdbSizer12, 1, wx.EXPAND, 5 )
		
		
		fgSizer68.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer68 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_search_string.Bind( wx.EVT_TEXT_ENTER, self.OnOK )
		self.m_sdbSizer12Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer12OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	

###########################################################################
## Class FindInFiles
###########################################################################

class FindInFiles ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Find in files", pos = wx.DefaultPosition, size = wx.Size( 436,256 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer68 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer68.AddGrowableCol( 0 )
		fgSizer68.AddGrowableRow( 1 )
		fgSizer68.SetFlexibleDirection( wx.BOTH )
		fgSizer68.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer70 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer70.AddGrowableCol( 1 )
		fgSizer70.AddGrowableRow( 0 )
		fgSizer70.SetFlexibleDirection( wx.BOTH )
		fgSizer70.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText34 = wx.StaticText( self, wx.ID_ANY, u"search:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText34.Wrap( -1 )
		fgSizer70.Add( self.m_staticText34, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_search_string = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		fgSizer70.Add( self.m_search_string, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer68.Add( fgSizer70, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		fgSizer61 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer61.AddGrowableCol( 0 )
		fgSizer61.AddGrowableCol( 1 )
		fgSizer61.AddGrowableRow( 0 )
		fgSizer61.SetFlexibleDirection( wx.BOTH )
		fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"options" ), wx.VERTICAL )
		
		self.m_checkBox4 = wx.CheckBox( self, wx.ID_ANY, u"&match case", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer6.Add( self.m_checkBox4, 0, wx.ALL, 5 )
		
		self.m_checkBox5 = wx.CheckBox( self, wx.ID_ANY, u"regular expression", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer6.Add( self.m_checkBox5, 0, wx.ALL, 5 )
		
		
		fgSizer61.Add( sbSizer6, 1, wx.EXPAND, 5 )
		
		sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"scope" ), wx.VERTICAL )
		
		self.m_radioBtn1 = wx.RadioButton( self, wx.ID_ANY, u"open files", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.m_radioBtn1, 0, wx.ALL, 5 )
		
		self.m_radioBtn2 = wx.RadioButton( self, wx.ID_ANY, u"project files", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.m_radioBtn2, 0, wx.ALL, 5 )
		
		self.m_radioBtn3 = wx.RadioButton( self, wx.ID_ANY, u"workspace files", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.m_radioBtn3, 0, wx.ALL, 5 )
		
		
		fgSizer61.Add( sbSizer7, 1, wx.EXPAND, 5 )
		
		
		fgSizer68.Add( fgSizer61, 1, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer159 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer159.AddGrowableCol( 1 )
		fgSizer159.SetFlexibleDirection( wx.BOTH )
		fgSizer159.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer159.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer12 = wx.StdDialogButtonSizer()
		self.m_sdbSizer12OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer12.AddButton( self.m_sdbSizer12OK )
		self.m_sdbSizer12Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer12.AddButton( self.m_sdbSizer12Cancel )
		m_sdbSizer12.Realize();
		
		fgSizer159.Add( m_sdbSizer12, 1, wx.EXPAND, 5 )
		
		
		fgSizer68.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer68 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_search_string.Bind( wx.EVT_TEXT_ENTER, self.OnOK )
		self.m_sdbSizer12Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer12OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	

###########################################################################
## Class NewWorkspace
###########################################################################

class NewWorkspace ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New workspace", pos = wx.DefaultPosition, size = wx.Size( 429,401 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer172 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer172.AddGrowableCol( 0 )
		fgSizer172.AddGrowableRow( 1 )
		fgSizer172.SetFlexibleDirection( wx.BOTH )
		fgSizer172.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer5 = wx.FlexGridSizer( 5, 2, 0, 0 )
		fgSizer5.AddGrowableCol( 1 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		fgSizer5.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer5.Add( self.m_textCtrl1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Base directory:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		fgSizer5.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		fgSizer29 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer29.AddGrowableCol( 0 )
		fgSizer29.SetFlexibleDirection( wx.BOTH )
		fgSizer29.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_textCtrl9 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer29.Add( self.m_textCtrl9, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_bpButton3 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FOLDER_OPEN, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer29.Add( self.m_bpButton3, 0, wx.ALL, 5 )
		
		
		fgSizer5.Add( fgSizer29, 1, wx.EXPAND, 5 )
		
		
		fgSizer172.Add( fgSizer5, 1, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer172.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer22 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer22.AddGrowableCol( 0 )
		fgSizer22.SetFlexibleDirection( wx.BOTH )
		fgSizer22.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer22.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button5 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer22.Add( self.m_button5, 0, wx.ALL, 5 )
		
		self.m_button6 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button6.SetDefault()
		fgSizer22.Add( self.m_button6, 0, wx.ALL, 5 )
		
		
		fgSizer172.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer172 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_textCtrl1.Bind( wx.EVT_TEXT, self.OnChangeWorkspaceName )
		self.m_bpButton3.Bind( wx.EVT_BUTTON, self.OnChooseDir )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnChangeWorkspaceName( self, event ):
		event.Skip()
	
	def OnChooseDir( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class Wait
###########################################################################

class Wait ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Please wait while processing files", pos = wx.DefaultPosition, size = wx.Size( 553,186 ), style = wx.CAPTION|wx.RESIZE_BORDER|wx.STAY_ON_TOP )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_PROCESS_IDLE|wx.WS_EX_PROCESS_UI_UPDATES )
		
		fgSizer224 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer224.AddGrowableCol( 0 )
		fgSizer224.AddGrowableRow( 0 )
		fgSizer224.AddGrowableRow( 2 )
		fgSizer224.SetFlexibleDirection( wx.BOTH )
		fgSizer224.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer224.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		fgSizer225 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer225.AddGrowableCol( 1 )
		fgSizer225.SetFlexibleDirection( wx.BOTH )
		fgSizer225.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer225.AddSpacer( ( 10, 0), 1, wx.EXPAND, 5 )
		
		self.m_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.NO_BORDER )
		self.m_text.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
		
		fgSizer225.Add( self.m_text, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		fgSizer225.AddSpacer( ( 10, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer224.Add( fgSizer225, 1, wx.EXPAND, 5 )
		
		
		fgSizer224.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer224 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class Working
###########################################################################

class Working ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 236,171 ), style = wx.FRAME_FLOAT_ON_PARENT|wx.FRAME_NO_TASKBAR )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer242 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer242.AddGrowableCol( 0 )
		fgSizer242.AddGrowableRow( 0 )
		fgSizer242.AddGrowableRow( 2 )
		fgSizer242.SetFlexibleDirection( wx.BOTH )
		fgSizer242.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_animCtrl = wx.animate.AnimationCtrl( self, wx.ID_ANY, wx.animate.NullAnimation, wx.DefaultPosition, wx.DefaultSize, wx.animate.AC_DEFAULT_STYLE|wx.NO_BORDER )
		
		self.m_animCtrl.SetInactiveBitmap( wx.NullBitmap )
		fgSizer242.Add( self.m_animCtrl, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticText112 = wx.StaticText( self, wx.ID_ANY, u"Please wait ...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText112.Wrap( -1 )
		fgSizer242.Add( self.m_staticText112, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer242.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer242 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class ImportProject
###########################################################################

class ImportProject ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Import project", pos = wx.DefaultPosition, size = wx.Size( 429,339 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer178 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer178.AddGrowableCol( 0 )
		fgSizer178.AddGrowableRow( 1 )
		fgSizer178.SetFlexibleDirection( wx.BOTH )
		fgSizer178.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer233 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer233.AddGrowableCol( 1 )
		fgSizer233.SetFlexibleDirection( wx.BOTH )
		fgSizer233.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText110 = wx.StaticText( self, wx.ID_ANY, u"base directory", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText110.Wrap( -1 )
		fgSizer233.Add( self.m_staticText110, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_dirPicker2 = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE|wx.DIRP_DIR_MUST_EXIST|wx.DIRP_USE_TEXTCTRL )
		fgSizer233.Add( self.m_dirPicker2, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer178.Add( fgSizer233, 1, wx.EXPAND, 5 )
		
		self.m_choicebook4 = wx.Choicebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel29 = wx.Panel( self.m_choicebook4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer183 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer183.AddGrowableCol( 0 )
		fgSizer183.AddGrowableRow( 0 )
		fgSizer183.SetFlexibleDirection( wx.BOTH )
		fgSizer183.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_checkList6Choices = []
		self.m_checkList6 = wx.CheckListBox( self.m_panel29, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList6Choices, 0 )
		fgSizer183.Add( self.m_checkList6, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel29.SetSizer( fgSizer183 )
		self.m_panel29.Layout()
		fgSizer183.Fit( self.m_panel29 )
		self.m_choicebook4.AddPage( self.m_panel29, u"python", False )
		self.m_panel28 = wx.Panel( self.m_choicebook4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer182 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer182.SetFlexibleDirection( wx.BOTH )
		fgSizer182.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		self.m_panel28.SetSizer( fgSizer182 )
		self.m_panel28.Layout()
		fgSizer182.Fit( self.m_panel28 )
		self.m_choicebook4.AddPage( self.m_panel28, u"c++", False )
		fgSizer178.Add( self.m_choicebook4, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer159 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer159.AddGrowableCol( 1 )
		fgSizer159.SetFlexibleDirection( wx.BOTH )
		fgSizer159.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer159.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer12 = wx.StdDialogButtonSizer()
		self.m_sdbSizer12OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer12.AddButton( self.m_sdbSizer12OK )
		self.m_sdbSizer12Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer12.AddButton( self.m_sdbSizer12Cancel )
		m_sdbSizer12.Realize();
		
		fgSizer159.Add( m_sdbSizer12, 1, wx.EXPAND, 5 )
		
		
		fgSizer178.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer178 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer12Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer12OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

