# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wxx
import wx.richtext

###########################################################################
## Class GitView
###########################################################################

class GitView ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 451,470 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer2 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer2.AddGrowableCol( 0 )
		fgSizer2.AddGrowableRow( 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wxx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE )
		fgSizer2.Add( self.m_tree, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer2 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class NewGitRepo
###########################################################################

class NewGitRepo ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Create new Git repository", pos = wx.DefaultPosition, size = wx.Size( 415,286 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer229 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer229.AddGrowableCol( 0 )
		fgSizer229.AddGrowableRow( 0 )
		fgSizer229.SetFlexibleDirection( wx.BOTH )
		fgSizer229.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_choicebook7 = wx.Choicebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel30 = wx.Panel( self.m_choicebook7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer233 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer233.AddGrowableCol( 0 )
		fgSizer233.AddGrowableRow( 1 )
		fgSizer233.SetFlexibleDirection( wx.BOTH )
		fgSizer233.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_dirPicker2 = wx.DirPickerCtrl( self.m_panel30, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DIR_MUST_EXIST|wx.DIRP_USE_TEXTCTRL )
		fgSizer233.Add( self.m_dirPicker2, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_textCtrl77 = wx.TextCtrl( self.m_panel30, wx.ID_ANY, u"Select the directory in what you want to create a new local git repository. It may be a directory already containing files. This case, you must add these files to the git control after the creation.", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER )
		self.m_textCtrl77.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
		
		fgSizer233.Add( self.m_textCtrl77, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel30.SetSizer( fgSizer233 )
		self.m_panel30.Layout()
		fgSizer233.Fit( self.m_panel30 )
		self.m_choicebook7.AddPage( self.m_panel30, u"local repository", False )
		fgSizer229.Add( self.m_choicebook7, 1, wx.EXPAND |wx.ALL, 5 )
		
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
		
		
		fgSizer229.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer229 )
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
	

###########################################################################
## Class OpenGitRepo
###########################################################################

class OpenGitRepo ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Open Git repository", pos = wx.DefaultPosition, size = wx.Size( 351,163 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer229 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer229.AddGrowableCol( 0 )
		fgSizer229.AddGrowableRow( 1 )
		fgSizer229.SetFlexibleDirection( wx.BOTH )
		fgSizer229.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_dirPicker2 = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DIR_MUST_EXIST|wx.DIRP_USE_TEXTCTRL )
		fgSizer229.Add( self.m_dirPicker2, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_textCtrl77 = wx.TextCtrl( self, wx.ID_ANY, u"Select the directory that holds a git repository", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER )
		self.m_textCtrl77.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )
		
		fgSizer229.Add( self.m_textCtrl77, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
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
		
		
		fgSizer229.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer229 )
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
	

###########################################################################
## Class CommitGit
###########################################################################

class CommitGit ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Commit to Git", pos = wx.DefaultPosition, size = wx.Size( 350,247 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer229 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer229.AddGrowableCol( 0 )
		fgSizer229.AddGrowableRow( 0 )
		fgSizer229.SetFlexibleDirection( wx.BOTH )
		fgSizer229.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer53 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"commit message" ), wx.VERTICAL )
		
		self.m_richText39 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		sbSizer53.Add( self.m_richText39, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer229.Add( sbSizer53, 1, wx.EXPAND|wx.ALL, 5 )
		
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
		
		
		fgSizer229.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer229 )
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
	

###########################################################################
## Class NewGitRemote
###########################################################################

class NewGitRemote ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New remote ...", pos = wx.DefaultPosition, size = wx.Size( 475,193 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer229 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer229.AddGrowableCol( 0 )
		fgSizer229.AddGrowableRow( 0 )
		fgSizer229.SetFlexibleDirection( wx.BOTH )
		fgSizer229.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer65 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer65.AddGrowableCol( 1 )
		fgSizer65.SetFlexibleDirection( wx.BOTH )
		fgSizer65.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer65.Add( self.m_staticText26, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer65.Add( self.m_name, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, u"url", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )
		fgSizer65.Add( self.m_staticText27, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.m_url = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer65.Add( self.m_url, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, u"password", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )
		fgSizer65.Add( self.m_staticText28, 0, wx.ALL, 5 )
		
		self.m_password = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PASSWORD )
		fgSizer65.Add( self.m_password, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer229.Add( fgSizer65, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer229.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer229 )
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
	

###########################################################################
## Class Progress
###########################################################################

class Progress ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Git progress", pos = wx.DefaultPosition, size = wx.Size( 445,278 ), style = wx.CAPTION|wx.STAY_ON_TOP )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 0 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		fgSizer12.Add( self.m_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer159 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer159.AddGrowableCol( 1 )
		fgSizer159.SetFlexibleDirection( wx.BOTH )
		fgSizer159.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer159.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer12 = wx.StdDialogButtonSizer()
		self.m_sdbSizer12OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer12.AddButton( self.m_sdbSizer12OK )
		m_sdbSizer12.Realize();
		
		fgSizer159.Add( m_sdbSizer12, 1, wx.EXPAND, 5 )
		
		
		fgSizer12.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer12OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

