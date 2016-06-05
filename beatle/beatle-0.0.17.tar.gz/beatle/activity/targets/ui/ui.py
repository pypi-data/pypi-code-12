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

###########################################################################
## Class TargetsView
###########################################################################

class TargetsView ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL|wx.WANTS_CHARS )
		
		self.SetExtraStyle( wx.WS_EX_BLOCK_EVENTS )
		
		fgSizer4 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer4.AddGrowableCol( 0 )
		fgSizer4.AddGrowableRow( 0 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tree = wxx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_SINGLE )
		fgSizer4.Add( self.m_tree, 0, wx.ALL, 5 )
		
		
		self.SetSizer( fgSizer4 )
		self.Layout()
	
	def __del__( self ):
		pass
	

