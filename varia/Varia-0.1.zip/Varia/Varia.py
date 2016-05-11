#!/usr/bin/env python

import pygame
from pygame.locals import *
from serial import Serial
import serial
#import configparser
import os
import sys
import math

pygame.font.init()
#STANDARD_FONT = pygame.font.SysFont('freesansbold.ttf', 14)

BLACK     	= (  0,   0,   0)
WHITE     	= (255, 255, 255)
DARKGRAY  	= ( 64,  64,  64)
GRAY      	= (128, 128, 128)
LIGHTGRAY 	= (212, 208, 200)
LIGHTERGRAY	= (222, 218, 210)
RED 		= (255,   0,   0)
GREEN		= (  0, 255,   0)
BLUE		= (  0,   0, 255)

class DropBox(object):
	def __init__(self, ItemList, Surface, Rect=None, Font=None, DominantItem=None):
		if Rect == None:
			self.Rect = pygame.Rect(0, 0, 100, 30)
		else:
			self.Rect = pygame.Rect(Rect)
			self.Rect.inflate_ip(20,0)
		if Font == None:
			self.Font = STANDARD_FONT
		else:
			self.Font = Font
		if DominantItem == None:
			if len(ItemList) > 0:
				self.DominantItem = str(ItemList[0])
			else:
				self.DominantItem = ""
		else:
			self.DominantItem = str(DominantItem)

		self.surface=Surface
		self.ItemList = []
		for item in ItemList:
			self.ItemList.append(str(item))
		self.clicked = False
		self.lastClick = False
		self.show_menu = False
		self.highlight = {}
		for item in self.ItemList:
			self.highlight[item] = False

	def _drop_down_menu(self, Surface=None, event=None):
		iItem = 0
		iEvent = 0
		font_size = self.Font.size("W")
		if event != None:
			for item in self.ItemList:
				self.highlight[item] = False
				if pygame.Rect(self.Rect.x, self.Rect.y+self.Rect.h+iEvent*(font_size[1]), self.Rect.w, font_size[1]).collidepoint(event.pos):
					if event.type == MOUSEBUTTONUP:
						self.DominantItem = item
					elif event.type == MOUSEMOTION:
						self.highlight[item] = True
				iEvent += 1
		elif Surface != None:
			for item in self.ItemList:
				if self.highlight[item]:
					chosen_color = LIGHTERGRAY
				else:
					chosen_color = LIGHTGRAY

				shownItem = item
				dItemSize = self.Font.size(shownItem)
				addShortener = False
				while dItemSize[0] > self.Rect.w-20:
					shownItem = shownItem[:-1]
					dItemSize = self.Font.size(shownItem)
					addShortener = True

				if addShortener:
					shownItem += "..."
				pygame.draw.rect(Surface, chosen_color, pygame.Rect(self.Rect.x, self.Rect.y+self.Rect.h+iItem*(font_size[1]), self.Rect.w, font_size[1]))
				pygame.draw.rect(Surface, GRAY, pygame.Rect(self.Rect.x, self.Rect.y+self.Rect.h+iItem*(font_size[1]), self.Rect.w, font_size[1]), 1)
				Surface.blit(self.Font.render(shownItem, 1, (0,0,0)), (self.Rect.x+2, self.Rect.y+self.Rect.h+2+iItem*(font_size[1])))
				iItem+=1

	def event_handler(self, event):
		if event.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
			return self.DominantItem
		if self.Rect.collidepoint(event.pos):
			if event.type is MOUSEBUTTONDOWN:
				self.clicked = True
				self.lastClick = True
		else:
			if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
				self.lastClick = False

		if event.type is MOUSEMOTION:
			self._drop_down_menu(event=event)

		if event.type is MOUSEBUTTONUP:
			if self.show_menu:
				self._drop_down_menu(event=event)
				self.show_menu = False
			elif self.lastClick:
				self.show_menu = True
			self.lastClick = False
		return self.DominantItem

	def draw(self):
		pygame.draw.rect(self.surface, LIGHTGRAY, self.Rect, 0)
		pygame.draw.rect(self.surface, GRAY, self.Rect, 2)
		pygame.draw.polygon(self.surface, GRAY, ((self.Rect.x+self.Rect.w-5, self.Rect.y+self.Rect.h*0.5-5), (self.Rect.x+self.Rect.w-10, self.Rect.y+self.Rect.h*0.8), (self.Rect.x+self.Rect.w-15, self.Rect.y+self.Rect.h*0.5-5)), 0)
		pygame.draw.line(self.surface, GRAY, (self.Rect.x+self.Rect.w-20, self.Rect.y), (self.Rect.x+self.Rect.w-20, self.Rect.y+self.Rect.h), 2)
		shownItem = self.DominantItem

		dItemSize = self.Font.size(shownItem)
		while dItemSize[0] > self.Rect.w-20:
			shownItem = shownItem[:-1]
			dItemSize = self.Font.size(shownItem)


		self.surface.blit(self.Font.render(shownItem, 1, (0,0,0)), (self.Rect.x+2, self.Rect.y+self.Rect.h*0.1))

		if self.show_menu:
			self._drop_down_menu(Surface=self.surface)

class ToggleButton(object):
	def __init__(self, Surface, Title=None, Rect=None, Font=None, DominantState=None):
		if Title == None:
			self.title = " "
		else:
			self.title = Title

		if Rect == None:
			self.Rect = pygame.Rect(10, 10, 60, 60)
		else:
			self.Rect = pygame.Rect(Rect)

		if Font == None:
			self.font = STANDARD_FONT
		else:
			self.font = Font
			self.clicked = False
			self.lastClick = False

		if DominantState == None:
			self.state = False
		else:
			if DominantState == "True" or DominantState == True:
				self.state = True
			else:
				self.state = False

		self.surface = Surface
		self.status_sign_size = 4

	def onClick(self, event):
		try:
			if self.Rect.collidepoint(event.pos):
				if event.type is MOUSEBUTTONDOWN:
					self.lastClick = True
			else:
				if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
					self.lastClick = False
		except:
			pass

		if event.type is MOUSEBUTTONUP:
			if self.lastClick:
				self.state = not self.state
			self.lastClick = False

		return self.state

	def draw(self):
		pygame.draw.rect(self.surface, LIGHTGRAY, self.Rect, 0)
		pygame.draw.rect(self.surface, GRAY, self.Rect, 2)
		status_pos = (self.Rect.centerx, self.Rect.centery-int(self.Rect.h/2)+self.status_sign_size*2)
		if self.state:
			chosen_color = GREEN
		else:
			chosen_color = RED
		pygame.draw.circle(self.surface, chosen_color, status_pos, self.status_sign_size)
		self.surface.blit(self.font.render(self.title, 1, (0,0,0)), (self.Rect.centerx-int(self.font.size(self.title)[0]/2), self.Rect.y+self.Rect.h-int(self.font.size(self.title)[1])))

	def _change_state(self):
		self.state = not self.state

class ScrollBox(object):
	def __init__(self, dItemList, Surface, Rect=None, Font=None, bSelecable=False):
		self.dItemList = dItemList
		self.bSelecable = bSelecable
		self.surface = Surface

		self.QueueItem = []
		self.QueueColor = []

		self.scroll_w_offset = 9
		self.scroll_h_offset = 6
		self.scroll_width = 6
		self.off_screen = False
		self.itemlist_colors = []

		if len(self.dItemList) == 0:
			self.dItemList.append(" ")

		if len(self.itemlist_colors) == 0:
			self.itemlist_colors.append((0,0,0))


		if Rect == None: self.rect = pygame.Rect((10,10,100,100))
		else: self.rect = pygame.Rect(Rect)

		if Font == None: self.font = STANDARD_FONT
		else: self.font = Font

		self.scroll_bar = pygame.Rect(self.rect.topright[0] - self.scroll_w_offset, self.rect.bottomright[1] - self.scroll_h_offset*2 - int(self.scroll_width/2) , self.scroll_width, self.rect.h - self.scroll_h_offset*2)
		self.clicked_scroll = False
		if len(self.dItemList) > self.rect.h/(self.font.size(str(self.dItemList[0]))[1]):
			self.scroll_bar.h = int(self.rect.h/len(self.dItemList))
			if self.scroll_bar.h < 30:
				self.scroll_bar.h = 30
		else:
			self.scroll_bar.y = -1000
			self.off_screen = True
		self.scroll_bar.y = self.rect.y + self.rect.h - self.scroll_bar.h - int(self.scroll_width)

	def draw(self):
		while len(self.QueueItem) > 0:
			self.dItemList.append(self.QueueItem.pop(0))
			self.itemlist_colors.append(self.QueueColor.pop(0))
		if len(self.dItemList) > self.rect.h/(self.font.size(str(self.dItemList[0]))[1]):
			self.scroll_bar.h = int(self.rect.h/len(self.dItemList))
			if self.scroll_bar.h < 30:
				self.scroll_bar.h = 30
			if self.off_screen:
				self.scroll_bar.y = self.rect.y + self.rect.h - self.scroll_bar.h - int(self.scroll_width)
				self.off_screen = False
		else:
			self.scroll_bar.y = -1000


		pygame.draw.rect(self.surface, LIGHTGRAY, self.rect)
		pygame.draw.rect(self.surface, GRAY, self.rect, 3)
		pygame.draw.rect(self.surface, DARKGRAY, self.scroll_bar)

		if self.scroll_bar.h != 0:
			pygame.draw.circle(self.surface, DARKGRAY, (self.scroll_bar.center[0], self.scroll_bar.bottomright[1]), int(self.scroll_width/2))
			pygame.draw.circle(self.surface, DARKGRAY, (self.scroll_bar.center[0], self.scroll_bar.topright[1]), int(self.scroll_width/2))

		i = 1
		if (self.rect.h - self.scroll_bar.h - self.scroll_width*2) != 0: pos_percent = (self.rect.y - self.scroll_bar.y + self.scroll_width)/(self.rect.h - self.scroll_bar.h - self.scroll_width*2) + 1
		else: pos_percent = 0
		u = (len(self.dItemList) + 2 - self.rect.h/(self.font.size(str(self.dItemList[0]))[1]))*pos_percent
		line_pos_x = self.rect.x + 5
		for k in self.dItemList[::-1]:
			line_pos_y = int(self.rect.y + self.rect.h + (u - i)*self.font.size(str(k))[1])
			if line_pos_y <= self.rect.y + self.rect.h - int(self.font.size(str(k))[1]) and line_pos_y >= self.rect.y:
				check_one = True
				if self.font.size(str(k))[0] > self.rect.w-15 and check_one:
					w = ""
					check_one = False
					while self.font.size(str(k))[0] >= self.rect.w-15:
						w += str(k)[-1:]
						k = str(k)[:-1]
					w = w[::-1]
					if self.dItemList[:-1] != w:
						self.dItemList.append(w)
						self.itemlist_colors.append(self.itemlist_colors[len(self.itemlist_colors)-1])

					self.dItemList = self.dItemList[::-1]
					self.dItemList[i] = k
					self.dItemList = self.dItemList[::-1]
				temp_itemlist_colors = self.itemlist_colors[::-1]
				self.surface.blit(self.font.render(str(k), 1, temp_itemlist_colors[i-1]), (line_pos_x, line_pos_y))
			i += 1

	def event_handler(self, event):
		if event.type is MOUSEBUTTONDOWN:
			if self.scroll_bar.collidepoint(event.pos):
				if event.button == 1:
					self.clicked_scroll = True
					self.click_pos = event.pos
					self.original_pos = self.scroll_bar

			elif self.rect.collidepoint(event.pos):
				if event.button == 5: self.scroll_bar.y = min(self.scroll_bar.y + 15, self.rect.bottomright[1] - self.scroll_h_offset - self.scroll_bar.h)
				if event.button == 4: self.scroll_bar.y = max(self.scroll_bar.y - 15, self.rect.topright[1] + self.scroll_h_offset)
		elif event.type is MOUSEBUTTONUP:
			self.clicked_scroll = False
		elif self.clicked_scroll and event.type is MOUSEMOTION and self.rect.collidepoint(event.pos):
			self.scroll_bar.y = max(min(self.original_pos.y - self.click_pos[1] + event.pos[1], self.rect.y + self.rect.h - self.scroll_bar.h - int(self.scroll_width)), self.rect.y + int(self.scroll_width))
			self.click_pos = event.pos

	def refresh_list(self, newList):
		self.dItemList = newList

	def add_item(self, item, item_color=(0,0,0)):
		self.QueueItem.append(item)
		self.QueueColor.append(item_color)

class PygButton(object):
    def __init__(self, rect=None, caption='', bgcolor=LIGHTGRAY, fgcolor=BLACK, font=None, normal=None, down=None, highlight=None):
        """Create a new button object. Parameters:
            rect - The size and position of the button as a pygame.Rect object
                or 4-tuple of integers.
            caption - The text on the button (default is blank)
            bgcolor - The background color of the button (default is a light
                gray color)
            fgcolor - The foreground color (i.e. the color of the text).
                Default is black.
            font - The pygame.font.Font object for the font of the text.
                Default is freesansbold in point 14.
            normal - A pygame.Surface object for the button's normal
                appearance.
            down - A pygame.Surface object for the button's pushed down
                appearance.
            highlight - A pygame.Surface object for the button's appearance
                when the mouse is over it.

            If the Surface objects are used, then the caption, bgcolor,
            fgcolor, and font parameters are ignored (and vice versa).
            Specifying the Surface objects lets the user use a custom image
            for the button.
            The normal, down, and highlight Surface objects must all be the
            same size as each other. Only the normal Surface object needs to
            be specified. The others, if left out, will default to the normal
            surface.
            """
        if rect is None:
            self._rect = pygame.Rect(0, 0, 30, 60)
        else:
            self._rect = pygame.Rect(rect)

        self._caption = caption
        self._bgcolor = bgcolor
        self._fgcolor = fgcolor

        if font is None:
            self._font = STANDARD_FONT
        else:
            self._font = font

        # tracks the state of the button
        self.buttonDown = False # is the button currently pushed down?
        self.mouseOverButton = False # is the mouse currently hovering over the button?
        self.lastMouseDownOverButton = False # was the last mouse down event over the mouse button? (Used to track clicks.)
        self._visible = True # is the button visible
        self.customSurfaces = False # button starts as a text button instead of having custom images for each surface

        if normal is None:
            # create the surfaces for a text button
            self.surfaceNormal = pygame.Surface(self._rect.size)
            self.surfaceDown = pygame.Surface(self._rect.size)
            self.surfaceHighlight = pygame.Surface(self._rect.size)
            self._update() # draw the initial button images
        else:
            # create the surfaces for a custom image button
            self.setSurfaces(normal, down, highlight)

    def handleEvent(self, eventObj):
        """All MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN event objects
        created by Pygame should be passed to this method. handleEvent() will
        detect if the event is relevant to this button and change its state.

        There are two ways that your code can respond to button-events. One is
        to inherit the PygButton class and override the mouse*() methods. The
        other is to have the caller of handleEvent() check the return value
        for the strings 'enter', 'move', 'down', 'up', 'click', or 'exit'.

        Note that mouseEnter() is always called before mouseMove(), and
        mouseMove() is always called before mouseExit(). Also, mouseUp() is
        always called before mouseClick().

        buttonDown is always True when mouseDown() is called, and always False
        when mouseUp() or mouseClick() is called. lastMouseDownOverButton is
        always False when mouseUp() or mouseClick() is called."""

        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            # The button only cares bout mouse-related events (or no events, if it is invisible)
            return []

        retVal = []

        hasExited = False
        if not self.mouseOverButton and self._rect.collidepoint(eventObj.pos):
            # if mouse has entered the button:
            self.mouseOverButton = True
            self.mouseEnter(eventObj)
            retVal.append('enter')
        elif self.mouseOverButton and not self._rect.collidepoint(eventObj.pos):
            # if mouse has exited the button:
            self.mouseOverButton = False
            hasExited = True # call mouseExit() later, since we want mouseMove() to be handled before mouseExit()

        if self._rect.collidepoint(eventObj.pos):
            # if mouse event happened over the button:
            if eventObj.type == MOUSEMOTION:
                self.mouseMove(eventObj)
                retVal.append('move')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self.buttonDown = True
                self.lastMouseDownOverButton = True
                self.mouseDown(eventObj)
                retVal.append('down')
        else:
            if eventObj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # if an up/down happens off the button, then the next up won't cause mouseClick()
                self.lastMouseDownOverButton = False

        # mouse up is handled whether or not it was over the button
        doMouseClick = False
        if eventObj.type == MOUSEBUTTONUP:
            if self.lastMouseDownOverButton:
                doMouseClick = True
            self.lastMouseDownOverButton = False

            if self.buttonDown:
                self.buttonDown = False
                self.mouseUp(eventObj)
                retVal.append('up')

            if doMouseClick:
                self.buttonDown = False
                self.mouseClick(eventObj)
                retVal.append('click')

        if hasExited:
            self.mouseExit(eventObj)
            retVal.append('exit')

        return retVal

    def draw(self, surfaceObj):
        """Blit the current button's appearance to the surface object."""
        if self._visible:
            if self.buttonDown:
                surfaceObj.blit(self.surfaceDown, self._rect)
            elif self.mouseOverButton:
                surfaceObj.blit(self.surfaceHighlight, self._rect)
            else:
                surfaceObj.blit(self.surfaceNormal, self._rect)

    def _update(self):
        """Redraw the button's Surface object. Call this method when the button has changed appearance."""
        if self.customSurfaces:
            self.surfaceNormal    = pygame.transform.smoothscale(self.origSurfaceNormal, self._rect.size)
            self.surfaceDown      = pygame.transform.smoothscale(self.origSurfaceDown, self._rect.size)
            self.surfaceHighlight = pygame.transform.smoothscale(self.origSurfaceHighlight, self._rect.size)
            return

        w = self._rect.width # syntactic sugar
        h = self._rect.height # syntactic sugar

        # fill background color for all buttons
        self.surfaceNormal.fill(self.bgcolor)
        self.surfaceDown.fill(self.bgcolor)
        self.surfaceHighlight.fill(self.bgcolor)

        # draw caption text for all buttons
        captionSurf = self._font.render(self._caption, True, self.fgcolor, self.bgcolor)
        captionRect = captionSurf.get_rect()
        captionRect.center = int(w / 2), int(h / 2)
        self.surfaceNormal.blit(captionSurf, captionRect)
        self.surfaceDown.blit(captionSurf, captionRect)

        # draw border for normal button
        pygame.draw.rect(self.surfaceNormal, BLACK, pygame.Rect((0, 0, w, h)), 1) # black border around everything
        pygame.draw.line(self.surfaceNormal, WHITE, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceNormal, WHITE, (1, 1), (1, h - 2))
        pygame.draw.line(self.surfaceNormal, DARKGRAY, (1, h - 1), (w - 1, h - 1))
        pygame.draw.line(self.surfaceNormal, DARKGRAY, (w - 1, 1), (w - 1, h - 1))
        pygame.draw.line(self.surfaceNormal, GRAY, (2, h - 2), (w - 2, h - 2))
        pygame.draw.line(self.surfaceNormal, GRAY, (w - 2, 2), (w - 2, h - 2))

        # draw border for down button
        pygame.draw.rect(self.surfaceDown, BLACK, pygame.Rect((0, 0, w, h)), 1) # black border around everything
        pygame.draw.line(self.surfaceDown, WHITE, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceDown, WHITE, (1, 1), (1, h - 2))
        pygame.draw.line(self.surfaceDown, DARKGRAY, (1, h - 2), (1, 1))
        pygame.draw.line(self.surfaceDown, DARKGRAY, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceDown, GRAY, (2, h - 3), (2, 2))
        pygame.draw.line(self.surfaceDown, GRAY, (2, 2), (w - 3, 2))

        # draw border for highlight button
        self.surfaceHighlight = self.surfaceNormal

    def mouseClick(self, event):
        pass # This class is meant to be overridden.
    def mouseEnter(self, event):
        pass # This class is meant to be overridden.
    def mouseMove(self, event):
        pass # This class is meant to be overridden.
    def mouseExit(self, event):
        pass # This class is meant to be overridden.
    def mouseDown(self, event):
        pass # This class is meant to be overridden.
    def mouseUp(self, event):
        pass # This class is meant to be overridden.

    def setSurfaces(self, normalSurface, downSurface=None, highlightSurface=None):
        """Switch the button to a custom image type of button (rather than a
        text button). You can specify either a pygame.Surface object or a
        string of a filename to load for each of the three button appearance
        states."""
        if downSurface is None:
            downSurface = normalSurface
        if highlightSurface is None:
            highlightSurface = normalSurface

        if type(normalSurface) == str:
            self.origSurfaceNormal = pygame.image.load(normalSurface)
        if type(downSurface) == str:
            self.origSurfaceDown = pygame.image.load(downSurface)
        if type(highlightSurface) == str:
            self.origSurfaceHighlight = pygame.image.load(highlightSurface)

        if self.origSurfaceNormal.get_size() != self.origSurfaceDown.get_size() != self.origSurfaceHighlight.get_size():
            raise Exception('foo')

        self.surfaceNormal = self.origSurfaceNormal
        self.surfaceDown = self.origSurfaceDown
        self.surfaceHighlight = self.origSurfaceHighlight
        self.customSurfaces = True
        self._rect = pygame.Rect((self._rect.left, self._rect.top, self.surfaceNormal.get_width(), self.surfaceNormal.get_height()))

    def _propGetCaption(self):
        return self._caption

    def _propSetCaption(self, captionText):
        self.customSurfaces = False
        self._caption = captionText
        self._update()

    def _propGetRect(self):
        return self._rect

    def _propSetRect(self, newRect):
        # Note that changing the attributes of the Rect won't update the button. You have to re-assign the rect member.
        self._update()
        self._rect = newRect

    def _propGetVisible(self):
        return self._visible

    def _propSetVisible(self, setting):
        self._visible = setting

    def _propGetFgColor(self):
        return self._fgcolor

    def _propSetFgColor(self, setting):
        self.customSurfaces = False
        self._fgcolor = setting
        self._update()

    def _propGetBgColor(self):
        return self._bgcolor

    def _propSetBgColor(self, setting):
        self.customSurfaces = False
        self._bgcolor = setting
        self._update()

    def _propGetFont(self):
        return self._font

    def _propSetFont(self, setting):
        self.customSurfaces = False
        self._font = setting
        self._update()

    caption = property(_propGetCaption, _propSetCaption)
    rect = property(_propGetRect, _propSetRect)
    visible = property(_propGetVisible, _propSetVisible)
    fgcolor = property(_propGetFgColor, _propSetFgColor)
    bgcolor = property(_propGetBgColor, _propSetBgColor)
    font = property(_propGetFont, _propSetFont)

class TypeBox(object):
	def __init__(self, Surface, Rect, Font, DominantItem=None, NumbersOnly=False, ReturnRemove=False, AlwaysActive=False):
		self.surface = Surface
		self.rect = pygame.Rect(Rect)
		self.font = Font
		self.type_state = False
		self.NumbersOnly = NumbersOnly
		self.ReturnRemove = ReturnRemove
		self.AlwaysActive = AlwaysActive
		self.letter_size = self.font.size("_")
		self.character_limit = int(self.rect.w/self.letter_size[0]) - 2
		pygame.key.set_repeat(500, 75)
		if DominantItem == None:
			self.DominantItem = ""
		else:
			self.DominantItem = DominantItem

	def event_handler(self, event):
		if event.type is MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				if event.button == 1 or self.AlwaysActive:
					self.type_state = True
			else:
				if event.button == 1 and self.type_state:
					self.type_state = False
		elif event.type is MOUSEBUTTONUP:
			pass
		elif event.type is KEYDOWN and (self.type_state or self.AlwaysActive):
			if self.NumbersOnly:
				for i in range(0,10):
					if str(event.unicode) == str(i):
						self.DominantItem += str(event.unicode)
				if event.key == pygame.K_BACKSPACE:
					self.DominantItem = self.DominantItem[:-1]
				elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
					self.type_state = False
					if self.ReturnRemove:
						self.DominantItem = ""
						self.type_state = True
			else:
				if event.key == pygame.K_TAB:
					self.DominantItem += "    "
				elif event.key == pygame.K_BACKSPACE:
					self.DominantItem = self.DominantItem[:-1]
				elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
					self.type_state = False
				else:
					self.DominantItem += str(event.unicode)
					self.type_state = True

		if not self.type_state:
			sent = self.DominantItem
			if self.ReturnRemove: self.DominantItem = ""
			return sent
		else:
			return ""

	def draw(self):
		cmd_width_offset = 0
		pygame.draw.rect(self.surface, LIGHTGRAY, self.rect)
		pygame.draw.rect(self.surface, GRAY, self.rect, 3)

		uptimeSec = math.floor(pygame.time.get_ticks()/1000)

		temp_text = str(self.DominantItem[-self.character_limit:])

		cmdWidthPlacement = self.font.render(str(temp_text), 1, (0,0,0)).get_width()

		if cmdWidthPlacement >= self.rect.w-self.letter_size[0]: cmd_width_offset = - (cmdWidthPlacement - self.rect.w + self.letter_size[0])

		if self.letter_size[1] < self.rect.h: y_pos = self.rect.y + int(self.rect.h/4)
		else: y_pos = self.rect.y
		text = self.font.render(str(temp_text), 1, (0,0,0))
		self.surface.blit(text, (self.rect.x+5+cmd_width_offset, y_pos))
		if uptimeSec % 2 == 0 and (self.type_state or self.AlwaysActive): self.surface.blit(self.font.render("|", 1, (0,0,0)), (self.rect.x+5+cmd_width_offset+text.get_width(), y_pos))

class Window(object):
	def __init__(self, Surface, Rect, Font):
		self.rect = pygame.Rect(Rect)
		self.font = Font
		self.surface = Surface

		self.interactive_objects = []
		self.values = {}
		self.ID = []
		self.text = {}

		self.visible = False

	def draw(self):
		if self.visible:
			pygame.draw.rect(self.surface, LIGHTGRAY, self.rect)
			pygame.draw.rect(self.surface, GRAY, self.rect, 3)

			if len(self.interactive_objects) > 0:
				d = 0
				for i in self.interactive_objects:
					if self.ID[d] != "EXIT": i.draw()
					else: i.draw(self.surface)
					d += 1

			if len(self.text) > 0:
				for k,v in self.text.items():
					self.surface.blit(self.font.render(k, 1, (0,0,0)), (v[0], v[1]))

	def event_handler(self, event):
		if self.visible:
			if len(self.interactive_objects) > 0:
				d = 0
				for i in self.interactive_objects:
					if self.ID[d] != "EXIT": self.values[self.ID[d]] = i.event_handler(event)
					else:
						if "click" in i.handleEvent(event):
							self.values[self.ID[d]] = True
						else:
							self.values[self.ID[d]] = False
					d += 1
			return self.values

	def set_visible(self, state):
		self.visible = state

	def get_visible(self):
		return self.visible

	def add_text(self, text, pos):
		pos_x = pos[0] + self.rect.x
		pos_y = pos[1] + self.rect.y
		self.text[text] = (pos_x, pos_y)

	def add_scrollbox(self, Rect, ItemList, ID):
		rect = []
		rect.append(Rect[0] + self.rect.x + 10)
		rect.append(Rect[1] + self.rect.y + 10)
		rect.append(Rect[2])
		rect.append(Rect[3])
		self.interactive_objects.append(ScrollBox(dItemList=ItemList, Surface=self.surface, Rect=rect, Font=self.font, bSelecable=False))
		self.ID.append(ID)

	def add_pygbutton(self, Rect, Title, ID):
		rect = []
		rect.append(Rect[0] + self.rect.x + 10)
		rect.append(Rect[1] + self.rect.y + 10)
		rect.append(Rect[2])
		rect.append(Rect[3])
		self.interactive_objects.append(PygButton(rect, Title, font=self.font))
		self.ID.append(ID)

	def add_typebox(self, Rect, ID, DominantItem=None, NumbersOnly=False, ReturnRemove=False, AlwaysActive=False):
		rect = []
		rect.append(Rect[0] + self.rect.x + 10)
		rect.append(Rect[1] + self.rect.y + 10)
		rect.append(Rect[2])
		rect.append(Rect[3])
		self.interactive_objects.append(TypeBox(Surface=self.surface, Rect=rect, Font=self.font, DominantItem=DominantItem, NumbersOnly=NumbersOnly, ReturnRemove=ReturnRemove, AlwaysActive=AlwaysActive))
		self.ID.append(ID)

	def add_toggle_button(self, Rect, ID, Title=None, DominantState=False):
		rect = []
		rect.append(Rect[0] + self.rect.x + 10)
		rect.append(Rect[1] + self.rect.y + 10)
		rect.append(Rect[2])
		rect.append(Rect[3])
		self.interactive_objects.append(ToggleButton(Surface=self.surface, Title=Title, Rect=rect, Font=self.font, DominantState=DominantState))
		self.ID.append(ID)

	def add_dropbox(self, ItemList, Rect, ID, DominantItem=None):
		rect = []
		rect.append(Rect[0] + self.rect.x + 10)
		rect.append(Rect[1] + self.rect.y + 10)
		rect.append(Rect[2])
		rect.append(Rect[3])
		self.interactive_objects.append(DropBox(ItemList=ItemList, Surface=self.surface, Rect=rect, Font=self.font, DominantItem=DominantItem))
		self.ID.append(ID)