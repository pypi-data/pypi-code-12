# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class LogExplorerPane
###########################################################################

class LogExplorerPane ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 511,326 ), style = wx.TAB_TRAVERSAL )
		
		fgSizer245 = wx.FlexGridSizer( 1, 1, 0, 0 )
		fgSizer245.AddGrowableCol( 0 )
		fgSizer245.AddGrowableRow( 0 )
		fgSizer245.SetFlexibleDirection( wx.BOTH )
		fgSizer245.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_report = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
		fgSizer245.Add( self.m_report, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( fgSizer245 )
		self.Layout()
	
	def __del__( self ):
		pass
	

