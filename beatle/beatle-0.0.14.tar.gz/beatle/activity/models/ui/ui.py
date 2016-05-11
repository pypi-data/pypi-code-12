# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version May 10 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui
import wxx
import wx.richtext
import wx.lib.agw.customtreectrl as CT

ID_SAVE_CODE = 1000
ID_UNDO_CODE = 1001
ID_REDO_CODE = 1002
ID_COPY_CODE = 1003
ID_CUT_CODE = 1004
ID_PASTE_CODE = 1005
ID_DELETE_CODE = 1006
ID_TOGGLE_FULLSCREEN = 1007

###########################################################################
## Class ConstructorPane
###########################################################################

class ConstructorPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.NO_BORDER|wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer28 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer28.AddGrowableCol( 0 )
		fgSizer28.AddGrowableRow( 1 )
		fgSizer28.SetFlexibleDirection( wx.BOTH )
		fgSizer28.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer130 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer130.AddGrowableCol( 0 )
		fgSizer130.AddGrowableRow( 0 )
		fgSizer130.SetFlexibleDirection( wx.BOTH )
		fgSizer130.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_auiToolBar5 = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT ) 
		self.m_save = self.m_auiToolBar5.AddTool( ID_SAVE_CODE, u"save project", wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Save", wx.EmptyString, None ) 
		
		self.m_auiToolBar5.AddSeparator()
		
		self.m_undo = self.m_auiToolBar5.AddTool( ID_UNDO_CODE, u"tool", wx.ArtProvider.GetBitmap( wx.ART_UNDO, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.m_redo = self.m_auiToolBar5.AddTool( ID_REDO_CODE, u"tool", wx.ArtProvider.GetBitmap( wx.ART_REDO, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.m_auiToolBar5.AddSeparator()
		
		self.m_copy = self.m_auiToolBar5.AddTool( ID_COPY_CODE, u"copy", wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Copy", wx.EmptyString, None ) 
		
		self.m_cut = self.m_auiToolBar5.AddTool( ID_CUT_CODE, u"cut", wx.ArtProvider.GetBitmap( wx.ART_CUT, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Cut", wx.EmptyString, None ) 
		
		self.m_paste = self.m_auiToolBar5.AddTool( ID_PASTE_CODE, u"paste", wx.ArtProvider.GetBitmap( wx.ART_PASTE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Paste", wx.EmptyString, None ) 
		
		self.m_auiToolBar5.AddSeparator()
		
		self.m_delete = self.m_auiToolBar5.AddTool( ID_DELETE_CODE, u"delete", wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Delete", wx.EmptyString, None ) 
		
		self.m_auiToolBar5.AddSeparator()
		
		self.m_fullScreen = self.m_auiToolBar5.AddTool( ID_TOGGLE_FULLSCREEN, u"tool", wx.ArtProvider.GetBitmap( u"gtk-fullscreen", wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_CHECK, u"toggle fullscreen", wx.EmptyString, None ) 
		
		self.m_auiToolBar5.AddSeparator()
		
		self.m_navigator = self.m_auiToolBar5.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"app/res/method.xpm", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"insert call", wx.EmptyString, None ) 
		
		self.m_auiToolBar5.Realize() 
		
		fgSizer130.Add( self.m_auiToolBar5, 0, wx.ALL, 5 )
		
		
		fgSizer28.Add( fgSizer130, 1, wx.EXPAND, 0 )
		
		self.m_splitter2 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter2.Bind( wx.EVT_IDLE, self.m_splitter2OnIdle )
		self.m_splitter2.SetMinimumPaneSize( 60 )
		
		self.m_panel3 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		self.m_panel3.SetMinSize( wx.Size( -1,60 ) )
		
		fgSizer60 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer60.AddGrowableCol( 0 )
		fgSizer60.AddGrowableRow( 0 )
		fgSizer60.SetFlexibleDirection( wx.BOTH )
		fgSizer60.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		import app.ui.ctrl.Editor as Editor
		self.m_init  = Editor(self.m_panel3)
		self.m_init.SetMinSize( wx.Size( -1,60 ) )
		
		fgSizer60.Add( self.m_init, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.m_panel3.SetSizer( fgSizer60 )
		self.m_panel3.Layout()
		fgSizer60.Fit( self.m_panel3 )
		self.m_panel4 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		fgSizer601 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer601.AddGrowableCol( 0 )
		fgSizer601.AddGrowableRow( 0 )
		fgSizer601.SetFlexibleDirection( wx.BOTH )
		fgSizer601.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_editor = Editor(self.m_panel4) 
		fgSizer601.Add( self.m_editor, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.m_panel4.SetSizer( fgSizer601 )
		self.m_panel4.Layout()
		fgSizer601.Fit( self.m_panel4 )
		self.m_splitter2.SplitHorizontally( self.m_panel3, self.m_panel4, 83 )
		fgSizer28.Add( self.m_splitter2, 1, wx.EXPAND, 0 )
		
		
		self.SetSizer( fgSizer28 )
		self.Layout()
		
		# Connect Events
		self.Bind( wx.EVT_INIT_DIALOG, self.OnInitPane )
		self.Bind( wx.EVT_TOOL, self.OnSaveCode, id = self.m_save.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateSaveCode, id = self.m_save.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnUndoCode, id = self.m_undo.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateUndoCode, id = self.m_undo.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnRedoCode, id = self.m_redo.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateRedoCode, id = self.m_redo.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnCopyCode, id = self.m_copy.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateCopyCode, id = self.m_copy.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnCutCode, id = self.m_cut.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateCutCode, id = self.m_cut.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnPasteCode, id = self.m_paste.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdatePasteCode, id = self.m_paste.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnDeleteCode, id = self.m_delete.GetId() )
		self.Bind( wx.EVT_UPDATE_UI, self.OnUpdateDeleteCode, id = self.m_delete.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnFullScreen, id = self.m_fullScreen.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnNavigator, id = self.m_navigator.GetId() )
		self.m_init.Bind( wx.EVT_KILL_FOCUS, self.OnInitLeaveFocus )
		self.m_init.Bind( wx.EVT_SET_FOCUS, self.OnInitGetFocus )
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnEditorLeaveFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnEditorGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnInitPane( self, event ):
		event.Skip()
	
	def OnSaveCode( self, event ):
		event.Skip()
	
	def OnUpdateSaveCode( self, event ):
		event.Skip()
	
	def OnUndoCode( self, event ):
		event.Skip()
	
	def OnUpdateUndoCode( self, event ):
		event.Skip()
	
	def OnRedoCode( self, event ):
		event.Skip()
	
	def OnUpdateRedoCode( self, event ):
		event.Skip()
	
	def OnCopyCode( self, event ):
		event.Skip()
	
	def OnUpdateCopyCode( self, event ):
		event.Skip()
	
	def OnCutCode( self, event ):
		event.Skip()
	
	def OnUpdateCutCode( self, event ):
		event.Skip()
	
	def OnPasteCode( self, event ):
		event.Skip()
	
	def OnUpdatePasteCode( self, event ):
		event.Skip()
	
	def OnDeleteCode( self, event ):
		event.Skip()
	
	def OnUpdateDeleteCode( self, event ):
		event.Skip()
	
	def OnFullScreen( self, event ):
		event.Skip()
	
	def OnNavigator( self, event ):
		event.Skip()
	
	def OnInitLeaveFocus( self, event ):
		event.Skip()
	
	def OnInitGetFocus( self, event ):
		event.Skip()
	
	def OnEditorLeaveFocus( self, event ):
		event.Skip()
	
	def OnEditorGetFocus( self, event ):
		event.Skip()
	
	def m_splitter2OnIdle( self, event ):
		self.m_splitter2.SetSashPosition( 83 )
		self.m_splitter2.Unbind( wx.EVT_IDLE )
	

###########################################################################
## Class ClassDiagramPane
###########################################################################

class ClassDiagramPane ( wx.PyScrolledWindow ):
	
	def __init__( self, parent ):
		wx.PyScrolledWindow.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS|wx.WS_EX_PROCESS_UI_UPDATES )
		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
		
		
		# Connect Events
		self.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnMouseDown )
		self.Bind( wx.EVT_LEFT_UP, self.OnMouseUp )
		self.Bind( wx.EVT_MOTION, self.OnMouseMove )
		self.Bind( wx.EVT_PAINT, self.OnPaintClassDiagram )
		self.Bind( wx.EVT_RIGHT_DOWN, self.OnDiagramMenu )
		self.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLeaveFocus( self, event ):
		event.Skip()
	
	def OnMouseDown( self, event ):
		event.Skip()
	
	def OnMouseUp( self, event ):
		event.Skip()
	
	def OnMouseMove( self, event ):
		event.Skip()
	
	def OnPaintClassDiagram( self, event ):
		event.Skip()
	
	def OnDiagramMenu( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class MethodPane
###########################################################################

class MethodPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer28 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer28.AddGrowableCol( 0 )
		fgSizer28.AddGrowableRow( 1 )
		fgSizer28.SetFlexibleDirection( wx.BOTH )
		fgSizer28.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_toolbarSizer = wx.FlexGridSizer( 1, 1, 0, 0 )
		self.m_toolbarSizer.AddGrowableCol( 0 )
		self.m_toolbarSizer.AddGrowableRow( 0 )
		self.m_toolbarSizer.SetFlexibleDirection( wx.BOTH )
		self.m_toolbarSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer28.Add( self.m_toolbarSizer, 1, wx.EXPAND, 5 )
		
		import app.ui.ctrl.Editor as Editor
		self.m_editor = Editor(self)
		fgSizer28.Add( self.m_editor, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer28 )
		self.Layout()
		
		# Connect Events
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLeaveFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class PyMethodPane
###########################################################################

class PyMethodPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		self._mainSizer = wx.FlexGridSizer( 2, 1, 0, 0 )
		self._mainSizer.AddGrowableCol( 0 )
		self._mainSizer.AddGrowableRow( 1 )
		self._mainSizer.SetFlexibleDirection( wx.BOTH )
		self._mainSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_toolbarSizer = wx.FlexGridSizer( 1, 1, 0, 0 )
		self.m_toolbarSizer.AddGrowableCol( 0 )
		self.m_toolbarSizer.AddGrowableRow( 0 )
		self.m_toolbarSizer.SetFlexibleDirection( wx.BOTH )
		self.m_toolbarSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		self._mainSizer.Add( self.m_toolbarSizer, 1, wx.EXPAND, 5 )
		
		import app.ui.ctrl.Editor as Editor
		self.m_editor = Editor(self, language='python')
		self._mainSizer.Add( self.m_editor, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( self._mainSizer )
		self.Layout()
		
		# Connect Events
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLeaveFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class PyModulePane
###########################################################################

class PyModulePane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		self._mainSizer = wx.FlexGridSizer( 2, 1, 0, 0 )
		self._mainSizer.AddGrowableCol( 0 )
		self._mainSizer.AddGrowableRow( 1 )
		self._mainSizer.SetFlexibleDirection( wx.BOTH )
		self._mainSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_toolbarSizer = wx.FlexGridSizer( 1, 1, 0, 0 )
		self.m_toolbarSizer.AddGrowableCol( 0 )
		self.m_toolbarSizer.AddGrowableRow( 0 )
		self.m_toolbarSizer.SetFlexibleDirection( wx.BOTH )
		self.m_toolbarSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		self._mainSizer.Add( self.m_toolbarSizer, 1, wx.EXPAND, 5 )
		
		import app.ui.ctrl.Editor as Editor
		self.m_editor = Editor(self, language='python')
		self._mainSizer.Add( self.m_editor, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( self._mainSizer )
		self.Layout()
		
		# Connect Events
		self.m_editor.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_editor.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLeaveFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	

###########################################################################
## Class ModelsView
###########################################################################

class ModelsView ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.NO_BORDER|wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_PROCESS_UI_UPDATES )
		
		fgSizer2 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer2.AddGrowableCol( 0 )
		fgSizer2.AddGrowableRow( 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wxx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE|wx.NO_BORDER )
		fgSizer2.Add( self.m_tree, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer2 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class ContextItems
###########################################################################

class ContextItems ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit context items", pos = wx.DefaultPosition, size = wx.Size( 662,664 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer97 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer97.AddGrowableCol( 0 )
		fgSizer97.AddGrowableRow( 1 )
		fgSizer97.AddGrowableRow( 2 )
		fgSizer97.SetFlexibleDirection( wx.BOTH )
		fgSizer97.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer100 = wx.FlexGridSizer( 2, 3, 0, 0 )
		fgSizer100.AddGrowableCol( 1 )
		fgSizer100.SetFlexibleDirection( wx.BOTH )
		fgSizer100.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText64 = wx.StaticText( self, wx.ID_ANY, u"name: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText64.Wrap( -1 )
		fgSizer100.Add( self.m_staticText64, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl40 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer100.Add( self.m_textCtrl40, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button30 = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer100.Add( self.m_button30, 0, wx.ALL, 5 )
		
		
		fgSizer100.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox64 = wx.CheckBox( self, wx.ID_ANY, u"Enabled", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer100.Add( self.m_checkBox64, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_button31 = wx.Button( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button31.Enable( False )
		
		fgSizer100.Add( self.m_button31, 0, wx.ALL, 5 )
		
		
		fgSizer97.Add( fgSizer100, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_splitter3 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter3.Bind( wx.EVT_IDLE, self.m_splitter3OnIdle )
		
		self.m_panel16 = wx.Panel( self.m_splitter3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER|wx.TAB_TRAVERSAL )
		sbSizer23 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel16, wx.ID_ANY, u"Contextuals" ), wx.VERTICAL )
		
		m_listBox1Choices = []
		self.m_listBox1 = wx.ListBox( self.m_panel16, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
		sbSizer23.Add( self.m_listBox1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel16.SetSizer( sbSizer23 )
		self.m_panel16.Layout()
		sbSizer23.Fit( self.m_panel16 )
		self.m_panel17 = wx.Panel( self.m_splitter3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer99 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer99.AddGrowableCol( 0 )
		fgSizer99.AddGrowableRow( 1 )
		fgSizer99.AddGrowableRow( 2 )
		fgSizer99.SetFlexibleDirection( wx.BOTH )
		fgSizer99.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer101 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer101.AddGrowableCol( 0 )
		fgSizer101.AddGrowableRow( 0 )
		fgSizer101.SetFlexibleDirection( wx.BOTH )
		fgSizer101.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer31 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel17, wx.ID_ANY, u"definition" ), wx.VERTICAL )
		
		self.m_richText15 = wx.richtext.RichTextCtrl( self.m_panel17, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		self.m_richText15.SetMinSize( wx.Size( -1,120 ) )
		self.m_richText15.SetMaxSize( wx.Size( -1,120 ) )
		
		sbSizer31.Add( self.m_richText15, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer101.Add( sbSizer31, 1, wx.EXPAND, 5 )
		
		
		fgSizer99.Add( fgSizer101, 1, wx.EXPAND, 5 )
		
		gSizer2 = wx.GridSizer( 2, 2, 0, 0 )
		
		sbSizer25 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel17, wx.ID_ANY, u"declaration prefix" ), wx.VERTICAL )
		
		self.m_richText11 = wx.richtext.RichTextCtrl( self.m_panel17, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer25.Add( self.m_richText11, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		gSizer2.Add( sbSizer25, 1, wx.EXPAND, 5 )
		
		sbSizer27 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel17, wx.ID_ANY, u"implementation prefix" ), wx.VERTICAL )
		
		self.m_richText12 = wx.richtext.RichTextCtrl( self.m_panel17, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer27.Add( self.m_richText12, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		gSizer2.Add( sbSizer27, 1, wx.EXPAND, 5 )
		
		sbSizer28 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel17, wx.ID_ANY, u"declaration sufix" ), wx.VERTICAL )
		
		self.m_richText13 = wx.richtext.RichTextCtrl( self.m_panel17, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer28.Add( self.m_richText13, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		gSizer2.Add( sbSizer28, 1, wx.EXPAND, 5 )
		
		sbSizer29 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel17, wx.ID_ANY, u"implementation sufix" ), wx.VERTICAL )
		
		self.m_richText14 = wx.richtext.RichTextCtrl( self.m_panel17, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer29.Add( self.m_richText14, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		gSizer2.Add( sbSizer29, 1, wx.EXPAND, 5 )
		
		
		fgSizer99.Add( gSizer2, 1, wx.EXPAND, 5 )
		
		
		self.m_panel17.SetSizer( fgSizer99 )
		self.m_panel17.Layout()
		fgSizer99.Fit( self.m_panel17 )
		self.m_splitter3.SplitVertically( self.m_panel16, self.m_panel17, 171 )
		fgSizer97.Add( self.m_splitter3, 1, wx.EXPAND, 5 )
		
		sbSizer30 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Note" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer30.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer97.Add( sbSizer30, 2, wx.EXPAND, 5 )
		
		fgSizer154 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer154.AddGrowableCol( 1 )
		fgSizer154.SetFlexibleDirection( wx.BOTH )
		fgSizer154.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer154.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer5 = wx.StdDialogButtonSizer()
		self.m_sdbSizer5OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer5.AddButton( self.m_sdbSizer5OK )
		self.m_sdbSizer5Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer5.AddButton( self.m_sdbSizer5Cancel )
		m_sdbSizer5.Realize();
		
		fgSizer154.Add( m_sdbSizer5, 1, wx.EXPAND, 5 )
		
		
		fgSizer97.Add( fgSizer154, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer97 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_textCtrl40.Bind( wx.EVT_TEXT, self.OnChangeName )
		self.m_button30.Bind( wx.EVT_BUTTON, self.OnAddNewContext )
		self.m_checkBox64.Bind( wx.EVT_CHECKBOX, self.OnEnabledChanged )
		self.m_button31.Bind( wx.EVT_BUTTON, self.OnRemoveContext )
		self.m_listBox1.Bind( wx.EVT_LISTBOX_DCLICK, self.OnSelectItem )
		self.m_richText15.Bind( wx.EVT_TEXT, self.OnChangeDefinition )
		self.m_richText11.Bind( wx.EVT_TEXT, self.OnChangeDeclarationPrefix )
		self.m_richText12.Bind( wx.EVT_TEXT, self.OnChangeImplementationPrefix )
		self.m_richText13.Bind( wx.EVT_TEXT, self.OnChangeDeclarationSufix )
		self.m_richText14.Bind( wx.EVT_TEXT, self.OnChangeImplementationSufix )
		self.m_richText1.Bind( wx.EVT_TEXT, self.OnChangeNote )
		self.m_sdbSizer5OK.Bind( wx.EVT_BUTTON, self.OnOk )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnChangeName( self, event ):
		event.Skip()
	
	def OnAddNewContext( self, event ):
		event.Skip()
	
	def OnEnabledChanged( self, event ):
		event.Skip()
	
	def OnRemoveContext( self, event ):
		event.Skip()
	
	def OnSelectItem( self, event ):
		event.Skip()
	
	def OnChangeDefinition( self, event ):
		event.Skip()
	
	def OnChangeDeclarationPrefix( self, event ):
		event.Skip()
	
	def OnChangeImplementationPrefix( self, event ):
		event.Skip()
	
	def OnChangeDeclarationSufix( self, event ):
		event.Skip()
	
	def OnChangeImplementationSufix( self, event ):
		event.Skip()
	
	def OnChangeNote( self, event ):
		event.Skip()
	
	def OnOk( self, event ):
		event.Skip()
	
	def m_splitter3OnIdle( self, event ):
		self.m_splitter3.SetSashPosition( 171 )
		self.m_splitter3.Unbind( wx.EVT_IDLE )
	

###########################################################################
## Class GenerateSources
###########################################################################

class GenerateSources ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Generate sources ...", pos = wx.DefaultPosition, size = wx.Size( 629,456 ), style = wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer71 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer71.AddGrowableCol( 0 )
		fgSizer71.AddGrowableRow( 0 )
		fgSizer71.SetFlexibleDirection( wx.BOTH )
		fgSizer71.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		fgSizer72 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer72.AddGrowableCol( 0 )
		fgSizer72.AddGrowableCol( 1 )
		fgSizer72.AddGrowableRow( 0 )
		fgSizer72.SetFlexibleDirection( wx.BOTH )
		fgSizer72.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer75 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer75.AddGrowableCol( 0 )
		fgSizer75.AddGrowableRow( 1 )
		fgSizer75.SetFlexibleDirection( wx.BOTH )
		fgSizer75.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer74 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer74.AddGrowableCol( 0 )
		fgSizer74.AddGrowableCol( 1 )
		fgSizer74.SetFlexibleDirection( wx.BOTH )
		fgSizer74.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText37 = wx.StaticText( self, wx.ID_ANY, u"Author", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText37.Wrap( -1 )
		fgSizer74.Add( self.m_staticText37, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_author = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer74.Add( self.m_author, 0, wx.ALL, 5 )
		
		self.m_staticText38 = wx.StaticText( self, wx.ID_ANY, u"Date", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38.Wrap( -1 )
		fgSizer74.Add( self.m_staticText38, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_date = wx.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.DP_DEFAULT )
		fgSizer74.Add( self.m_date, 0, wx.ALL, 5 )
		
		
		fgSizer75.Add( fgSizer74, 1, wx.EXPAND|wx.TOP, 5 )
		
		sbSizer20 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Comments" ), wx.VERTICAL )
		
		self.m_richText15 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer20.Add( self.m_richText15, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer75.Add( sbSizer20, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer72.Add( fgSizer75, 1, wx.EXPAND, 5 )
		
		self.m_report = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ICON|wx.LC_REPORT )
		fgSizer72.Add( self.m_report, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer71.Add( fgSizer72, 0, wx.EXPAND|wx.TOP, 5 )
		
		fgSizer73 = wx.FlexGridSizer( 1, 4, 0, 0 )
		fgSizer73.AddGrowableCol( 0 )
		fgSizer73.SetFlexibleDirection( wx.BOTH )
		fgSizer73.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer73.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_overwrite = wx.CheckBox( self, wx.ID_ANY, u"Overwrite &all", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer73.Add( self.m_overwrite, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_button23 = wx.Button( self, wx.ID_ANY, u"&Generate", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer73.Add( self.m_button23, 0, wx.ALL, 5 )
		
		self.m_button24 = wx.Button( self, wx.ID_CANCEL, u"&Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer73.Add( self.m_button24, 0, wx.ALL, 5 )
		
		
		fgSizer71.Add( fgSizer73, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer71 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button23.Bind( wx.EVT_BUTTON, self.OnGenerate )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnGenerate( self, event ):
		event.Skip()
	

###########################################################################
## Class NewArgument
###########################################################################

class NewArgument ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New argument", pos = wx.DefaultPosition, size = wx.Size( 546,483 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer23 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer23.AddGrowableCol( 0 )
		fgSizer23.AddGrowableRow( 2 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer24 = wx.FlexGridSizer( 2, 6, 0, 0 )
		fgSizer24.AddGrowableCol( 1 )
		fgSizer24.AddGrowableCol( 4 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		fgSizer24.Add( self.m_staticText10, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_typeChoices = []
		self.m_type = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_typeChoices, wx.CB_SORT|wx.WANTS_CHARS )
		self.m_type.SetSelection( 0 )
		fgSizer24.Add( self.m_type, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer24.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"&name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer24.Add( self.m_staticText9, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SUNKEN_BORDER )
		fgSizer24.Add( self.m_name, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		fgSizer24.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText67 = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText67.Wrap( -1 )
		self.m_staticText67.Enable( False )
		
		fgSizer24.Add( self.m_staticText67, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_template_args = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template_args.Enable( False )
		
		fgSizer24.Add( self.m_template_args, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText68 = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText68.Wrap( -1 )
		self.m_staticText68.Enable( False )
		
		fgSizer24.Add( self.m_staticText68, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText111 = wx.StaticText( self, wx.ID_ANY, u"value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText111.Wrap( -1 )
		fgSizer24.Add( self.m_staticText111, 0, wx.ALL, 5 )
		
		self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer24.Add( self.m_textCtrl8, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer23.Add( fgSizer24, 1, wx.EXPAND|wx.TOP, 5 )
		
		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"properties" ), wx.VERTICAL )
		
		fgSizer25 = wx.FlexGridSizer( 3, 4, 0, 0 )
		fgSizer25.SetFlexibleDirection( wx.BOTH )
		fgSizer25.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox48 = wx.CheckBox( self, wx.ID_ANY, u"mutable", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox48.Hide()
		
		fgSizer25.Add( self.m_checkBox48, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_const = wx.CheckBox( self, wx.ID_ANY, u"&const", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_const, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_ptr = wx.CheckBox( self, wx.ID_ANY, u"&pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_ptr, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_reference = wx.CheckBox( self, wx.ID_ANY, u"&reference", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_reference, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_volatile = wx.CheckBox( self, wx.ID_ANY, u"volatile", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_volatile.Enable( False )
		self.m_volatile.Hide()
		
		fgSizer25.Add( self.m_volatile, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_constptr = wx.CheckBox( self, wx.ID_ANY, u"c&onst pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_constptr.Enable( False )
		
		fgSizer25.Add( self.m_constptr, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_array = wx.CheckBox( self, wx.ID_ANY, u"&array", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_array, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl7 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl7.Enable( False )
		self.m_textCtrl7.Hide()
		
		fgSizer25.Add( self.m_textCtrl7, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox50 = wx.CheckBox( self, wx.ID_ANY, u"volatile pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox50.Enable( False )
		self.m_checkBox50.Hide()
		
		fgSizer25.Add( self.m_checkBox50, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_pptr = wx.CheckBox( self, wx.ID_ANY, u"po&inter/pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_pptr.Enable( False )
		
		fgSizer25.Add( self.m_pptr, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox51 = wx.CheckBox( self, wx.ID_ANY, u"bit field", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox51.Enable( False )
		self.m_checkBox51.Hide()
		
		fgSizer25.Add( self.m_checkBox51, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl39 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl39.Enable( False )
		self.m_textCtrl39.Hide()
		
		fgSizer25.Add( self.m_textCtrl39, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer5.Add( fgSizer25, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		fgSizer23.Add( sbSizer5, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"note" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer23.Add( sbSizer6, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer23.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer23 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_type.Bind( wx.EVT_CHOICE, self.OnTypeChanged )
		self.m_type.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_const.Bind( wx.EVT_CHECKBOX, self.OnToggleConst )
		self.m_ptr.Bind( wx.EVT_CHECKBOX, self.OnTogglePtr )
		self.m_reference.Bind( wx.EVT_CHECKBOX, self.OnToggleReference )
		self.m_constptr.Bind( wx.EVT_CHECKBOX, self.OnToggleConstPtr )
		self.m_array.Bind( wx.EVT_CHECKBOX, self.OnToggleArray )
		self.m_pptr.Bind( wx.EVT_CHECKBOX, self.OnTogglePointerPointer )
		self.m_checkBox51.Bind( wx.EVT_CHECKBOX, self.OnToggleBitFiled )
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnTypeChanged( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	def OnToggleConst( self, event ):
		event.Skip()
	
	def OnTogglePtr( self, event ):
		event.Skip()
	
	def OnToggleReference( self, event ):
		event.Skip()
	
	def OnToggleConstPtr( self, event ):
		event.Skip()
	
	def OnToggleArray( self, event ):
		event.Skip()
	
	def OnTogglePointerPointer( self, event ):
		event.Skip()
	
	def OnToggleBitFiled( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyArgument
###########################################################################

class NewPyArgument ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New argument", pos = wx.DefaultPosition, size = wx.Size( 428,356 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer23 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer23.AddGrowableCol( 0 )
		fgSizer23.AddGrowableRow( 1 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer24 = wx.FlexGridSizer( 2, 4, 0, 0 )
		fgSizer24.AddGrowableCol( 1 )
		fgSizer24.AddGrowableCol( 3 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"&name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer24.Add( self.m_staticText9, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl6 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SUNKEN_BORDER )
		fgSizer24.Add( self.m_textCtrl6, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText111 = wx.StaticText( self, wx.ID_ANY, u"=", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText111.Wrap( -1 )
		fgSizer24.Add( self.m_staticText111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer24.Add( self.m_textCtrl8, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer23.Add( fgSizer24, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"note" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer23.Add( sbSizer6, 1, wx.EXPAND|wx.ALL, 5 )
		
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
		
		
		fgSizer23.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer23 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewClass
###########################################################################

class NewClass ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New class", pos = wx.DefaultPosition, size = wx.Size( 549,464 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer6 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.AddGrowableRow( 1 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer7 = wx.FlexGridSizer( 5, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.AddGrowableRow( 0 )
		fgSizer7.AddGrowableRow( 2 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox90 = wx.CheckBox( self, wx.ID_ANY, u"Extern class", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer7.Add( self.m_checkBox90, 0, wx.ALL, 5 )
		
		
		fgSizer7.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Name :", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer7.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textCtrl2, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_staticText48 = wx.StaticText( self, wx.ID_ANY, u"Members prefix :", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText48.Wrap( -1 )
		fgSizer7.Add( self.m_staticText48, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textPrefix = wx.TextCtrl( self, wx.ID_ANY, u"_", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textPrefix, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox60 = wx.CheckBox( self, wx.ID_ANY, u"serialize", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_checkBox60, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		fgSizer134 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer134.AddGrowableCol( 1 )
		fgSizer134.AddGrowableCol( 2 )
		fgSizer134.SetFlexibleDirection( wx.BOTH )
		fgSizer134.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox83 = wx.CheckBox( self, wx.ID_ANY, u"struct", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer134.Add( self.m_checkBox83, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText88 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText88.Wrap( -1 )
		self.m_staticText88.Enable( False )
		
		fgSizer134.Add( self.m_staticText88, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_choice2Choices = [ u"public", u"protected", u"private" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		self.m_choice2.Enable( False )
		
		fgSizer134.Add( self.m_choice2, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer7.Add( fgSizer134, 1, wx.EXPAND, 5 )
		
		self.m_checkBox61 = wx.CheckBox( self, wx.ID_ANY, u"template", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_checkBox61, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		fgSizer93 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer93.AddGrowableCol( 1 )
		fgSizer93.AddGrowableRow( 0 )
		fgSizer93.SetFlexibleDirection( wx.BOTH )
		fgSizer93.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_stStartTemplate = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stStartTemplate.Wrap( -1 )
		self.m_stStartTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stStartTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_template = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template.Enable( False )
		
		fgSizer93.Add( self.m_template, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_stEndTemplate = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stEndTemplate.Wrap( -1 )
		self.m_stEndTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stEndTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer7.Add( fgSizer93, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer6.Add( fgSizer7, 0, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer6.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
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
		
		
		fgSizer6.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_checkBox90.Bind( wx.EVT_CHECKBOX, self.OnToggleExternalClass )
		self.m_checkBox61.Bind( wx.EVT_CHECKBOX, self.OnToggleTemplate )
		self.m_template.Bind( wx.EVT_TEXT, self.OnChangeTemplateSpecification )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnToggleExternalClass( self, event ):
		event.Skip()
	
	def OnToggleTemplate( self, event ):
		event.Skip()
	
	def OnChangeTemplateSpecification( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyClass
###########################################################################

class NewPyClass ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New class", pos = wx.DefaultPosition, size = wx.Size( 489,464 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer6 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.AddGrowableRow( 1 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer7 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.AddGrowableRow( 1 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Name :", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer7.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textCtrl2, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_staticText48 = wx.StaticText( self, wx.ID_ANY, u"Members prefix :", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText48.Wrap( -1 )
		fgSizer7.Add( self.m_staticText48, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textPrefix = wx.TextCtrl( self, wx.ID_ANY, u"_", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textPrefix, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer7.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox94 = wx.CheckBox( self, wx.ID_ANY, u"export", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_checkBox94, 0, wx.ALL, 5 )
		
		
		fgSizer6.Add( fgSizer7, 0, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer6.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
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
		
		
		fgSizer6.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewClassDiagram
###########################################################################

class NewClassDiagram ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"new class diagram", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer6 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.AddGrowableRow( 1 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer7 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.AddGrowableRow( 0 )
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
		
		
		fgSizer6.Add( sbSizer9, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer6.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewConstructor
###########################################################################

class NewConstructor ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New constructor", pos = wx.DefaultPosition, size = wx.Size( 546,483 ), style = wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 2 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Properties" ), wx.VERTICAL )
		
		fgSizer20 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer20.AddGrowableCol( 0 )
		fgSizer20.AddGrowableCol( 1 )
		fgSizer20.SetFlexibleDirection( wx.BOTH )
		fgSizer20.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer16 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer16.AddGrowableCol( 1 )
		fgSizer16.SetFlexibleDirection( wx.BOTH )
		fgSizer16.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer16.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.RIGHT|wx.LEFT, 5 )
		
		m_choice2Choices = [ u"public", u"protected", u"private" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		fgSizer16.Add( self.m_choice2, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_checkBox6 = wx.CheckBox( self, wx.ID_ANY, u"&calling", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer16.Add( self.m_checkBox6, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT|wx.ALIGN_RIGHT, 5 )
		
		m_comboBox1Choices = [ u"cdecl", u"stdcall", u"fastcall", u"naked" ]
		self.m_comboBox1 = wx.ComboBox( self, wx.ID_ANY, u"cdecl", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
		self.m_comboBox1.Enable( False )
		
		fgSizer16.Add( self.m_comboBox1, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer20.Add( fgSizer16, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		fgSizer141 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer141.AddGrowableCol( 0 )
		fgSizer141.AddGrowableCol( 1 )
		fgSizer141.SetFlexibleDirection( wx.BOTH )
		fgSizer141.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox31 = wx.CheckBox( self, wx.ID_ANY, u"&inline", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer141.Add( self.m_checkBox31, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox41 = wx.CheckBox( self, wx.ID_ANY, u"&explicit", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer141.Add( self.m_checkBox41, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox92 = wx.CheckBox( self, wx.ID_ANY, u"&declare", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox92.SetValue(True) 
		fgSizer141.Add( self.m_checkBox92, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox93 = wx.CheckBox( self, wx.ID_ANY, u"i&mplement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox93.SetValue(True) 
		fgSizer141.Add( self.m_checkBox93, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBoxPreferred = wx.CheckBox( self, wx.ID_ANY, u"preferred", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer141.Add( self.m_checkBoxPreferred, 0, wx.ALL, 5 )
		
		
		fgSizer20.Add( fgSizer141, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		sbSizer3.Add( fgSizer20, 1, wx.EXPAND, 5 )
		
		
		fgSizer12.Add( sbSizer3, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Notes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer12.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		fgSizer12.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer21.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.SetDefault() 
		fgSizer21.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_checkBox6.Bind( wx.EVT_CHECKBOX, self.OnCallingToggle )
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCallingToggle( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewDestructor
###########################################################################

class NewDestructor ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New destructor", pos = wx.DefaultPosition, size = wx.Size( 546,483 ), style = wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 2 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Properties" ), wx.VERTICAL )
		
		fgSizer20 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer20.AddGrowableCol( 0 )
		fgSizer20.AddGrowableCol( 1 )
		fgSizer20.AddGrowableRow( 0 )
		fgSizer20.SetFlexibleDirection( wx.BOTH )
		fgSizer20.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer16 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer16.AddGrowableCol( 1 )
		fgSizer16.SetFlexibleDirection( wx.BOTH )
		fgSizer16.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer16.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.RIGHT|wx.LEFT, 5 )
		
		m_choice2Choices = [ u"public", u"protected", u"private" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		fgSizer16.Add( self.m_choice2, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_checkBox6 = wx.CheckBox( self, wx.ID_ANY, u"&calling", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer16.Add( self.m_checkBox6, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		m_comboBox1Choices = [ u"cdecl", u"stdcall", u"fastcall", u"naked" ]
		self.m_comboBox1 = wx.ComboBox( self, wx.ID_ANY, u"cdecl", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
		self.m_comboBox1.Enable( False )
		
		fgSizer16.Add( self.m_comboBox1, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer20.Add( fgSizer16, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		fgSizer141 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer141.AddGrowableCol( 0 )
		fgSizer141.AddGrowableCol( 1 )
		fgSizer141.SetFlexibleDirection( wx.BOTH )
		fgSizer141.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox31 = wx.CheckBox( self, wx.ID_ANY, u"&inline", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer141.Add( self.m_checkBox31, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer141.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox41 = wx.CheckBox( self, wx.ID_ANY, u"&virtual", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox41.SetValue(True) 
		fgSizer141.Add( self.m_checkBox41, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox104 = wx.CheckBox( self, wx.ID_ANY, u"&pure", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer141.Add( self.m_checkBox104, 0, wx.ALL, 5 )
		
		self.m_checkBox92 = wx.CheckBox( self, wx.ID_ANY, u"&declare", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox92.SetValue(True) 
		fgSizer141.Add( self.m_checkBox92, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox93 = wx.CheckBox( self, wx.ID_ANY, u"i&mplement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox93.SetValue(True) 
		fgSizer141.Add( self.m_checkBox93, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer20.Add( fgSizer141, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		sbSizer3.Add( fgSizer20, 1, wx.EXPAND, 5 )
		
		
		fgSizer12.Add( sbSizer3, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Notes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer12.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		fgSizer12.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer21.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.SetDefault() 
		fgSizer21.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewEnum
###########################################################################

class NewEnum ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New enum", pos = wx.DefaultPosition, size = wx.Size( 613,528 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer135 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer135.AddGrowableCol( 0 )
		fgSizer135.AddGrowableRow( 1 )
		fgSizer135.AddGrowableRow( 2 )
		fgSizer135.SetFlexibleDirection( wx.BOTH )
		fgSizer135.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer136 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer136.AddGrowableCol( 1 )
		fgSizer136.AddGrowableCol( 2 )
		fgSizer136.SetFlexibleDirection( wx.BOTH )
		fgSizer136.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText89 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText89.Wrap( -1 )
		fgSizer136.Add( self.m_staticText89, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl55 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer136.Add( self.m_textCtrl55, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		fgSizer16 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer16.AddGrowableCol( 1 )
		fgSizer16.SetFlexibleDirection( wx.BOTH )
		fgSizer16.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		self.m_staticText8.Enable( False )
		
		fgSizer16.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.RIGHT|wx.LEFT, 5 )
		
		m_choice2Choices = [ u"public", u"protected", u"private" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		self.m_choice2.Enable( False )
		
		fgSizer16.Add( self.m_choice2, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		fgSizer136.Add( fgSizer16, 1, wx.EXPAND, 5 )
		
		
		fgSizer135.Add( fgSizer136, 1, wx.EXPAND|wx.TOP|wx.LEFT, 5 )
		
		fgSizer137 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer137.AddGrowableCol( 0 )
		fgSizer137.AddGrowableRow( 0 )
		fgSizer137.SetFlexibleDirection( wx.BOTH )
		fgSizer137.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_listCtrl5 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.m_listCtrl5.SetToolTipString( u"click for select item\ndouble click or enter for edit" )
		
		fgSizer137.Add( self.m_listCtrl5, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer138 = wx.FlexGridSizer( 5, 1, 0, 0 )
		fgSizer138.AddGrowableCol( 0 )
		fgSizer138.AddGrowableRow( 4 )
		fgSizer138.SetFlexibleDirection( wx.BOTH )
		fgSizer138.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer138.SetMinSize( wx.Size( 32,-1 ) ) 
		self.m_bpButton11 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-add", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer138.Add( self.m_bpButton11, 0, wx.ALL, 5 )
		
		self.m_bpButton12 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-go-up", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton12.Enable( False )
		
		fgSizer138.Add( self.m_bpButton12, 0, wx.ALL, 5 )
		
		self.m_bpButton13 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-go-down", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton13.Enable( False )
		
		fgSizer138.Add( self.m_bpButton13, 0, wx.ALL, 5 )
		
		self.m_bpButton14 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-delete", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton14.Enable( False )
		
		fgSizer138.Add( self.m_bpButton14, 0, wx.ALL, 5 )
		
		
		fgSizer137.Add( fgSizer138, 1, wx.EXPAND, 5 )
		
		
		fgSizer135.Add( fgSizer137, 0, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.HORIZONTAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer135.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer43 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer43.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_button8, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button7.SetDefault() 
		fgSizer43.Add( self.m_button7, 0, wx.ALL, 5 )
		
		
		fgSizer135.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer135 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_listCtrl5.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.OnEditEnumItem )
		self.m_listCtrl5.Bind( wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselectEnumItem )
		self.m_listCtrl5.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnSelectEnumItem )
		self.m_bpButton11.Bind( wx.EVT_BUTTON, self.OnAddEnumItem )
		self.m_bpButton12.Bind( wx.EVT_BUTTON, self.OnEnumItemUp )
		self.m_bpButton13.Bind( wx.EVT_BUTTON, self.OnEnumItemDown )
		self.m_bpButton14.Bind( wx.EVT_BUTTON, self.OnRemoveEnumItem )
		self.m_button8.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button7.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnEditEnumItem( self, event ):
		event.Skip()
	
	def OnDeselectEnumItem( self, event ):
		event.Skip()
	
	def OnSelectEnumItem( self, event ):
		event.Skip()
	
	def OnAddEnumItem( self, event ):
		event.Skip()
	
	def OnEnumItemUp( self, event ):
		event.Skip()
	
	def OnEnumItemDown( self, event ):
		event.Skip()
	
	def OnRemoveEnumItem( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewEnumItem
###########################################################################

class NewEnumItem ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Enum item", pos = wx.DefaultPosition, size = wx.Size( 339,148 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer142 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer142.AddGrowableCol( 0 )
		fgSizer142.AddGrowableRow( 0 )
		fgSizer142.SetFlexibleDirection( wx.BOTH )
		fgSizer142.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer149 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer149.AddGrowableCol( 0 )
		fgSizer149.SetFlexibleDirection( wx.BOTH )
		fgSizer149.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer143 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer143.AddGrowableCol( 1 )
		fgSizer143.SetFlexibleDirection( wx.BOTH )
		fgSizer143.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer143.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer143.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText90 = wx.StaticText( self, wx.ID_ANY, u"label", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText90.Wrap( -1 )
		fgSizer143.Add( self.m_staticText90, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl56 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer143.Add( self.m_textCtrl56, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText91 = wx.StaticText( self, wx.ID_ANY, u"value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText91.Wrap( -1 )
		fgSizer143.Add( self.m_staticText91, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_comboBox6Choices = []
		self.m_comboBox6 = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_comboBox6Choices, 0 )
		fgSizer143.Add( self.m_comboBox6, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer149.Add( fgSizer143, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer142.Add( fgSizer149, 1, wx.EXPAND|wx.TOP, 5 )
		
		fgSizer43 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer43.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_button8, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button7.SetDefault() 
		fgSizer43.Add( self.m_button7, 0, wx.ALL, 5 )
		
		
		fgSizer142.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer142 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button8.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button7.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewFile
###########################################################################

class NewFile ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New file", pos = wx.DefaultPosition, size = wx.Size( 274,144 ), style = wx.DEFAULT_DIALOG_STYLE )
		
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
## Class NewInheritance
###########################################################################

class NewInheritance ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New inheritance", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer54 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer54.AddGrowableCol( 0 )
		fgSizer54.AddGrowableRow( 1 )
		fgSizer54.SetFlexibleDirection( wx.BOTH )
		fgSizer54.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer55 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer55.AddGrowableCol( 1 )
		fgSizer55.SetFlexibleDirection( wx.BOTH )
		fgSizer55.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"from class:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )
		fgSizer55.Add( self.m_staticText24, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice11Choices = []
		self.m_choice11 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice11Choices, 0 )
		self.m_choice11.SetSelection( 0 )
		fgSizer55.Add( self.m_choice11, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"access:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		fgSizer55.Add( self.m_staticText25, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice12Choices = [ u"public", u"protected", u"private" ]
		self.m_choice12 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice12Choices, 0 )
		self.m_choice12.SetSelection( 0 )
		fgSizer55.Add( self.m_choice12, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer55.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox51 = wx.CheckBox( self, wx.ID_ANY, u"&virtual", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer55.Add( self.m_checkBox51, 0, wx.ALL, 5 )
		
		
		fgSizer54.Add( fgSizer55, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer54.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer43 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer43.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_button8, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button7.SetDefault() 
		fgSizer43.Add( self.m_button7, 0, wx.ALL, 5 )
		
		
		fgSizer54.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer54 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button8.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button7.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyImport
###########################################################################

class NewPyImport ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New import", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_VALIDATE_RECURSIVELY )
		
		fgSizer54 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer54.AddGrowableCol( 0 )
		fgSizer54.AddGrowableRow( 1 )
		fgSizer54.SetFlexibleDirection( wx.BOTH )
		fgSizer54.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer242 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer242.AddGrowableCol( 0 )
		fgSizer242.AddGrowableRow( 0 )
		fgSizer242.SetFlexibleDirection( wx.BOTH )
		fgSizer242.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_choicebook5 = wx.Choicebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_choicebook5.SetExtraStyle( wx.WS_EX_VALIDATE_RECURSIVELY )
		
		self.m_panel31 = wx.Panel( self.m_choicebook5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel31.SetExtraStyle( wx.WS_EX_VALIDATE_RECURSIVELY )
		
		fgSizer243 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer243.AddGrowableCol( 0 )
		fgSizer243.SetFlexibleDirection( wx.BOTH )
		fgSizer243.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_textCtrl82 = wx.TextCtrl( self.m_panel31, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer243.Add( self.m_textCtrl82, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer244 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer244.AddGrowableCol( 1 )
		fgSizer244.SetFlexibleDirection( wx.BOTH )
		fgSizer244.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox147 = wx.CheckBox( self.m_panel31, wx.ID_ANY, u"as", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer244.Add( self.m_checkBox147, 0, wx.ALL, 5 )
		
		self.m_textCtrl83 = wx.TextCtrl( self.m_panel31, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl83.Enable( False )
		
		fgSizer244.Add( self.m_textCtrl83, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer243.Add( fgSizer244, 1, wx.EXPAND, 5 )
		
		
		self.m_panel31.SetSizer( fgSizer243 )
		self.m_panel31.Layout()
		fgSizer243.Fit( self.m_panel31 )
		self.m_choicebook5.AddPage( self.m_panel31, u"import", True )
		self.m_panel32 = wx.Panel( self.m_choicebook5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel32.SetExtraStyle( wx.WS_EX_VALIDATE_RECURSIVELY )
		
		fgSizer2431 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer2431.AddGrowableCol( 0 )
		fgSizer2431.SetFlexibleDirection( wx.BOTH )
		fgSizer2431.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_textCtrl821 = wx.TextCtrl( self.m_panel32, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.WANTS_CHARS )
		fgSizer2431.Add( self.m_textCtrl821, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer2441 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer2441.AddGrowableCol( 1 )
		fgSizer2441.SetFlexibleDirection( wx.BOTH )
		fgSizer2441.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText134 = wx.StaticText( self.m_panel32, wx.ID_ANY, u"import", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText134.Wrap( -1 )
		fgSizer2441.Add( self.m_staticText134, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_comboBox12Choices = [ u"caca", u"pis" ]
		self.m_comboBox12 = wx.ComboBox( self.m_panel32, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_comboBox12Choices, wx.CB_DROPDOWN|wx.WANTS_CHARS )
		fgSizer2441.Add( self.m_comboBox12, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox1471 = wx.CheckBox( self.m_panel32, wx.ID_ANY, u"as", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2441.Add( self.m_checkBox1471, 0, wx.ALL, 5 )
		
		self.m_textCtrl831 = wx.TextCtrl( self.m_panel32, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl831.Enable( False )
		
		fgSizer2441.Add( self.m_textCtrl831, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer2431.Add( fgSizer2441, 1, wx.EXPAND, 5 )
		
		
		self.m_panel32.SetSizer( fgSizer2431 )
		self.m_panel32.Layout()
		fgSizer2431.Fit( self.m_panel32 )
		self.m_choicebook5.AddPage( self.m_panel32, u"from", False )
		fgSizer242.Add( self.m_choicebook5, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer54.Add( fgSizer242, 1, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer54.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer43 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer43.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_button8, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button7.SetDefault() 
		fgSizer43.Add( self.m_button7, 0, wx.ALL, 5 )
		
		
		fgSizer54.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer54 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_checkBox147.Bind( wx.EVT_CHECKBOX, self.OnAs )
		self.m_textCtrl821.Bind( wx.EVT_TEXT, self.OnFromChange )
		self.m_comboBox12.Bind( wx.EVT_CHAR, self.OnChangeFor )
		self.m_comboBox12.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_checkBox1471.Bind( wx.EVT_CHECKBOX, self.OnAs )
		self.m_button8.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button7.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnAs( self, event ):
		event.Skip()
	
	def OnFromChange( self, event ):
		event.Skip()
	
	def OnChangeFor( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyInheritance
###########################################################################

class NewPyInheritance ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New inheritance", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer54 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer54.AddGrowableCol( 0 )
		fgSizer54.AddGrowableRow( 1 )
		fgSizer54.SetFlexibleDirection( wx.BOTH )
		fgSizer54.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer55 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer55.AddGrowableCol( 1 )
		fgSizer55.SetFlexibleDirection( wx.BOTH )
		fgSizer55.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"from class:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )
		fgSizer55.Add( self.m_staticText24, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice11Choices = []
		self.m_choice11 = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_choice11Choices, 0 )
		fgSizer55.Add( self.m_choice11, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer54.Add( fgSizer55, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer54.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer43 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer43.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_button8, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button7.SetDefault() 
		fgSizer43.Add( self.m_button7, 0, wx.ALL, 5 )
		
		
		fgSizer54.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer54 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button8.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button7.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewMember
###########################################################################

class NewMember ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New member", pos = wx.DefaultPosition, size = wx.Size( 621,489 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer23 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer23.AddGrowableCol( 0 )
		fgSizer23.AddGrowableRow( 2 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		gSizer2 = wx.GridSizer( 3, 2, 0, 0 )
		
		fgSizer184 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer184.AddGrowableCol( 1 )
		fgSizer184.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer184.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"&type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		fgSizer184.Add( self.m_staticText10, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		m_typeChoices = []
		self.m_type = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_typeChoices, wx.CB_SORT|wx.WANTS_CHARS )
		self.m_type.SetSelection( 0 )
		fgSizer184.Add( self.m_type, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5 )
		
		
		gSizer2.Add( fgSizer184, 1, wx.EXPAND|wx.LEFT, 5 )
		
		fgSizer185 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer185.AddGrowableCol( 1 )
		fgSizer185.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer185.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"&name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer185.Add( self.m_staticText9, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SUNKEN_BORDER )
		fgSizer185.Add( self.m_name, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer185.AddSpacer( ( 0, 0), 0, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		gSizer2.Add( fgSizer185, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		fgSizer186 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer186.AddGrowableCol( 1 )
		fgSizer186.SetFlexibleDirection( wx.BOTH )
		fgSizer186.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText67 = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText67.Wrap( -1 )
		self.m_staticText67.Enable( False )
		
		fgSizer186.Add( self.m_staticText67, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_template_args = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template_args.Enable( False )
		
		fgSizer186.Add( self.m_template_args, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		gSizer2.Add( fgSizer186, 1, wx.EXPAND|wx.LEFT, 5 )
		
		fgSizer187 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer187.AddGrowableCol( 1 )
		fgSizer187.SetFlexibleDirection( wx.BOTH )
		fgSizer187.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText68 = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText68.Wrap( -1 )
		self.m_staticText68.Enable( False )
		
		fgSizer187.Add( self.m_staticText68, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer187.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer187.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		gSizer2.Add( fgSizer187, 1, wx.EXPAND|wx.RIGHT, 5 )
		
		fgSizer188 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer188.AddGrowableCol( 1 )
		fgSizer188.SetFlexibleDirection( wx.BOTH )
		fgSizer188.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText50 = wx.StaticText( self, wx.ID_ANY, u"&access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText50.Wrap( -1 )
		fgSizer188.Add( self.m_staticText50, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.RIGHT|wx.LEFT, 5 )
		
		m_choice2Choices = [ u"public", u"protected", u"private" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		fgSizer188.Add( self.m_choice2, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5 )
		
		
		gSizer2.Add( fgSizer188, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.LEFT, 5 )
		
		fgSizer190 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer190.AddGrowableCol( 1 )
		fgSizer190.SetFlexibleDirection( wx.BOTH )
		fgSizer190.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"&default", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer190.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer190.Add( self.m_textCtrl8, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5 )
		
		
		fgSizer190.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		gSizer2.Add( fgSizer190, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer23.Add( gSizer2, 1, wx.EXPAND|wx.TOP, 5 )
		
		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"properties" ), wx.VERTICAL )
		
		fgSizer25 = wx.FlexGridSizer( 4, 4, 0, 0 )
		fgSizer25.AddGrowableCol( 3 )
		fgSizer25.SetFlexibleDirection( wx.BOTH )
		fgSizer25.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox105 = wx.CheckBox( self, wx.ID_ANY, u"&static", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox105, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox48 = wx.CheckBox( self, wx.ID_ANY, u"&mutable", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox48, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_ptr = wx.CheckBox( self, wx.ID_ANY, u"&pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_ptr, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_const = wx.CheckBox( self, wx.ID_ANY, u"&const", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_const, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_reference = wx.CheckBox( self, wx.ID_ANY, u"&reference", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_reference, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox49 = wx.CheckBox( self, wx.ID_ANY, u"&volatile", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox49, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_constptr = wx.CheckBox( self, wx.ID_ANY, u"c&onst pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_constptr.Enable( False )
		
		fgSizer25.Add( self.m_constptr, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox50 = wx.CheckBox( self, wx.ID_ANY, u"vo&latile pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox50.Enable( False )
		
		fgSizer25.Add( self.m_checkBox50, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_pptr = wx.CheckBox( self, wx.ID_ANY, u"po&inter/pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_pptr.Enable( False )
		
		fgSizer25.Add( self.m_pptr, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer25.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_array = wx.CheckBox( self, wx.ID_ANY, u"arra&y", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_array, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl7 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl7.Enable( False )
		self.m_textCtrl7.Hide()
		
		fgSizer25.Add( self.m_textCtrl7, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer25.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer25.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox51 = wx.CheckBox( self, wx.ID_ANY, u"&bit field", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox51, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl39 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl39.Enable( False )
		self.m_textCtrl39.Hide()
		
		fgSizer25.Add( self.m_textCtrl39, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer5.Add( fgSizer25, 1, wx.EXPAND, 5 )
		
		
		fgSizer23.Add( sbSizer5, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"n&otes" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer23.Add( sbSizer6, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer23.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer23 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_type.Bind( wx.EVT_CHOICE, self.OnTypeChanged )
		self.m_type.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_name.Bind( wx.EVT_TEXT_ENTER, self.OnEnterName )
		self.m_checkBox105.Bind( wx.EVT_CHECKBOX, self.OnToggleStatic )
		self.m_ptr.Bind( wx.EVT_CHECKBOX, self.OnPointerToggle )
		self.m_array.Bind( wx.EVT_CHECKBOX, self.OnToggleArray )
		self.m_checkBox51.Bind( wx.EVT_CHECKBOX, self.OnToggleBitFiled )
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnTypeChanged( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	def OnEnterName( self, event ):
		event.Skip()
	
	def OnToggleStatic( self, event ):
		event.Skip()
	
	def OnPointerToggle( self, event ):
		event.Skip()
	
	def OnToggleArray( self, event ):
		event.Skip()
	
	def OnToggleBitFiled( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyMember
###########################################################################

class NewPyMember ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New member", pos = wx.DefaultPosition, size = wx.Size( 545,392 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer23 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer23.AddGrowableCol( 0 )
		fgSizer23.AddGrowableRow( 1 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer24 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer24.AddGrowableCol( 0 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer202 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer202.AddGrowableCol( 0 )
		fgSizer202.SetFlexibleDirection( wx.BOTH )
		fgSizer202.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer200 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer200.AddGrowableCol( 1 )
		fgSizer200.SetFlexibleDirection( wx.BOTH )
		fgSizer200.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer200.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl6 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SUNKEN_BORDER )
		fgSizer200.Add( self.m_textCtrl6, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer202.Add( fgSizer200, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.EXPAND, 5 )
		
		sbSizer52 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"initialization" ), wx.VERTICAL )
		
		self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		sbSizer52.Add( self.m_textCtrl8, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5 )
		
		
		fgSizer202.Add( sbSizer52, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer24.Add( fgSizer202, 1, wx.EXPAND, 5 )
		
		m_radioBox1Choices = [ u"class variable", u"instance variable" ]
		self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
		self.m_radioBox1.SetSelection( 1 )
		fgSizer24.Add( self.m_radioBox1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer23.Add( fgSizer24, 1, wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"notes" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer23.Add( sbSizer6, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer23.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer23 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewMemberMethod
###########################################################################

class NewMemberMethod ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New method", pos = wx.DefaultPosition, size = wx.Size( 596,500 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 6, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 3 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer15 = wx.FlexGridSizer( 2, 3, 0, 0 )
		fgSizer15.AddGrowableCol( 1 )
		fgSizer15.SetFlexibleDirection( wx.BOTH )
		fgSizer15.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"method name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		fgSizer15.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_comboBox5Choices = [ u"operator =", u"operator ==", u"operator !=", u"operator <", u"operator >", u"operator <=", u"operator >=", u"operator +", u"operator -", u"operator *", u"operator /", u"operator %", u"operator +=", u"operator -=", u"operator *=", u"operator /=", u"operator %=", u"operator !", u"operator &&", u"operator ||", u"operator ++", u"operator --", u"operator &", u"operator |", u"operator ^", u"operator ~", u"operator &=", u"operator |=", u"operator ^=", u"operator <<", u"operator >>", u"operator <<=", u"operator >>=", u"operator ->", u"operator ()", u"operator []", u"operator new", u"operator delete", u"operator bool", u"operator int" ]
		self.m_comboBox5 = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_comboBox5Choices, wx.CB_SORT )
		fgSizer15.Add( self.m_comboBox5, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox85 = wx.CheckBox( self, wx.ID_ANY, u"&declare", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox85.SetValue(True) 
		fgSizer15.Add( self.m_checkBox85, 0, wx.ALL, 5 )
		
		self.m_checkBox63 = wx.CheckBox( self, wx.ID_ANY, u"template", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer15.Add( self.m_checkBox63, 0, wx.ALL, 5 )
		
		fgSizer93 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer93.AddGrowableCol( 1 )
		fgSizer93.AddGrowableRow( 0 )
		fgSizer93.SetFlexibleDirection( wx.BOTH )
		fgSizer93.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_stStartTemplate = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stStartTemplate.Wrap( -1 )
		self.m_stStartTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stStartTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_template = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template.Enable( False )
		
		fgSizer93.Add( self.m_template, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_stEndTemplate = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stEndTemplate.Wrap( -1 )
		self.m_stEndTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stEndTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer15.Add( fgSizer93, 1, wx.EXPAND, 5 )
		
		self.m_checkBox86 = wx.CheckBox( self, wx.ID_ANY, u"&implement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox86.SetValue(True) 
		fgSizer15.Add( self.m_checkBox86, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer15, 1, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer97 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer97.AddGrowableCol( 0 )
		fgSizer97.AddGrowableCol( 1 )
		fgSizer97.SetFlexibleDirection( wx.BOTH )
		fgSizer97.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Type" ), wx.VERTICAL )
		
		fgSizer13 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_choice1Choices = []
		self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, wx.CB_SORT|wx.WANTS_CHARS )
		self.m_choice1.SetSelection( 0 )
		fgSizer13.Add( self.m_choice1, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer101 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer101.AddGrowableCol( 1 )
		fgSizer101.SetFlexibleDirection( wx.BOTH )
		fgSizer101.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText65 = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText65.Wrap( -1 )
		self.m_staticText65.Enable( False )
		
		fgSizer101.Add( self.m_staticText65, 0, wx.ALL, 5 )
		
		self.m_template_args = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template_args.Enable( False )
		
		fgSizer101.Add( self.m_template_args, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText66 = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText66.Wrap( -1 )
		self.m_staticText66.Enable( False )
		
		fgSizer101.Add( self.m_staticText66, 0, wx.ALL, 5 )
		
		
		fgSizer13.Add( fgSizer101, 1, wx.EXPAND, 5 )
		
		fgSizer14 = wx.FlexGridSizer( 3, 3, 0, 0 )
		fgSizer14.SetFlexibleDirection( wx.BOTH )
		fgSizer14.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, u"&const", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer14.Add( self.m_checkBox1, 0, wx.ALL, 5 )
		
		self.m_checkBox2 = wx.CheckBox( self, wx.ID_ANY, u"&reference", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer14.Add( self.m_checkBox2, 0, wx.ALL, 5 )
		
		
		fgSizer14.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox3 = wx.CheckBox( self, wx.ID_ANY, u"&pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer14.Add( self.m_checkBox3, 0, wx.ALL, 5 )
		
		self.m_checkBox4 = wx.CheckBox( self, wx.ID_ANY, u"&to pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox4.Enable( False )
		
		fgSizer14.Add( self.m_checkBox4, 0, wx.ALL, 5 )
		
		self.m_checkBox5 = wx.CheckBox( self, wx.ID_ANY, u"c&onst ptr", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox5.Enable( False )
		
		fgSizer14.Add( self.m_checkBox5, 0, wx.ALL, 5 )
		
		
		fgSizer13.Add( fgSizer14, 1, wx.EXPAND, 5 )
		
		
		sbSizer2.Add( fgSizer13, 1, wx.EXPAND, 5 )
		
		
		fgSizer97.Add( sbSizer2, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Properties" ), wx.VERTICAL )
		
		fgSizer20 = wx.FlexGridSizer( 5, 2, 0, 0 )
		fgSizer20.AddGrowableCol( 0 )
		fgSizer20.AddGrowableCol( 1 )
		fgSizer20.SetFlexibleDirection( wx.BOTH )
		fgSizer20.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer20.Add( self.m_staticText8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice2Choices = [ u"public", u"protected", u"private" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		fgSizer20.Add( self.m_choice2, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox61 = wx.CheckBox( self, wx.ID_ANY, u"&calling", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer20.Add( self.m_checkBox61, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		m_comboBox1Choices = [ u"cdecl", u"stdcall", u"fastcall", u"naked" ]
		self.m_comboBox1 = wx.ComboBox( self, wx.ID_ANY, u"cdecl", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
		self.m_comboBox1.Enable( False )
		
		fgSizer20.Add( self.m_comboBox1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox6 = wx.CheckBox( self, wx.ID_ANY, u"&static", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox11 = wx.CheckBox( self, wx.ID_ANY, u"&virtual", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox11, 0, wx.ALL, 5 )
		
		self.m_checkBox21 = wx.CheckBox( self, wx.ID_ANY, u"p&ure", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox21, 0, wx.ALL, 5 )
		
		self.m_checkBox31 = wx.CheckBox( self, wx.ID_ANY, u"&inline", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox31, 0, wx.ALL, 5 )
		
		self.m_checkBox41 = wx.CheckBox( self, wx.ID_ANY, u"co&nst method", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox41, 0, wx.ALL, 5 )
		
		
		sbSizer3.Add( fgSizer20, 1, wx.EXPAND, 5 )
		
		
		fgSizer97.Add( sbSizer3, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer12.Add( fgSizer97, 1, wx.EXPAND, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Notes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer12.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		fgSizer12.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer21.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.SetDefault() 
		fgSizer21.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_checkBox63.Bind( wx.EVT_CHECKBOX, self.OnToggleTemplate )
		self.m_template.Bind( wx.EVT_TEXT, self.OnChangeTemplateSpecification )
		self.m_choice1.Bind( wx.EVT_CHOICE, self.OnTypeChanged )
		self.m_choice1.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_checkBox3.Bind( wx.EVT_CHECKBOX, self.OnPointerToggle )
		self.m_checkBox61.Bind( wx.EVT_CHECKBOX, self.OnCallingToggle )
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnToggleTemplate( self, event ):
		event.Skip()
	
	def OnChangeTemplateSpecification( self, event ):
		event.Skip()
	
	def OnTypeChanged( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	def OnPointerToggle( self, event ):
		event.Skip()
	
	def OnCallingToggle( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyMemberMethod
###########################################################################

class NewPyMemberMethod ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New method", pos = wx.DefaultPosition, size = wx.Size( 453,392 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 5, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 3 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer15 = wx.FlexGridSizer( 2, 3, 0, 0 )
		fgSizer15.AddGrowableCol( 1 )
		fgSizer15.SetFlexibleDirection( wx.BOTH )
		fgSizer15.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"method name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		fgSizer15.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_comboBox5Choices = [ u"__new__", u"__init__", u"__del__", u"__cmp__", u"__eq__", u"__ne__", u"__lt__", u"__gt__", u"__le__", u"__ge__", u"__pos__", u"__neg__", u"__abs__", u"__invert__", u"__round__", u"__floor__", u"__ceil__", u"__trunc__", u"__add__", u"__sub__", u"__mul__", u"__floordiv__", u"__div__", u"__truediv__", u"__mod__", u"__divmod__", u"__pow__", u"__lshift__", u"__rshift__", u"__and__", u"__or__", u"__xor__", u"__radd__", u"__rsub__", u"__rmul__", u"__rfloordiv__", u"__rdiv__", u"__rtruediv__", u"__rmod__", u"__rdivmod__", u"__rpow__", u"__rlshift__", u"__rrshift__", u"__rand__", u"__ror__", u"__rxor__", u"__iadd__", u"__isub__", u"__imul__", u"__ifloordiv__", u"__idiv__", u"__itruediv__", u"__imod__", u"__ipow__", u"__ilshift__", u"__irshift__", u"__iand__", u"__ior__", u"__ixor__", u"__int__", u"__long__", u"__float__", u"__complex__", u"__oct__", u"__hex__", u"__index__", u"__trunc__", u"__coerce__", u"__str__", u"__repr__", u"__unicode__", u"__format__", u"__hash__", u"__nonzero__", u"__dir__", u"__sizeof__", u"__getattr__", u"__setattr__", u"__delattr__", u"__getattribute__", u"__len__", u"__getitem__", u"__setitem__", u"__delitem__", u"__iter__", u"__reversed__", u"__contains__", u"__missing__", u"__call__", u"__enter__", u"__exit__", u"__get__", u"__set__", u"__delete__", u"__copy__", u"__deepcopy__", u"__getinitargs__", u"__getnewargs__", u"__getstate__", u"__setstate__", u"__reduce__", u"__reduce_ex__" ]
		self.m_comboBox5 = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_comboBox5Choices, 0 )
		fgSizer15.Add( self.m_comboBox5, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox86 = wx.CheckBox( self, wx.ID_ANY, u"&implement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox86.SetValue(True) 
		fgSizer15.Add( self.m_checkBox86, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer15, 1, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Properties" ), wx.VERTICAL )
		
		fgSizer20 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer20.AddGrowableCol( 0 )
		fgSizer20.AddGrowableCol( 1 )
		fgSizer20.AddGrowableCol( 2 )
		fgSizer20.SetFlexibleDirection( wx.BOTH )
		fgSizer20.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox6 = wx.CheckBox( self, wx.ID_ANY, u"@&staticmethod", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox21 = wx.CheckBox( self, wx.ID_ANY, u"@&classmethod", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox21, 0, wx.ALL, 5 )
		
		self.m_checkBox41 = wx.CheckBox( self, wx.ID_ANY, u"@&property", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer20.Add( self.m_checkBox41, 0, wx.ALL, 5 )
		
		
		sbSizer3.Add( fgSizer20, 1, wx.EXPAND, 5 )
		
		
		fgSizer12.Add( sbSizer3, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Notes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer12.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		fgSizer12.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer21.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.SetDefault() 
		fgSizer21.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewMethod
###########################################################################

class NewMethod ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New method", pos = wx.DefaultPosition, size = wx.Size( 578,450 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 6, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 3 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer15 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer15.AddGrowableCol( 1 )
		fgSizer15.SetFlexibleDirection( wx.BOTH )
		fgSizer15.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		fgSizer15.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl5 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer15.Add( self.m_textCtrl5, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox63 = wx.CheckBox( self, wx.ID_ANY, u"template", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer15.Add( self.m_checkBox63, 0, wx.ALL, 5 )
		
		fgSizer93 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer93.AddGrowableCol( 1 )
		fgSizer93.AddGrowableRow( 0 )
		fgSizer93.SetFlexibleDirection( wx.BOTH )
		fgSizer93.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_stStartTemplate = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stStartTemplate.Wrap( -1 )
		self.m_stStartTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stStartTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_template = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template.Enable( False )
		
		fgSizer93.Add( self.m_template, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_stEndTemplate = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stEndTemplate.Wrap( -1 )
		self.m_stEndTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stEndTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer15.Add( fgSizer93, 1, wx.EXPAND, 5 )
		
		
		fgSizer12.Add( fgSizer15, 1, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer97 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer97.AddGrowableCol( 1 )
		fgSizer97.SetFlexibleDirection( wx.BOTH )
		fgSizer97.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Type" ), wx.VERTICAL )
		
		fgSizer13 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_choice1Choices = []
		self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, wx.CB_SORT|wx.WANTS_CHARS )
		self.m_choice1.SetSelection( 0 )
		fgSizer13.Add( self.m_choice1, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer101 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer101.AddGrowableCol( 1 )
		fgSizer101.SetFlexibleDirection( wx.BOTH )
		fgSizer101.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText65 = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText65.Wrap( -1 )
		self.m_staticText65.Enable( False )
		
		fgSizer101.Add( self.m_staticText65, 0, wx.ALL, 5 )
		
		self.m_template_args = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template_args.Enable( False )
		
		fgSizer101.Add( self.m_template_args, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText66 = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText66.Wrap( -1 )
		self.m_staticText66.Enable( False )
		
		fgSizer101.Add( self.m_staticText66, 0, wx.ALL, 5 )
		
		
		fgSizer13.Add( fgSizer101, 1, wx.EXPAND, 5 )
		
		fgSizer14 = wx.FlexGridSizer( 2, 3, 0, 0 )
		fgSizer14.SetFlexibleDirection( wx.BOTH )
		fgSizer14.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, u"&const", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer14.Add( self.m_checkBox1, 0, wx.ALL, 5 )
		
		self.m_checkBox2 = wx.CheckBox( self, wx.ID_ANY, u"&reference", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer14.Add( self.m_checkBox2, 0, wx.ALL, 5 )
		
		self.m_checkBox3 = wx.CheckBox( self, wx.ID_ANY, u"&pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer14.Add( self.m_checkBox3, 0, wx.ALL, 5 )
		
		self.m_checkBox4 = wx.CheckBox( self, wx.ID_ANY, u"&to pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox4.Enable( False )
		
		fgSizer14.Add( self.m_checkBox4, 0, wx.ALL, 5 )
		
		self.m_checkBox5 = wx.CheckBox( self, wx.ID_ANY, u"c&onst ptr", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox5.Enable( False )
		
		fgSizer14.Add( self.m_checkBox5, 0, wx.ALL, 5 )
		
		
		fgSizer13.Add( fgSizer14, 1, wx.EXPAND, 5 )
		
		
		sbSizer2.Add( fgSizer13, 1, wx.EXPAND, 5 )
		
		
		fgSizer97.Add( sbSizer2, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Properties" ), wx.VERTICAL )
		
		fgSizer20 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer20.AddGrowableCol( 0 )
		fgSizer20.AddGrowableCol( 1 )
		fgSizer20.AddGrowableRow( 0 )
		fgSizer20.AddGrowableRow( 2 )
		fgSizer20.SetFlexibleDirection( wx.BOTH )
		fgSizer20.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox6 = wx.CheckBox( self, wx.ID_ANY, u"&static", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer20.Add( self.m_checkBox6, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT, 5 )
		
		self.m_checkBox31 = wx.CheckBox( self, wx.ID_ANY, u"&inline", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer20.Add( self.m_checkBox31, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )
		
		self.m_checkBox61 = wx.CheckBox( self, wx.ID_ANY, u"&calling", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer20.Add( self.m_checkBox61, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		m_comboBox1Choices = [ u"cdecl", u"stdcall", u"fastcall", u"naked" ]
		self.m_comboBox1 = wx.ComboBox( self, wx.ID_ANY, u"cdecl", wx.DefaultPosition, wx.DefaultSize, m_comboBox1Choices, 0 )
		self.m_comboBox1.Enable( False )
		
		fgSizer20.Add( self.m_comboBox1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer20.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		sbSizer3.Add( fgSizer20, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5 )
		
		
		fgSizer97.Add( sbSizer3, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer12.Add( fgSizer97, 1, wx.EXPAND, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Notes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer12.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		fgSizer12.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer21.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.SetDefault() 
		fgSizer21.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_checkBox63.Bind( wx.EVT_CHECKBOX, self.OnToggleTemplate )
		self.m_template.Bind( wx.EVT_TEXT, self.OnChangeTemplateSpecification )
		self.m_choice1.Bind( wx.EVT_CHOICE, self.OnTypeChanged )
		self.m_choice1.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_checkBox3.Bind( wx.EVT_CHECKBOX, self.OnPointerToggle )
		self.m_checkBox61.Bind( wx.EVT_CHECKBOX, self.OnCallingToggle )
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnToggleTemplate( self, event ):
		event.Skip()
	
	def OnChangeTemplateSpecification( self, event ):
		event.Skip()
	
	def OnTypeChanged( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	def OnPointerToggle( self, event ):
		event.Skip()
	
	def OnCallingToggle( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyMethod
###########################################################################

class NewPyMethod ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New method", pos = wx.DefaultPosition, size = wx.Size( 578,450 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer12 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer12.AddGrowableCol( 0 )
		fgSizer12.AddGrowableRow( 2 )
		fgSizer12.SetFlexibleDirection( wx.BOTH )
		fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer15 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer15.AddGrowableCol( 1 )
		fgSizer15.SetFlexibleDirection( wx.BOTH )
		fgSizer15.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		fgSizer15.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl5 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer15.Add( self.m_textCtrl5, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox86 = wx.CheckBox( self, wx.ID_ANY, u"&implement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox86.SetValue(True) 
		fgSizer15.Add( self.m_checkBox86, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer15, 1, wx.EXPAND|wx.ALL, 5 )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Notes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer12.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		fgSizer12.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		fgSizer21 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer21.Add( self.m_info, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_button2 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button2.SetDefault() 
		fgSizer21.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		fgSizer12.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer12 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewModule
###########################################################################

class NewModule ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New module", pos = wx.DefaultPosition, size = wx.Size( 325,204 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer106 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer106.AddGrowableCol( 0 )
		fgSizer106.AddGrowableRow( 0 )
		fgSizer106.SetFlexibleDirection( wx.BOTH )
		fgSizer106.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer40 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.HORIZONTAL )
		
		fgSizer108 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer108.AddGrowableCol( 1 )
		fgSizer108.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer108.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText98 = wx.StaticText( self, wx.ID_ANY, u"Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText98.Wrap( -1 )
		fgSizer108.Add( self.m_staticText98, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_moduleName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer108.Add( self.m_moduleName, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_staticText70 = wx.StaticText( self, wx.ID_ANY, u"Header:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText70.Wrap( -1 )
		fgSizer108.Add( self.m_staticText70, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		self.m_choiceHeader = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer108.Add( self.m_choiceHeader, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		self.m_staticText71 = wx.StaticText( self, wx.ID_ANY, u"Source:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText71.Wrap( -1 )
		fgSizer108.Add( self.m_staticText71, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		self.m_choiceSource = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer108.Add( self.m_choiceSource, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		
		sbSizer40.Add( fgSizer108, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer106.Add( sbSizer40, 1, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer157 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer157.AddGrowableCol( 1 )
		fgSizer157.SetFlexibleDirection( wx.BOTH )
		fgSizer157.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer157.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer9 = wx.StdDialogButtonSizer()
		self.m_sdbSizer9OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer9.AddButton( self.m_sdbSizer9OK )
		self.m_sdbSizer9Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer9.AddButton( self.m_sdbSizer9Cancel )
		m_sdbSizer9.Realize();
		
		fgSizer157.Add( m_sdbSizer9, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )
		
		
		fgSizer106.Add( fgSizer157, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer106 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer9OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

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
## Class NewPyPackage
###########################################################################

class NewPyPackage ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New package", pos = wx.DefaultPosition, size = wx.Size( 380,320 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer106 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer106.AddGrowableCol( 0 )
		fgSizer106.AddGrowableRow( 1 )
		fgSizer106.SetFlexibleDirection( wx.BOTH )
		fgSizer106.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer40 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.HORIZONTAL )
		
		fgSizer108 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer108.AddGrowableCol( 1 )
		fgSizer108.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer108.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText98 = wx.StaticText( self, wx.ID_ANY, u"Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText98.Wrap( -1 )
		fgSizer108.Add( self.m_staticText98, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_package_name = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer108.Add( self.m_package_name, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		sbSizer40.Add( fgSizer108, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer106.Add( sbSizer40, 1, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer106.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
		fgSizer157 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer157.AddGrowableCol( 1 )
		fgSizer157.SetFlexibleDirection( wx.BOTH )
		fgSizer157.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer157.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer9 = wx.StdDialogButtonSizer()
		self.m_sdbSizer9OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer9.AddButton( self.m_sdbSizer9OK )
		self.m_sdbSizer9Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer9.AddButton( self.m_sdbSizer9Cancel )
		m_sdbSizer9.Realize();
		
		fgSizer157.Add( m_sdbSizer9, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )
		
		
		fgSizer106.Add( fgSizer157, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer106 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer9Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer9OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyModule
###########################################################################

class NewPyModule ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New module", pos = wx.DefaultPosition, size = wx.Size( 401,261 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer106 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer106.AddGrowableCol( 0 )
		fgSizer106.AddGrowableRow( 1 )
		fgSizer106.SetFlexibleDirection( wx.BOTH )
		fgSizer106.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer40 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.HORIZONTAL )
		
		fgSizer108 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer108.AddGrowableCol( 1 )
		fgSizer108.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer108.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText98 = wx.StaticText( self, wx.ID_ANY, u"Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText98.Wrap( -1 )
		fgSizer108.Add( self.m_staticText98, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_moduleName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer108.Add( self.m_moduleName, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		sbSizer40.Add( fgSizer108, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer106.Add( sbSizer40, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"notes" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer106.Add( sbSizer6, 1, wx.EXPAND, 5 )
		
		fgSizer157 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer157.AddGrowableCol( 1 )
		fgSizer157.SetFlexibleDirection( wx.BOTH )
		fgSizer157.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer157.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer9 = wx.StdDialogButtonSizer()
		self.m_sdbSizer9OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer9.AddButton( self.m_sdbSizer9OK )
		self.m_sdbSizer9Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer9.AddButton( self.m_sdbSizer9Cancel )
		m_sdbSizer9.Realize();
		
		fgSizer157.Add( m_sdbSizer9, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )
		
		
		fgSizer106.Add( fgSizer157, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer106 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer9OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewNamespace
###########################################################################

class NewNamespace ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New namespace", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
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
		
		fgSizer163 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer163.AddGrowableCol( 1 )
		fgSizer163.SetFlexibleDirection( wx.BOTH )
		fgSizer163.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer163.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
		self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
		m_sdbSizer2.Realize();
		
		fgSizer163.Add( m_sdbSizer2, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		
		fgSizer6.Add( fgSizer163, 1, wx.EXPAND, 5 )
		
		
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
## Class NewRelation
###########################################################################

class NewRelation ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New relation", pos = wx.DefaultPosition, size = wx.Size( 589,599 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer29 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer29.AddGrowableCol( 0 )
		fgSizer29.AddGrowableRow( 2 )
		fgSizer29.SetFlexibleDirection( wx.BOTH )
		fgSizer29.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer44 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer44.AddGrowableCol( 0 )
		fgSizer44.AddGrowableCol( 1 )
		fgSizer44.SetFlexibleDirection( wx.BOTH )
		fgSizer44.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"From " ), wx.VERTICAL )
		
		fgSizer34 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer34.AddGrowableCol( 0 )
		fgSizer34.SetFlexibleDirection( wx.BOTH )
		fgSizer34.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer30 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer30.AddGrowableCol( 1 )
		fgSizer30.SetFlexibleDirection( wx.BOTH )
		fgSizer30.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"class", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		fgSizer30.Add( self.m_staticText12, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice4Choices = []
		self.m_choice4 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), m_choice4Choices, 0 )
		self.m_choice4.SetSelection( 0 )
		fgSizer30.Add( self.m_choice4, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"alias", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )
		fgSizer30.Add( self.m_staticText13, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl10 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer30.Add( self.m_textCtrl10, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )
		fgSizer30.Add( self.m_staticText29, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		m_choice12Choices = [ u"public", u"protected", u"private" ]
		self.m_choice12 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice12Choices, 0 )
		self.m_choice12.SetSelection( 0 )
		fgSizer30.Add( self.m_choice12, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer34.Add( fgSizer30, 1, wx.EXPAND, 5 )
		
		fgSizer35 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer35.AddGrowableCol( 0 )
		fgSizer35.AddGrowableCol( 1 )
		fgSizer35.SetFlexibleDirection( wx.BOTH )
		fgSizer35.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_chkMinCardFrom = wx.CheckBox( self, wx.ID_ANY, u"M&in cardinal:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_chkMinCardFrom.SetValue(True) 
		fgSizer35.Add( self.m_chkMinCardFrom, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_minFrom = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0|wx.RAISED_BORDER )
		fgSizer35.Add( self.m_minFrom, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_chkMaxCardFrom = wx.CheckBox( self, wx.ID_ANY, u"M&ax cardinal:", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer35.Add( self.m_chkMaxCardFrom, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_maxFrom = wx.TextCtrl( self, wx.ID_ANY, u"infinity", wx.DefaultPosition, wx.DefaultSize, 0|wx.RAISED_BORDER )
		self.m_maxFrom.Enable( False )
		
		fgSizer35.Add( self.m_maxFrom, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer34.Add( fgSizer35, 1, wx.EXPAND, 5 )
		
		
		sbSizer6.Add( fgSizer34, 1, wx.EXPAND, 5 )
		
		
		fgSizer44.Add( sbSizer6, 1, wx.EXPAND|wx.TOP, 5 )
		
		sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"To " ), wx.VERTICAL )
		
		fgSizer341 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer341.AddGrowableCol( 0 )
		fgSizer341.SetFlexibleDirection( wx.BOTH )
		fgSizer341.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer301 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer301.AddGrowableCol( 1 )
		fgSizer301.SetFlexibleDirection( wx.BOTH )
		fgSizer301.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText121 = wx.StaticText( self, wx.ID_ANY, u"class", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText121.Wrap( -1 )
		fgSizer301.Add( self.m_staticText121, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice41Choices = []
		self.m_choice41 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice41Choices, 0 )
		self.m_choice41.SetSelection( 0 )
		fgSizer301.Add( self.m_choice41, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText131 = wx.StaticText( self, wx.ID_ANY, u"alias", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText131.Wrap( -1 )
		fgSizer301.Add( self.m_staticText131, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl101 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer301.Add( self.m_textCtrl101, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )
		fgSizer301.Add( self.m_staticText30, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		m_choice121Choices = [ u"public", u"protected", u"private" ]
		self.m_choice121 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice121Choices, 0 )
		self.m_choice121.SetSelection( 0 )
		fgSizer301.Add( self.m_choice121, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer341.Add( fgSizer301, 1, wx.EXPAND, 5 )
		
		fgSizer351 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer351.AddGrowableCol( 0 )
		fgSizer351.AddGrowableCol( 1 )
		fgSizer351.SetFlexibleDirection( wx.BOTH )
		fgSizer351.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_chkMinCardTo = wx.CheckBox( self, wx.ID_ANY, u"Min cardinal:", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer351.Add( self.m_chkMinCardTo, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_minTo = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0|wx.RAISED_BORDER )
		self.m_minTo.Enable( False )
		
		fgSizer351.Add( self.m_minTo, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_chkMaxCardTo = wx.CheckBox( self, wx.ID_ANY, u"Ma&x cardinal:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_chkMaxCardTo.SetValue(True) 
		fgSizer351.Add( self.m_chkMaxCardTo, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_maxTo = wx.TextCtrl( self, wx.ID_ANY, u"infinity", wx.DefaultPosition, wx.DefaultSize, 0|wx.RAISED_BORDER )
		fgSizer351.Add( self.m_maxTo, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		fgSizer341.Add( fgSizer351, 1, wx.EXPAND, 5 )
		
		
		sbSizer7.Add( fgSizer341, 1, wx.EXPAND, 5 )
		
		
		fgSizer44.Add( sbSizer7, 1, wx.EXPAND|wx.TOP, 5 )
		
		
		fgSizer29.Add( fgSizer44, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Properties" ), wx.VERTICAL )
		
		fgSizer45 = wx.FlexGridSizer( 2, 4, 0, 0 )
		fgSizer45.AddGrowableCol( 3 )
		fgSizer45.AddGrowableRow( 0 )
		fgSizer45.AddGrowableRow( 1 )
		fgSizer45.SetFlexibleDirection( wx.BOTH )
		fgSizer45.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox23 = wx.CheckBox( self, wx.ID_ANY, u"&Critical", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer45.Add( self.m_checkBox23, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox24 = wx.CheckBox( self, wx.ID_ANY, u"&Filter", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer45.Add( self.m_checkBox24, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox25 = wx.CheckBox( self, wx.ID_ANY, u"&Unique", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer45.Add( self.m_checkBox25, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		m_memberChoices = []
		self.m_member = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_memberChoices, 0 )
		self.m_member.SetSelection( 0 )
		self.m_member.Enable( False )
		
		fgSizer45.Add( self.m_member, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox47 = wx.CheckBox( self, wx.ID_ANY, u"&Global", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer45.Add( self.m_checkBox47, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer45.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText49 = wx.StaticText( self, wx.ID_ANY, u"Implementation", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText49.Wrap( -1 )
		fgSizer45.Add( self.m_staticText49, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_choice19Choices = [ u"native" ]
		self.m_choice19 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice19Choices, 0 )
		self.m_choice19.SetSelection( 0 )
		fgSizer45.Add( self.m_choice19, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sbSizer8.Add( fgSizer45, 1, wx.EXPAND, 5 )
		
		
		fgSizer29.Add( sbSizer8, 1, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer29.Add( sbSizer9, 1, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer43 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer43.AddGrowableCol( 0 )
		fgSizer43.SetFlexibleDirection( wx.BOTH )
		fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer43.Add( self.m_info, 0, wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_button8 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer43.Add( self.m_button8, 0, wx.ALL, 5 )
		
		self.m_button7 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button7.SetDefault() 
		fgSizer43.Add( self.m_button7, 0, wx.ALL, 5 )
		
		
		fgSizer29.Add( fgSizer43, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer29 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_choice4.Bind( wx.EVT_CHOICE, self.OnChangeFrom )
		self.m_chkMinCardFrom.Bind( wx.EVT_CHECKBOX, self.OnMinCardinalFrom )
		self.m_chkMaxCardFrom.Bind( wx.EVT_CHECKBOX, self.OnMaxCardinalFrom )
		self.m_choice41.Bind( wx.EVT_CHOICE, self.OnChangeTo )
		self.m_chkMinCardTo.Bind( wx.EVT_CHECKBOX, self.OnMinCardinalTo )
		self.m_chkMaxCardTo.Bind( wx.EVT_CHECKBOX, self.OnMaxCardinalTo )
		self.m_checkBox25.Bind( wx.EVT_CHECKBOX, self.OnUnique )
		self.m_checkBox47.Bind( wx.EVT_CHECKBOX, self.OnGlobal )
		self.m_button7.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnChangeFrom( self, event ):
		event.Skip()
	
	def OnMinCardinalFrom( self, event ):
		event.Skip()
	
	def OnMaxCardinalFrom( self, event ):
		event.Skip()
	
	def OnChangeTo( self, event ):
		event.Skip()
	
	def OnMinCardinalTo( self, event ):
		event.Skip()
	
	def OnMaxCardinalTo( self, event ):
		event.Skip()
	
	def OnUnique( self, event ):
		event.Skip()
	
	def OnGlobal( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewType
###########################################################################

class NewType ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New type", pos = wx.DefaultPosition, size = wx.Size( 546,483 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer6 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.AddGrowableRow( 1 )
		fgSizer6.AddGrowableRow( 2 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer7 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.AddGrowableRow( 0 )
		fgSizer7.AddGrowableRow( 1 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer7.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textCtrl2, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_checkBoxTemplate = wx.CheckBox( self, wx.ID_ANY, u"template", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_checkBoxTemplate, 0, wx.ALL, 5 )
		
		fgSizer93 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer93.AddGrowableCol( 1 )
		fgSizer93.AddGrowableRow( 0 )
		fgSizer93.SetFlexibleDirection( wx.BOTH )
		fgSizer93.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_stStartTemplate = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stStartTemplate.Wrap( -1 )
		self.m_stStartTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stStartTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_template = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template.Enable( False )
		
		fgSizer93.Add( self.m_template, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_stEndTemplate = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stEndTemplate.Wrap( -1 )
		self.m_stEndTemplate.Enable( False )
		
		fgSizer93.Add( self.m_stEndTemplate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer7.Add( fgSizer93, 1, wx.EXPAND, 5 )
		
		self.m_accessLb = wx.StaticText( self, wx.ID_ANY, u"access", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_accessLb.Wrap( -1 )
		self.m_accessLb.Enable( False )
		
		fgSizer7.Add( self.m_accessLb, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_accessChoices = [ u"public", u"protected", u"private" ]
		self.m_access = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_accessChoices, 0 )
		self.m_access.SetSelection( 0 )
		self.m_access.Enable( False )
		
		fgSizer7.Add( self.m_access, 0, wx.ALL, 5 )
		
		
		fgSizer6.Add( fgSizer7, 0, wx.EXPAND|wx.ALL, 5 )
		
		sbSizer20 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Declaration" ), wx.VERTICAL )
		
		self.m_richText2 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer20.Add( self.m_richText2, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer6.Add( sbSizer20, 1, wx.EXPAND, 5 )
		
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Documentation" ), wx.VERTICAL )
		
		self.m_richText3 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SUNKEN_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer9.Add( self.m_richText3, 1, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer6.Add( sbSizer9, 1, wx.EXPAND, 5 )
		
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
		
		
		fgSizer6.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_checkBoxTemplate.Bind( wx.EVT_CHECKBOX, self.OnToggleTemplate )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnToggleTemplate( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewVariable
###########################################################################

class NewVariable ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New variable", pos = wx.DefaultPosition, size = wx.Size( 483,409 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer23 = wx.FlexGridSizer( 5, 1, 0, 0 )
		fgSizer23.AddGrowableCol( 0 )
		fgSizer23.AddGrowableRow( 2 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer24 = wx.FlexGridSizer( 2, 5, 0, 0 )
		fgSizer24.AddGrowableCol( 1 )
		fgSizer24.AddGrowableCol( 3 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer24.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl6 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SUNKEN_BORDER )
		fgSizer24.Add( self.m_textCtrl6, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT, 5 )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"=", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer24.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer24.Add( self.m_textCtrl8, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5 )
		
		
		fgSizer24.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		fgSizer24.Add( self.m_staticText10, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		m_choice1Choices = []
		self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, wx.CB_SORT|wx.WANTS_CHARS )
		self.m_choice1.SetSelection( 0 )
		fgSizer24.Add( self.m_choice1, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText67 = wx.StaticText( self, wx.ID_ANY, u"<", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText67.Wrap( -1 )
		self.m_staticText67.Enable( False )
		
		fgSizer24.Add( self.m_staticText67, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_template_args = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_template_args.Enable( False )
		
		fgSizer24.Add( self.m_template_args, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.m_staticText68 = wx.StaticText( self, wx.ID_ANY, u">", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText68.Wrap( -1 )
		self.m_staticText68.Enable( False )
		
		fgSizer24.Add( self.m_staticText68, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer23.Add( fgSizer24, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"properties" ), wx.VERTICAL )
		
		fgSizer25 = wx.FlexGridSizer( 3, 4, 0, 0 )
		fgSizer25.SetFlexibleDirection( wx.BOTH )
		fgSizer25.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_checkBox105 = wx.CheckBox( self, wx.ID_ANY, u"&static", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox105, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox13 = wx.CheckBox( self, wx.ID_ANY, u"&pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox13, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox11 = wx.CheckBox( self, wx.ID_ANY, u"&const", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox11, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox12 = wx.CheckBox( self, wx.ID_ANY, u"&reference", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox12, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_checkBox49 = wx.CheckBox( self, wx.ID_ANY, u"&volatile", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox49, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox14 = wx.CheckBox( self, wx.ID_ANY, u"c&onst pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox14.Enable( False )
		
		fgSizer25.Add( self.m_checkBox14, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox50 = wx.CheckBox( self, wx.ID_ANY, u"vo&latile pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox50.Enable( False )
		
		fgSizer25.Add( self.m_checkBox50, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_checkBox15 = wx.CheckBox( self, wx.ID_ANY, u"po&inter/pointer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox15.Enable( False )
		
		fgSizer25.Add( self.m_checkBox15, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer25.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox17 = wx.CheckBox( self, wx.ID_ANY, u"a&rray", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer25.Add( self.m_checkBox17, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl7 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textCtrl7.Enable( False )
		self.m_textCtrl7.Hide()
		
		fgSizer25.Add( self.m_textCtrl7, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer25.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		sbSizer5.Add( fgSizer25, 1, wx.EXPAND, 5 )
		
		
		fgSizer23.Add( sbSizer5, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"notes" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer23.Add( sbSizer6, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer23.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer23 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_choice1.Bind( wx.EVT_CHOICE, self.OnTypeChanged )
		self.m_choice1.Bind( wx.EVT_KEY_DOWN, self.OnKeyDown )
		self.m_checkBox105.Bind( wx.EVT_CHECKBOX, self.OnToggleStatic )
		self.m_checkBox13.Bind( wx.EVT_CHECKBOX, self.OnPointerToggle )
		self.m_checkBox17.Bind( wx.EVT_CHECKBOX, self.OnToggleArray )
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnTypeChanged( self, event ):
		event.Skip()
	
	def OnKeyDown( self, event ):
		event.Skip()
	
	def OnToggleStatic( self, event ):
		event.Skip()
	
	def OnPointerToggle( self, event ):
		event.Skip()
	
	def OnToggleArray( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewPyVariable
###########################################################################

class NewPyVariable ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New variable", pos = wx.DefaultPosition, size = wx.Size( 483,409 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer23 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer23.AddGrowableCol( 0 )
		fgSizer23.AddGrowableRow( 1 )
		fgSizer23.SetFlexibleDirection( wx.BOTH )
		fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer24 = wx.FlexGridSizer( 1, 5, 0, 0 )
		fgSizer24.AddGrowableCol( 1 )
		fgSizer24.AddGrowableCol( 3 )
		fgSizer24.SetFlexibleDirection( wx.BOTH )
		fgSizer24.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		fgSizer24.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl6 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.SUNKEN_BORDER )
		fgSizer24.Add( self.m_textCtrl6, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT, 5 )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"=", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer24.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrl8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer24.Add( self.m_textCtrl8, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5 )
		
		self.m_checkBox86 = wx.CheckBox( self, wx.ID_ANY, u"&implement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox86.SetValue(True) 
		fgSizer24.Add( self.m_checkBox86, 0, wx.ALL, 5 )
		
		
		fgSizer23.Add( fgSizer24, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"notes" ), wx.VERTICAL )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		sbSizer6.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		fgSizer23.Add( sbSizer6, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer23.Add( fgSizer22, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer23 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_button6.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class SelectClasses
###########################################################################

class SelectClasses ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Select Classes", pos = wx.DefaultPosition, size = wx.Size( 551,217 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer63 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer63.AddGrowableCol( 0 )
		fgSizer63.AddGrowableRow( 1 )
		fgSizer63.SetFlexibleDirection( wx.BOTH )
		fgSizer63.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.NO_BORDER )
		fgSizer63.Add( self.m_info, 0, wx.ALIGN_RIGHT, 5 )
		
		m_classChecklistChoices = []
		self.m_classChecklist = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_classChecklistChoices, 0 )
		fgSizer63.Add( self.m_classChecklist, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer64 = wx.FlexGridSizer( 1, 3, 0, 0 )
		fgSizer64.AddGrowableCol( 0 )
		fgSizer64.SetFlexibleDirection( wx.BOTH )
		fgSizer64.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer64.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_button21 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer64.Add( self.m_button21, 0, wx.ALL, 5 )
		
		self.m_button22 = wx.Button( self, wx.ID_OK, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button22.SetDefault() 
		fgSizer64.Add( self.m_button22, 0, wx.ALL, 5 )
		
		
		fgSizer63.Add( fgSizer64, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer63 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_INIT_DIALOG, self.OnInitDialog )
		self.m_button22.Bind( wx.EVT_BUTTON, self.OnOk )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnInitDialog( self, event ):
		event.Skip()
	
	def OnOk( self, event ):
		event.Skip()
	

###########################################################################
## Class SelectContexts
###########################################################################

class SelectContexts ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Select contexts", pos = wx.DefaultPosition, size = wx.Size( 466,420 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer126 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer126.AddGrowableCol( 0 )
		fgSizer126.AddGrowableRow( 0 )
		fgSizer126.SetFlexibleDirection( wx.BOTH )
		fgSizer126.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer127 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer127.AddGrowableCol( 0 )
		fgSizer127.AddGrowableRow( 0 )
		fgSizer127.SetFlexibleDirection( wx.BOTH )
		fgSizer127.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer128 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer128.AddGrowableCol( 0 )
		fgSizer128.AddGrowableCol( 1 )
		fgSizer128.AddGrowableRow( 0 )
		fgSizer128.SetFlexibleDirection( wx.BOTH )
		fgSizer128.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer37 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Available contexts" ), wx.VERTICAL )
		
		self.m_listCtrl5 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
		sbSizer37.Add( self.m_listCtrl5, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer128.Add( sbSizer37, 1, wx.EXPAND, 5 )
		
		sbSizer38 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Assigned contexts" ), wx.VERTICAL )
		
		self.m_listCtrl4 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
		sbSizer38.Add( self.m_listCtrl4, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer128.Add( sbSizer38, 1, wx.EXPAND, 5 )
		
		
		fgSizer127.Add( fgSizer128, 1, wx.EXPAND, 5 )
		
		fgSizer129 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer129.AddGrowableCol( 0 )
		fgSizer129.AddGrowableRow( 2 )
		fgSizer129.SetFlexibleDirection( wx.BOTH )
		fgSizer129.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_button31 = wx.Button( self, wx.ID_ANY, u"Move up", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button31.Enable( False )
		
		fgSizer129.Add( self.m_button31, 0, wx.ALL, 5 )
		
		self.m_button32 = wx.Button( self, wx.ID_ANY, u"Move down", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button32.Enable( False )
		
		fgSizer129.Add( self.m_button32, 0, wx.ALL, 5 )
		
		
		fgSizer127.Add( fgSizer129, 1, wx.EXPAND, 5 )
		
		
		fgSizer126.Add( fgSizer127, 1, wx.EXPAND, 5 )
		
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
		
		
		fgSizer126.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer126 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_listCtrl5.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.OnAddContext )
		self.m_listCtrl4.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.OnRemoveContext )
		self.m_listCtrl4.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnSelectAssigned )
		self.m_button31.Bind( wx.EVT_BUTTON, self.OnMoveUp )
		self.m_button32.Bind( wx.EVT_BUTTON, self.OnMoveDown )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnAddContext( self, event ):
		event.Skip()
	
	def OnRemoveContext( self, event ):
		event.Skip()
	
	def OnSelectAssigned( self, event ):
		event.Skip()
	
	def OnMoveUp( self, event ):
		event.Skip()
	
	def OnMoveDown( self, event ):
		event.Skip()
	

###########################################################################
## Class IsClassMethods
###########################################################################

class IsClassMethods ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"is_class methods", pos = wx.DefaultPosition, size = wx.Size( 441,320 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer154 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer154.AddGrowableCol( 0 )
		fgSizer154.AddGrowableRow( 0 )
		fgSizer154.SetFlexibleDirection( wx.BOTH )
		fgSizer154.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_checkList2Choices = []
		self.m_checkList2 = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList2Choices, 0 )
		fgSizer154.Add( self.m_checkList2, 0, wx.ALL|wx.EXPAND, 5 )
		
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
		
		
		fgSizer154.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer154 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class VirtualMethods
###########################################################################

class VirtualMethods ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"virtual methods", pos = wx.DefaultPosition, size = wx.Size( 441,320 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer154 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer154.AddGrowableCol( 0 )
		fgSizer154.AddGrowableRow( 0 )
		fgSizer154.SetFlexibleDirection( wx.BOTH )
		fgSizer154.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_checkList2Choices = []
		self.m_checkList2 = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList2Choices, 0 )
		fgSizer154.Add( self.m_checkList2, 0, wx.ALL|wx.EXPAND, 5 )
		
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
		
		
		fgSizer154.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer154 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class SelectFriends
###########################################################################

class SelectFriends ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"select friends", pos = wx.DefaultPosition, size = wx.Size( 441,320 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer154 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer154.AddGrowableCol( 0 )
		fgSizer154.AddGrowableRow( 0 )
		fgSizer154.SetFlexibleDirection( wx.BOTH )
		fgSizer154.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		m_checkList2Choices = []
		self.m_checkList2 = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkList2Choices, 0 )
		fgSizer154.Add( self.m_checkList2, 0, wx.ALL|wx.EXPAND, 5 )
		
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
		
		
		fgSizer154.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer154 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class UserSections
###########################################################################

class UserSections ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"user sections", pos = wx.DefaultPosition, size = wx.Size( 764,423 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer158 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer158.AddGrowableCol( 0 )
		fgSizer158.AddGrowableRow( 0 )
		fgSizer158.SetFlexibleDirection( wx.BOTH )
		fgSizer158.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_choicebook3 = wx.Choicebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel22 = wx.Panel( self.m_choicebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer162 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer162.AddGrowableCol( 0 )
		fgSizer162.AddGrowableRow( 0 )
		fgSizer162.SetFlexibleDirection( wx.BOTH )
		fgSizer162.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		import app.ui.ctrl.Editor as Editor
		self.m_h1 = Editor(self.m_panel22)
		fgSizer162.Add( self.m_h1, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel22.SetSizer( fgSizer162 )
		self.m_panel22.Layout()
		fgSizer162.Fit( self.m_panel22 )
		self.m_choicebook3.AddPage( self.m_panel22, u"before class declaration", False )
		self.m_panel23 = wx.Panel( self.m_choicebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1621 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer1621.AddGrowableCol( 0 )
		fgSizer1621.AddGrowableRow( 0 )
		fgSizer1621.SetFlexibleDirection( wx.BOTH )
		fgSizer1621.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_h2 = Editor(self.m_panel23) 
		fgSizer1621.Add( self.m_h2, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel23.SetSizer( fgSizer1621 )
		self.m_panel23.Layout()
		fgSizer1621.Fit( self.m_panel23 )
		self.m_choicebook3.AddPage( self.m_panel23, u"inside class declaration", False )
		self.m_panel24 = wx.Panel( self.m_choicebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1622 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer1622.AddGrowableCol( 0 )
		fgSizer1622.AddGrowableRow( 0 )
		fgSizer1622.SetFlexibleDirection( wx.BOTH )
		fgSizer1622.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_h3 = Editor(self.m_panel24) 
		fgSizer1622.Add( self.m_h3, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel24.SetSizer( fgSizer1622 )
		self.m_panel24.Layout()
		fgSizer1622.Fit( self.m_panel24 )
		self.m_choicebook3.AddPage( self.m_panel24, u"after class declaration", False )
		self.m_panel25 = wx.Panel( self.m_choicebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1623 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer1623.AddGrowableCol( 0 )
		fgSizer1623.AddGrowableRow( 0 )
		fgSizer1623.SetFlexibleDirection( wx.BOTH )
		fgSizer1623.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_s1 = Editor(self.m_panel25) 
		fgSizer1623.Add( self.m_s1, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel25.SetSizer( fgSizer1623 )
		self.m_panel25.Layout()
		fgSizer1623.Fit( self.m_panel25 )
		self.m_choicebook3.AddPage( self.m_panel25, u"before implementation includes", False )
		self.m_panel26 = wx.Panel( self.m_choicebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1624 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer1624.AddGrowableCol( 0 )
		fgSizer1624.AddGrowableRow( 0 )
		fgSizer1624.SetFlexibleDirection( wx.BOTH )
		fgSizer1624.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_s2 = Editor(self.m_panel26) 
		fgSizer1624.Add( self.m_s2, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel26.SetSizer( fgSizer1624 )
		self.m_panel26.Layout()
		fgSizer1624.Fit( self.m_panel26 )
		self.m_choicebook3.AddPage( self.m_panel26, u"before implementation", False )
		self.m_panel27 = wx.Panel( self.m_choicebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1625 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer1625.AddGrowableCol( 0 )
		fgSizer1625.AddGrowableRow( 0 )
		fgSizer1625.SetFlexibleDirection( wx.BOTH )
		fgSizer1625.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_s3 = Editor(self.m_panel27) 
		fgSizer1625.Add( self.m_s3, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel27.SetSizer( fgSizer1625 )
		self.m_panel27.Layout()
		fgSizer1625.Fit( self.m_panel27 )
		self.m_choicebook3.AddPage( self.m_panel27, u"after implementation", False )
		fgSizer158.Add( self.m_choicebook3, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
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
		
		
		fgSizer158.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer158 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_h1.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_h1.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
		self.m_h2.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_h2.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
		self.m_h3.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_h3.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
		self.m_s1.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_s1.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
		self.m_s2.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_s2.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
		self.m_s3.Bind( wx.EVT_KILL_FOCUS, self.OnLeaveFocus )
		self.m_s3.Bind( wx.EVT_SET_FOCUS, self.OnGetFocus )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnLeaveFocus( self, event ):
		event.Skip()
	
	def OnGetFocus( self, event ):
		event.Skip()
	
	
	
	
	
	
	
	
	
	
	

###########################################################################
## Class SelectLibraries
###########################################################################

class SelectLibraries ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Select libraries  ...", pos = wx.DefaultPosition, size = wx.Size( 383,351 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer178 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer178.AddGrowableCol( 0 )
		fgSizer178.AddGrowableRow( 0 )
		fgSizer178.SetFlexibleDirection( wx.BOTH )
		fgSizer178.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
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
		self.m_choicebook4.AddPage( self.m_panel29, u"builtin libraries", False )
		self.m_panel28 = wx.Panel( self.m_choicebook4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer182 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer182.SetFlexibleDirection( wx.BOTH )
		fgSizer182.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		self.m_panel28.SetSizer( fgSizer182 )
		self.m_panel28.Layout()
		fgSizer182.Fit( self.m_panel28 )
		self.m_choicebook4.AddPage( self.m_panel28, u"custom libraries", False )
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
	
	def __del__( self ):
		pass
	

###########################################################################
## Class EditDecorators
###########################################################################

class EditDecorators ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit decorators", pos = wx.DefaultPosition, size = wx.Size( 503,376 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer229 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer229.AddGrowableCol( 0 )
		fgSizer229.AddGrowableRow( 0 )
		fgSizer229.SetFlexibleDirection( wx.BOTH )
		fgSizer229.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer239 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer239.AddGrowableCol( 0 )
		fgSizer239.AddGrowableRow( 0 )
		fgSizer239.SetFlexibleDirection( wx.BOTH )
		fgSizer239.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_listCtrl6 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_SMALL_ICON )
		fgSizer239.Add( self.m_listCtrl6, 1, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer240 = wx.FlexGridSizer( 6, 1, 0, 0 )
		fgSizer240.AddGrowableCol( 0 )
		fgSizer240.AddGrowableRow( 5 )
		fgSizer240.SetFlexibleDirection( wx.BOTH )
		fgSizer240.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_bpButton64 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-add", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer240.Add( self.m_bpButton64, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_bpButton65 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-edit", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton65.Enable( False )
		
		fgSizer240.Add( self.m_bpButton65, 0, wx.ALL, 5 )
		
		self.m_bpButton66 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( u"gtk-delete", wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton66.Enable( False )
		
		fgSizer240.Add( self.m_bpButton66, 0, wx.ALL, 5 )
		
		self.m_bpButton67 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_GO_UP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton67.Enable( False )
		
		fgSizer240.Add( self.m_bpButton67, 0, wx.ALL, 5 )
		
		self.m_bpButton68 = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_GO_DOWN, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpButton68.Enable( False )
		
		fgSizer240.Add( self.m_bpButton68, 0, wx.ALL, 5 )
		
		
		fgSizer240.AddSpacer( ( 40, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer239.Add( fgSizer240, 1, wx.EXPAND, 5 )
		
		
		fgSizer229.Add( fgSizer239, 1, wx.EXPAND, 5 )
		
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
		self.m_listCtrl6.Bind( wx.EVT_LIST_ITEM_DESELECTED, self.OnUnselectDecorator )
		self.m_listCtrl6.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnSelectDecorator )
		self.m_bpButton64.Bind( wx.EVT_BUTTON, self.OnAddDecorator )
		self.m_bpButton65.Bind( wx.EVT_BUTTON, self.OnEditDecorator )
		self.m_bpButton66.Bind( wx.EVT_BUTTON, self.OnDeleteDecorator )
		self.m_bpButton67.Bind( wx.EVT_BUTTON, self.OnDecoratorUp )
		self.m_bpButton68.Bind( wx.EVT_BUTTON, self.OnDecoratorDown )
		self.m_sdbSizer12Cancel.Bind( wx.EVT_BUTTON, self.OnCancel )
		self.m_sdbSizer12OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnUnselectDecorator( self, event ):
		event.Skip()
	
	def OnSelectDecorator( self, event ):
		event.Skip()
	
	def OnAddDecorator( self, event ):
		event.Skip()
	
	def OnEditDecorator( self, event ):
		event.Skip()
	
	def OnDeleteDecorator( self, event ):
		event.Skip()
	
	def OnDecoratorUp( self, event ):
		event.Skip()
	
	def OnDecoratorDown( self, event ):
		event.Skip()
	
	def OnCancel( self, event ):
		event.Skip()
	
	def OnOK( self, event ):
		event.Skip()
	

###########################################################################
## Class NewDecorator
###########################################################################

class NewDecorator ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New decorator", pos = wx.DefaultPosition, size = wx.Size( 463,237 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer229 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer229.AddGrowableCol( 0 )
		fgSizer229.AddGrowableRow( 0 )
		fgSizer229.SetFlexibleDirection( wx.BOTH )
		fgSizer229.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer239 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer239.AddGrowableCol( 0 )
		fgSizer239.AddGrowableRow( 1 )
		fgSizer239.SetFlexibleDirection( wx.BOTH )
		fgSizer239.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer250 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer250.AddGrowableCol( 1 )
		fgSizer250.SetFlexibleDirection( wx.BOTH )
		fgSizer250.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText111 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText111.Wrap( -1 )
		fgSizer250.Add( self.m_staticText111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl79 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer250.Add( self.m_textCtrl79, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer239.Add( fgSizer250, 1, wx.EXPAND, 5 )
		
		sbSizer56 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"declaration" ), wx.VERTICAL )
		
		self.m_textCtrl80 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		sbSizer56.Add( self.m_textCtrl80, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer239.Add( sbSizer56, 1, wx.EXPAND, 5 )
		
		
		fgSizer229.Add( fgSizer239, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
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
		m_sdbSizer12.SetMinSize( wx.Size( -1,40 ) ) 
		
		fgSizer159.Add( m_sdbSizer12, 1, wx.EXPAND, 5 )
		
		
		fgSizer229.Add( fgSizer159, 1, wx.EXPAND|wx.ALL, 5 )
		
		
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
## Class NewBoostPythonModule
###########################################################################

class NewBoostPythonModule ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New boost.python module", pos = wx.DefaultPosition, size = wx.Size( 435,372 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer53 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer53.AddGrowableCol( 0 )
		fgSizer53.AddGrowableRow( 1 )
		fgSizer53.SetFlexibleDirection( wx.BOTH )
		fgSizer53.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer54 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer54.AddGrowableCol( 1 )
		fgSizer54.AddGrowableRow( 0 )
		fgSizer54.SetFlexibleDirection( wx.BOTH )
		fgSizer54.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer54.Add( self.m_staticText26, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl21 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer54.Add( self.m_textCtrl21, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		fgSizer53.Add( fgSizer54, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"exposed elements" ), wx.VERTICAL )
		
		agwStyle = (CT.TR_DEFAULT_STYLE|CT.TR_MULTIPLE  | CT.TR_AUTO_CHECK_CHILD  | CT.TR_AUTO_CHECK_PARENT | CT.TR_AUTO_TOGGLE_CHILD)
		self.m_tree = CT.CustomTreeCtrl(self, agwStyle=agwStyle)
		sbSizer6.Add( self.m_tree, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer53.Add( sbSizer6, 1, wx.EXPAND, 5 )
		
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
		
		
		fgSizer53.Add( fgSizer159, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer53 )
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
## Class Navigator
###########################################################################

class Navigator ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 451,417 ), style = 0|wx.NO_BORDER )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer189 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer189.AddGrowableCol( 0 )
		fgSizer189.AddGrowableRow( 0 )
		fgSizer189.SetFlexibleDirection( wx.BOTH )
		fgSizer189.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT|wx.TR_SINGLE )
		fgSizer189.Add( self.m_tree, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer189 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnEraseBrackground )
		self.Bind( wx.EVT_KILL_FOCUS, self.OnLoseFocus )
		self.m_tree.Bind( wx.EVT_ERASE_BACKGROUND, self.OnEraseBrackground )
		self.m_tree.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.OnChoice )
		self.m_tree.Bind( wx.EVT_TREE_ITEM_EXPANDED, self.OnExpandItem )
		self.m_tree.Bind( wx.EVT_TREE_SEL_CHANGED, self.OnSelectElement )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnEraseBrackground( self, event ):
		event.Skip()
	
	def OnLoseFocus( self, event ):
		event.Skip()
	
	
	def OnChoice( self, event ):
		event.Skip()
	
	def OnExpandItem( self, event ):
		event.Skip()
	
	def OnSelectElement( self, event ):
		event.Skip()
	

