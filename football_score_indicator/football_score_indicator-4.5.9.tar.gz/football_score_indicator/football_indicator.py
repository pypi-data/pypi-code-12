#!/usr/bin/env python

from gi.repository import Gtk,GObject,GdkPixbuf
from gi.repository import AppIndicator3 as appindicator
from configuration import Configurations

from os import path
import threading
import time
import signal
import webbrowser
import sys

from espnfootball_scrap import get_matches_summary, get_match_goaldata
from Preferences import PreferencesWindow

ICON = "football"
VERSION_STR="4.5.2"
#time ot between each fetch
REFRESH_INTERVAL = 10

class FootballIndicator:
    
    def __init__(self):
        self.config = Configurations()
        self.indicator = appindicator.Indicator.new("football-score-indicator",
                        ICON,
                        appindicator.IndicatorCategory.APPLICATION_STATUS)
        # path.abspath(path.dirname(__file__))+"/football.png"
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_icon(ICON)

        self.indicatorLabelId = None
        self.indicator.set_label("No Live Matches","")

        self.menu = Gtk.Menu().new()
        self.indicator.set_menu(self.menu)

        self.matchMenu = []
        self.addQuitAboutPreferences(self.menu)

        self.dataLock = threading.Semaphore()

    def main(self):
        signal.signal(signal.SIGINT,signal.SIG_DFL)
        thread = threading.Thread(target = self.updateDataAfterInterval)
        #print thread.name
        thread.daemon = True
        
        #read previous configurations initially
        print "READING INITIAL SETTINGS"
        self.settingsChanged()
        print "READ INITIAL SETTINGS"




        thread.start()
        Gtk.main()

    
    def settingsChanged(self):
        print "CALLBACK: SETTINGS CHANGED"
        self.configurations = self.config.readConfigurations()
        self.changed = True


    def addQuitAboutPreferences(self,menu):
        preferences_item = Gtk.MenuItem('Preferences')
        preferences_item.connect("activate", preferences,self.settingsChanged)
        preferences_item.show()

        about_item = Gtk.MenuItem("About")
        about_item.connect("activate", about)
        about_item.show()

        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", quit)
        quit_item.show()

        menu.append(preferences_item)
        menu.append(about_item)
        menu.append(quit_item)


    def setIndicatorLabel(self,label):
        self.indicator.set_label(label,"Football Score Indicator")

    def insertMenuItem(self,widget,pos):
        self.menu.insert(widget,pos)

    def removeMenuItem(self,widget):
        self.menu.remove(widget)

    def showClicked_cb(self, widget, matchItem):
        self.indicatorLabelId = matchItem['id']
        #print "show clicked id is  :   ---   ",
        #print matchItem['id']

        # NOTE: `idle_add` is not required here as we are in callback and
        # therefore can modify Gtk data structures
        # NOTE: this function seems to be causing crash
        # take a good look at the args passed to it
        self.setIndicatorLabel(matchItem['gtkSummary'].get_label())

    def updateDataAfterInterval(self):
        while True:
            start = time.time()

            # please explain why locks are required, there are no cuncuurent threads

            self.dataLock.acquire()
            self.updateLabels()
            self.setSubMenuData()
            self.dataLock.release()
            duration = time.time() - start
            if duration < REFRESH_INTERVAL:
                # sleep if time permits
                time.sleep(REFRESH_INTERVAL-duration)

    def updateLabels(self):
        # TODO: use caching
        settings = self.configurations
        #settings = self.config.readConfigurations()
        #print settings

        leauges = get_matches_summary()
        if leauges is None:
            return
        #print " ****************************************************************\n\n"
            
        currentCount = 0
        previousLength = len(self.menu) - 3
        #print "=====================================>    ",
        #print previousLength
        #print "=====================================>    ",
        #print currentCount
        for leauge,matches in leauges.iteritems():
            # TODO: use a creator function for creating Gtk objects
            #print "----> " + leauge
            if currentCount >= previousLength :
                newLeaugeItem = Gtk.ImageMenuItem(leauge)
                newLeaugeItem.set_sensitive(False)
                if not settings['hide_leauges']:
                    GObject.idle_add(newLeaugeItem.show)
                else:
                    GObject.idle_add(newLeaugeItem.hide)
                
                GObject.idle_add(self.insertMenuItem,newLeaugeItem,currentCount)
                self.matchMenu.append(leauge)
            else:
                # %% we're using the old menuitem
                if self.menu.get_children()[currentCount].get_submenu():
                    # %% why r u doing dis?
                    # %% I am doing this since I got no way of removing the submenu from MenuItem, it orderchanges and the matchitem having submenu is changed
                    newLeaugeItem = Gtk.ImageMenuItem(leauge)
                    newLeaugeItem.set_sensitive(False)
                    if not settings['hide_leauges']:
                        GObject.idle_add(newLeaugeItem.show)
                    else:
                        GObject.idle_add(newLeaugeItem.hide)
                               
                    GObject.idle_add(self.menu.remove,self.menu.get_children()[currentCount])
                    GObject.idle_add(self.insertMenuItem,newLeaugeItem,currentCount)
                else:
                    GObject.idle_add(setMenuLabel,self.menu.get_children()[currentCount],leauge)
                    if not settings['hide_leauges']:
                        GObject.idle_add(self.menu.get_children()[currentCount].show)
                    else:
                        GObject.idle_add(self.menu.get_children()[currentCount].hide)
                
                    
            self.matchMenu[currentCount] = leauge


            currentCount += 1
            for matchInfo in matches.values():
                #print "=====================================>    ",
                #print previousLength
                #print "=====================================>    ",
                #print currentCount
                #print "---------------------------->    " , matchInfo['score_summary']

                if self.indicatorLabelId is None:
                    self.indicatorLabelId = matchInfo['id']
                if self.indicatorLabelId == matchInfo['id']:
                    if ":" in matchInfo['status']:
                        GObject.idle_add(self.setIndicatorLabel,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
                    else:
                        GObject.idle_add(self.setIndicatorLabel, matchInfo['score_summary'] + "  " + matchInfo['status'])

                if previousLength <= currentCount:
                    matchItem = self.createMatchItem(matchInfo)
                    #print "in here since previous length is less than cuncurrent count"
                    #print "\ncreating matchitem for " + matchInfo['score_summary']
                    if ":" in matchInfo['status']:
                        GObject.idle_add(matchItem['gtkSummary'].set_label,matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
                    else:
                        GObject.idle_add(matchItem['gtkSummary'].set_label,matchInfo['score_summary'] + "\n " + matchInfo['status'])
                    self.matchMenu.append(matchItem)
                    #print str(previousLength) + "----" + str(currentCount)
                    GObject.idle_add(self.insertMenuItem,matchItem['gtkSummary'],currentCount)
                    GObject.idle_add(matchItem['gtkSummary'].show)
                else:
                    widget = self.menu.get_children()[currentCount]
                    if type(self.matchMenu[currentCount]) is dict:
                        self.updateMenu(self.matchMenu[currentCount],matchInfo)
                    else:
                        widget.set_sensitive(True)
                        matchItem = self.createMatchItem(matchInfo,widget)
                        if ":" in matchInfo['status']:
                            GObject.idle_add(matchItem['gtkSummary'].set_label,matchInfo['score_summary'] + " Starts at " + matchInfo['status'])
                        else:
                            GObject.idle_add(matchItem['gtkSummary'].set_label,matchInfo['score_summary'] + "\n " + matchInfo['status'])
                        self.matchMenu[currentCount] = matchItem

                if settings['live_matches'] and 'LIVE' in self.matchMenu[currentCount]['status']:
                    GObject.idle_add(self.matchMenu[currentCount]['gtkSummary'].show)
                elif not settings['live_matches']:
                    GObject.idle_add(self.matchMenu[currentCount]['gtkSummary'].show)
                else:
                    GObject.idle_add(self.matchMenu[currentCount]['gtkSummary'].hide)
                currentCount += 1

        """
        check this pattter

        Actually this is what I told you to do because I am not able to figure this out
        """
        while currentCount < len(self.menu) - 3:
            #print "in while loop"
            #print "currentCount ----------------------------------------------> ", currentCount
            #print "sen(self.menu) --------------------------------------------> ",len(self.menu)
            #print "match menu length -----------------------------------------> ", len(self.matchMenu)
            GObject.idle_add(self.removeMenuItem, self.menu.get_children()[currentCount + 1])
            #if type(self.matchMenu[-1]) is dict:
            #  GObject.idle_add(self.removeMenuItem, self.menu.get_children()[-4])
            #else:
            #  GObject.idle_add(self.removeMenuItem,self.matchMenu[-1])

    def createMatchItem(self,matchInfo, widget=None):
        matchItem = {
          "gtkSummary":       Gtk.ImageMenuItem.new_with_label(matchInfo['score_summary'] + "\t"*3 + matchInfo['status'])
                              if widget is None else widget,
          "gtkSubMenu":       Gtk.Menu.new(),
          "gtkSetAslabel":    Gtk.MenuItem("Set as Label"),
          "gtkOpenInBrowser": Gtk.MenuItem.new_with_label("Open in Browser"),
          "gtkSeperator1":    Gtk.SeparatorMenuItem().new(),
          "gtkSeperator2":    Gtk.SeparatorMenuItem().new(),
          "gtkSeperator3":    Gtk.SeparatorMenuItem().new(),

          "gtkGoalHeading":       Gtk.MenuItem("Goals"),
          "gtkGoalData":          Gtk.MenuItem("Loading..."),
          "gtkStatus":            Gtk.MenuItem("Loading..."),
          "gtkSubMenuScoreLabel": Gtk.MenuItem("Loading"),

          "id":        matchInfo["id"],
          "leauge":    matchInfo["leauge"],
          "status":    matchInfo['status'],
          "extraInfo": matchInfo['extra_info'],
          "url":       matchInfo['url'],

        }
        matchItem['gtkSummary'].set_submenu(matchItem['gtkSubMenu'])

        matchItem['gtkSetAslabel'].connect("activate",self.showClicked_cb,matchItem)
        matchItem['gtkOpenInBrowser'].connect("activate",self.openInBrowser_cb,matchItem)

        matchItem['gtkSubMenu'].append(matchItem['gtkSetAslabel'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSeperator1'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSubMenuScoreLabel'])
        matchItem['gtkSubMenu'].append(matchItem['gtkStatus'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSeperator2'])
        matchItem['gtkSubMenu'].append(matchItem['gtkGoalHeading'])
        matchItem['gtkSubMenu'].append(matchItem['gtkGoalData'])
        matchItem['gtkSubMenu'].append(matchItem['gtkSeperator3'])
        matchItem['gtkSubMenu'].append(matchItem['gtkOpenInBrowser'])

        matchItem['gtkSubMenu'].show_all()

        return matchItem

    def openInBrowser_cb(self,widget,matchItem):
        webbrowser.open(matchItem['url'])


    def updateMenu(self,matchItem,matchInfo):
        if ":" in matchInfo['status']:
            GObject.idle_add(matchItem['gtkSummary'].set_label,matchInfo['score_summary'] + " starts at " + matchInfo['status'])
        else:
            GObject.idle_add(matchItem['gtkSummary'].set_label,matchInfo['score_summary'] + " " + matchInfo['status'])
            if 'LIVE' in matchInfo['status']:
                image = Gtk.Image()
                image.set_from_icon_name("football",1)
                GObject.idle_add(matchItem['gtkSummary'].set_image,image)
                GObject.idle_add(matchItem['gtkSummary'].set_always_show_image,True)
            else:
                GObject.idle_add(matchItem['gtkSummary'].set_always_show_image,False)

        GObject.idle_add(matchItem['gtkSubMenuScoreLabel'].set_label,matchInfo['score_summary'] )
        GObject.idle_add(matchItem['gtkStatus'].set_label,matchInfo['status'])
        GObject.idle_add(matchItem['gtkSetAslabel'].set_label,"Set as Label")
        matchItem['gtkStatus'].set_sensitive(False)

        matchItem['id'] = matchInfo['id']
        matchItem['status'] = matchInfo['status']
        matchItem['extraInfo'] = matchInfo['extra_info']
        matchItem['url'] = matchInfo['url']
        matchItem['leauge'] = matchInfo['leauge']

    def updateSubMenuLabels(self,matchId,widget):
        goals = get_match_goaldata(matchId)
        # goals
        if not goals:
            #print "goals are not available"
            GObject.idle_add(widget.set_label,"No Goals Yet...")
            return
        else:
            label = ""
            for i in goals:
                label += i.replace("<b>","").replace("</b>","").replace("<br>","") + "\n"
            GObject.idle_add(widget.set_label, label)

    def setSubMenuData(self):
        for i in self.matchMenu:
            if type(i) is dict and 'LIVE' in i['gtkStatus'].get_label():
                thread = threading.Thread(target=self.updateSubMenuLabels,args=(i['id'], i['gtkGoalData']))
                thread.start()
                # TODO: join?
                # Well, convice me to use the join

def run():
    myIndicator = FootballIndicator()
    myIndicator.main()

if __name__ == "__main__":
    print ("use 'footnallscore_indicator to run the applet")

# TODO: move to scraper file

def setMenuLabel(widget, label):
    widget.set_label(label)

def preferences(widget,function):
    window = PreferencesWindow()
    window.display(function)

def about(widget):
    dialog = Gtk.AboutDialog.new()
    dialog.set_transient_for(widget.get_parent().get_parent())

    dialog.set_program_name("Football Score Indicator")
    dialog.add_credit_section("Authors:", ['Nishant Kukreja (github.com/rubyace71697)', 'Abhishek (github.com/rawcoder)'])

    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_version(VERSION_STR)
    dialog.set_website("https://github.com/rawcoder/football-score-applet")
    dialog.set_website_label("Github page")
    #dialog.set_logo_icon_name('football.png')
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(sys.prefix + "/share/pixmaps/football.png", 50, 50)
    dialog.set_logo(pixbuf)
    dialog.run()
    dialog.destroy()

def quit(widget):
    print "*** quit clicked ***"
    Gtk.main_quit()


# vim: ts=2
