# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.propgrid as pg

import gettext
_ = gettext.gettext

###########################################################################
## Class AstExplorerPane
###########################################################################

class AstExplorerPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 474,434 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer245 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer245.AddGrowableCol( 0 )
		fgSizer245.AddGrowableRow( 0 )
		fgSizer245.SetFlexibleDirection( wx.BOTH )
		fgSizer245.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_splitter3 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter3.Bind( wx.EVT_IDLE, self.m_splitter3OnIdle )
		
		self.m_panel32 = wx.Panel( self.m_splitter3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer250 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer250.AddGrowableCol( 0 )
		fgSizer250.AddGrowableRow( 0 )
		fgSizer250.SetFlexibleDirection( wx.BOTH )
		fgSizer250.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_splitter4 = wx.SplitterWindow( self.m_panel32, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter4.Bind( wx.EVT_IDLE, self.m_splitter4OnIdle )
		
		self.m_panel30 = wx.Panel( self.m_splitter4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer246 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer246.AddGrowableCol( 0 )
		fgSizer246.AddGrowableRow( 0 )
		fgSizer246.SetFlexibleDirection( wx.BOTH )
		fgSizer246.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wx.TreeCtrl( self.m_panel30, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_SINGLE )
		fgSizer246.Add( self.m_tree, 0, wx.EXPAND|wx.TOP|wx.LEFT, 5 )
		
		
		self.m_panel30.SetSizer( fgSizer246 )
		self.m_panel30.Layout()
		fgSizer246.Fit( self.m_panel30 )
		self.m_panel31 = wx.Panel( self.m_splitter4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer247 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer247.AddGrowableCol( 0 )
		fgSizer247.AddGrowableRow( 0 )
		fgSizer247.SetFlexibleDirection( wx.BOTH )
		fgSizer247.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_propertyGrid = pg.PropertyGrid(self.m_panel31, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE)
		fgSizer247.Add( self.m_propertyGrid, 0, wx.EXPAND|wx.BOTTOM|wx.LEFT, 5 )
		
		
		self.m_panel31.SetSizer( fgSizer247 )
		self.m_panel31.Layout()
		fgSizer247.Fit( self.m_panel31 )
		self.m_splitter4.SplitHorizontally( self.m_panel30, self.m_panel31, 317 )
		fgSizer250.Add( self.m_splitter4, 1, wx.EXPAND, 5 )
		
		
		self.m_panel32.SetSizer( fgSizer250 )
		self.m_panel32.Layout()
		fgSizer250.Fit( self.m_panel32 )
		self.m_splitter3.Initialize( self.m_panel32 )
		fgSizer245.Add( self.m_splitter3, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer245 )
		self.Layout()
		
		# Connect Events
		self.m_tree.Bind( wx.EVT_TREE_SEL_CHANGED, self.OnSelectItem )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnSelectItem( self, event ):
		event.Skip()
	
	def m_splitter3OnIdle( self, event ):
		self.m_splitter3.SetSashPosition( 0 )
		self.m_splitter3.Unbind( wx.EVT_IDLE )
	
	def m_splitter4OnIdle( self, event ):
		self.m_splitter4.SetSashPosition( 317 )
		self.m_splitter4.Unbind( wx.EVT_IDLE )
	

###########################################################################
## Class ChooseFile
###########################################################################

class ChooseFile ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Select file"), pos = wx.DefaultPosition, size = wx.Size( 366,231 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		fgSizer242 = wx.FlexGridSizer( 2, 1, 0, 0 )
		fgSizer242.AddGrowableCol( 0 )
		fgSizer242.AddGrowableRow( 0 )
		fgSizer242.SetFlexibleDirection( wx.BOTH )
		fgSizer242.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		fgSizer244 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer244.AddGrowableCol( 1 )
		fgSizer244.AddGrowableRow( 0 )
		fgSizer244.SetFlexibleDirection( wx.BOTH )
		fgSizer244.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText112 = wx.StaticText( self, wx.ID_ANY, _(u"select file"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText112.Wrap( -1 )
		fgSizer244.Add( self.m_staticText112, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )
		
		self.m_filePicker1 = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, _(u"Select a python file"), u"*.py", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_USE_TEXTCTRL )
		fgSizer244.Add( self.m_filePicker1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer242.Add( fgSizer244, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		fgSizer243 = wx.FlexGridSizer( 1, 2, 0, 0 )
		fgSizer243.AddGrowableCol( 1 )
		fgSizer243.SetFlexibleDirection( wx.BOTH )
		fgSizer243.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_info = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer243.Add( self.m_info, 0, wx.ALL, 5 )
		
		m_sdbSizer25 = wx.StdDialogButtonSizer()
		self.m_sdbSizer25OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer25.AddButton( self.m_sdbSizer25OK )
		self.m_sdbSizer25Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer25.AddButton( self.m_sdbSizer25Cancel )
		m_sdbSizer25.Realize();
		
		fgSizer243.Add( m_sdbSizer25, 1, wx.EXPAND, 5 )
		
		
		fgSizer242.Add( fgSizer243, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer242 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_sdbSizer25OK.Bind( wx.EVT_BUTTON, self.OnOK )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		event.Skip()
	

