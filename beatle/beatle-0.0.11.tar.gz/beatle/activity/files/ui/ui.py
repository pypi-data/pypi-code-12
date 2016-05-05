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
import wx.propgrid as pg

###########################################################################
## Class FilePane
###########################################################################

class FilePane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer28 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer28.AddGrowableCol( 0 )
		fgSizer28.AddGrowableRow( 0 )
		fgSizer28.SetFlexibleDirection( wx.BOTH )
		fgSizer28.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		import app.ui.ctrl.Editor as Editor
		self.m_editor = Editor(self)
		fgSizer28.Add( self.m_editor, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer28 )
		self.Layout()
		
		# Connect Events
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnKillFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnKillFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class TextPane
###########################################################################

class TextPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer28 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer28.AddGrowableCol( 0 )
		fgSizer28.AddGrowableRow( 0 )
		fgSizer28.SetFlexibleDirection( wx.BOTH )
		fgSizer28.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		import app.ui.ctrl.Editor as Editor
		self.m_editor = Editor(self)
		fgSizer28.Add( self.m_editor, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer28 )
		self.Layout()
		
		# Connect Events
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnKillFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnKillFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class FilePythonPane
###########################################################################

class FilePythonPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer28 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer28.AddGrowableCol( 0 )
		fgSizer28.AddGrowableRow( 0 )
		fgSizer28.SetFlexibleDirection( wx.BOTH )
		fgSizer28.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		import app.ui.ctrl.Editor as Editor
		self.m_editor = Editor(self, language='python')
		fgSizer28.Add( self.m_editor, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer28 )
		self.Layout()
		
		# Connect Events
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnKillFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnKillFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class FilesView
###########################################################################

class FilesView ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		fgSizer3 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer3.AddGrowableCol( 0 )
		fgSizer3.AddGrowableRow( 0 )
		fgSizer3.SetFlexibleDirection( wx.BOTH )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wxx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.NO_BORDER )
		fgSizer3.Add( self.m_tree, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer3 )
		self.Layout()
		
		# Connect Events
		self.Bind( wx.EVT_KILL_FOCUS, self.OnKillFocus )
		self.Bind( wx.EVT_SET_FOCUS, self.OnSetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnKillFocus( self, event ):
		event.Skip()
	
	def OnSetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class NewFile
###########################################################################

class NewFile ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"NewFile", pos = wx.DefaultPosition, size = wx.Size( 421,356 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer125 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer125.AddGrowableCol( 0 )
		fgSizer125.AddGrowableRow( 1 )
		fgSizer125.SetFlexibleDirection( wx.BOTH )
		fgSizer125.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer126 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer126.AddGrowableCol( 1 )
		fgSizer126.SetFlexibleDirection( wx.BOTH )
		fgSizer126.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		self.m_staticText85 = wx.StaticText( self, wx.ID_ANY, u"File name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText85.Wrap( -1 )
		fgSizer126.Add( self.m_staticText85, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_file = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer126.Add( self.m_file, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer125.Add( fgSizer126, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.ALL, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer125.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
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
		
		# Connect Events
		self.m_sdbSizer10Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer10OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewDir
###########################################################################

class NewDir ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New directory", pos = wx.DefaultPosition, size = wx.Size( 421,356 ), style = wx.DEFAULT_DIALOG_STYLE )
		
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
		
		self.m_dirPicker = wx.DirPickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_USE_TEXTCTRL )
		fgSizer7.Add( self.m_dirPicker, 0, wx.ALL|wx.EXPAND, 5 )
		
		
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
		self.m_sdbSizer2Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer2OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class Threads
###########################################################################

class Threads ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 468,421 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer10 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer10.AddGrowableCol( 0 )
		fgSizer10.AddGrowableRow( 0 )
		fgSizer10.SetFlexibleDirection( wx.BOTH )
		fgSizer10.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer11 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer11.AddGrowableCol( 0 )
		fgSizer11.AddGrowableRow( 0 )
		fgSizer11.SetFlexibleDirection( wx.BOTH )
		fgSizer11.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_listThreadsChoices = []
		self.m_listThreads = wx.ListBox( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listThreadsChoices, 0 )
		fgSizer11.Add( self.m_listThreads, 1, wx.EXPAND, 5 )
		
		
		self.m_panel1.SetSizer( fgSizer11 )
		self.m_panel1.Layout()
		fgSizer11.Fit( self.m_panel1 )
		fgSizer10.Add( self.m_panel1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer10 )
		self.Layout()
		
		# Connect Events
		self.m_listThreads.Bind( wx.EVT_LISTBOX, self.OnSelectThread )
		self.m_listThreads.Bind( wx.EVT_LISTBOX_DCLICK, self.OnActivateThread )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnSelectThread( self, event ):
		event.Skip()
	
	def OnActivateThread( self, event ):
		event.Skip()
	

###########################################################################
## Class StackFrame
###########################################################################

class StackFrame ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer12 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 0 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_stackFrameChoices = []
		self.m_stackFrame = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_stackFrameChoices, wx.LB_SINGLE )
		fgSizer12.Add( self.m_stackFrame, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		# Connect Events
		self.m_stackFrame.Bind( wx.EVT_LISTBOX, self.OnSelectStackFrame )
		self.m_stackFrame.Bind( wx.EVT_LISTBOX_DCLICK, self.OnActivateStackFrame )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnSelectStackFrame( self, event ):
		event.Skip()
	
	def OnActivateStackFrame( self, event ):
		event.Skip()
	

###########################################################################
## Class Locals
###########################################################################

class Locals ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer13 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.AddGrowableRow( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_locals = pg.PropertyGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE)
		fgSizer13.Add( self.m_locals, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer13 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class Expressions
###########################################################################

class Expressions ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer13 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.AddGrowableRow( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_propertyGrid1 = pg.PropertyGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE)
		fgSizer13.Add( self.m_propertyGrid1, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer13 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class Breakpoints
###########################################################################

class Breakpoints ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 459,479 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer13 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.AddGrowableRow( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_listBreakpoints = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_REPORT|wx.LC_SINGLE_SEL )
		fgSizer13.Add( self.m_listBreakpoints, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer13 )
		self.Layout()
		
		# Connect Events
		self.m_listBreakpoints.Bind( wx.EVT_LIST_COL_RIGHT_CLICK, self.OnBreakpoinMenu )
		self.m_listBreakpoints.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.OnEditBreakpoint )
		self.m_listBreakpoints.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnSelectBreakpoint )
		self.m_listBreakpoints.Bind( wx.EVT_SIZE, self.OnSize )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnBreakpoinMenu( self, event ):
		event.Skip()
	
	def OnEditBreakpoint( self, event ):
		event.Skip()
	
	def OnSelectBreakpoint( self, event ):
		event.Skip()
	
	def OnSize( self, event ):
		event.Skip()
	

###########################################################################
## Class DebugCommand
###########################################################################

class DebugCommand ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer18 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer18.AddGrowableCol( 0 )
		fgSizer18.AddGrowableRow( 0 )
		fgSizer18.SetFlexibleDirection( wx.BOTH )
		fgSizer18.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_debugOutput = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		fgSizer18.Add( self.m_debugOutput, 0, wx.EXPAND, 5 )
		
		fgSizer19 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer19.AddGrowableCol( 1 )
		fgSizer19.AddGrowableRow( 0 )
		fgSizer19.SetFlexibleDirection( wx.BOTH )
		fgSizer19.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"command:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		fgSizer19.Add( self.m_staticText3, 0, wx.ALL, 5 )
		
		self.m_debugCommand = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		fgSizer19.Add( self.m_debugCommand, 0, wx.EXPAND, 5 )
		
		
		fgSizer18.Add( fgSizer19, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer18 )
		self.Layout()
		
		# Connect Events
		self.m_debugCommand.Bind( wx.EVT_TEXT_ENTER, self.OnEnter )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnEnter( self, event ):
		event.Skip()
	

