# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.richtext
import wxx
import wx.propgrid as pg

###########################################################################
## Class NewTask
###########################################################################

class NewTask ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Task", pos = wx.DefaultPosition, size = wx.Size( 518,544 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer6 = wx.FlexGridSizer( 5, 1, 0, 0 )
		fgSizer6.AddGrowableCol( 0 )
		fgSizer6.AddGrowableRow( 3 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer7 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.AddGrowableRow( 0 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Short description:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer7.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textCtrl2, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		fgSizer6.Add( fgSizer7, 0, wx.EXPAND|wx.ALL, 5 )
		
		fgSizer5 = wx.FlexGridSizer( 3, 4, 0, 0 )
		fgSizer5.AddGrowableCol( 1 )
		fgSizer5.AddGrowableCol( 3 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"type:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		fgSizer5.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice2Choices = [ u"development", u"modification", u"improvement", u"fix" ]
		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		fgSizer5.Add( self.m_choice2, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText41 = wx.StaticText( self, wx.ID_ANY, u"created:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText41.Wrap( -1 )
		fgSizer5.Add( self.m_staticText41, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		fgSizer5.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText48 = wx.StaticText( self, wx.ID_ANY, u"status:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText48.Wrap( -1 )
		fgSizer5.Add( self.m_staticText48, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		m_choice1Choices = [ u"pending", u"working", u"done" ]
		self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
		self.m_choice1.SetSelection( 0 )
		fgSizer5.Add( self.m_choice1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"started:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )
		fgSizer5.Add( self.m_staticText5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		fgSizer5.Add( self.m_staticText7, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"priority:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		fgSizer5.Add( self.m_staticText12, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_choice3Choices = [ u"Low", u"Normal", u"High", u"Critical" ]
		self.m_choice3 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice3Choices, 0 )
		self.m_choice3.SetSelection( 1 )
		fgSizer5.Add( self.m_choice3, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText71 = wx.StaticText( self, wx.ID_ANY, u"finished:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText71.Wrap( -1 )
		fgSizer5.Add( self.m_staticText71, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText72 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText72.Wrap( -1 )
		fgSizer5.Add( self.m_staticText72, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer6.Add( fgSizer5, 1, wx.EXPAND, 5 )
		
		fgSizer61 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer61.AddGrowableCol( 1 )
		fgSizer61.SetFlexibleDirection( wx.BOTH )
		fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"reference:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		fgSizer61.Add( self.m_staticText10, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"none", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer61.Add( self.m_staticText11, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer6.Add( fgSizer61, 1, wx.EXPAND, 5 )
		
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
## Class TasksView
###########################################################################

class TasksView ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 510,801 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer41 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer41.AddGrowableCol( 0 )
		fgSizer41.AddGrowableRow( 0 )
		fgSizer41.SetFlexibleDirection( wx.BOTH )
		fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_splitter = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter.SetSashGravity( 1 )
		self.m_splitter.Bind( wx.EVT_IDLE, self.m_splitterOnIdle )
		self.m_splitter.SetMinimumPaneSize( 50 )
		
		self.m_treePane = wx.Panel( self.m_splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		fgSizer8 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer8.AddGrowableCol( 0 )
		fgSizer8.AddGrowableRow( 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wxx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE | wx.NO_BORDER)
		fgSizer8.Add( self.m_tree, 0, wx.EXPAND, 5 )
		
		
		self.m_treePane.SetSizer( fgSizer8 )
		self.m_treePane.Layout()
		fgSizer8.Fit( self.m_treePane )
		self.m_splitter.Initialize( self.m_treePane )
		fgSizer41.Add( self.m_splitter, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer41 )
		self.Layout()
		
		# Connect Events
		self.m_tree.Bind( wx.EVT_RIGHT_DOWN, self.OnTasksMenu )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnTasksMenu( self, event ):
		event.Skip()
	
	def m_splitterOnIdle( self, event ):
		self.m_splitter.SetSashPosition( 553 )
		self.m_splitter.Unbind( wx.EVT_IDLE )
	

###########################################################################
## Class Info
###########################################################################

class Info ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,150 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer247 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer247.AddGrowableCol( 0 )
		fgSizer247.AddGrowableRow( 0 )
		fgSizer247.SetFlexibleDirection( wx.BOTH )
		fgSizer247.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_propertyGrid = pg.PropertyGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE|wx.SIMPLE_BORDER)
		fgSizer247.Add( self.m_propertyGrid, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_text = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.HSCROLL|wx.SIMPLE_BORDER|wx.VSCROLL|wx.WANTS_CHARS )
		self.m_text.SetMinSize( wx.Size( -1,100 ) )
		
		fgSizer247.Add( self.m_text, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.SetSizer( fgSizer247 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class NewFolder
###########################################################################

class NewFolder ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New tasks folder", pos = wx.DefaultPosition, size = wx.Size( 423,390 ), style = wx.DEFAULT_DIALOG_STYLE )
		
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
	

