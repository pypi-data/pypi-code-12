#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: sap.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: SAP service

import sys
import time
import json
import traceback
from shutil import which
from cgi import escape
import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#~ from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import feedparser


from .service import Service

# Default settings for SAP module
LOGIN_PAGE_URL = "https://accounts.sap.com"
LOGOUT_PAGE_URL = "https://accounts.sap.com/ui/logout"
ODATA_NOTE_URL = "https://launchpad.support.sap.com/services/odata/svt/snogwscorr/TrunkSet(SapNotesNumber='%s',Version='0',Language='E')" #$expand=LongText" #?$expand=LongText,RefTo,RefBy"
SAP_NOTE_URL = "https://launchpad.support.sap.com/#/notes/%s"
TIMEOUT = 5


class SAP(Service):
    def initialize(self):
        '''
        Setup AppLogic Service
        '''
        self.windriver = None
        self.sapnotes = {}
        self.stats = {}
        self.stats['maincomp'] = {}
        self.stats['cats'] = {}
        self.stats['component'] = set()
        self.stats['category'] = set()
        self.stats['priority'] = set()
        self.stats['type'] = set()
        self.stats['version'] = set()
        #~ self.stats['releaseon'] = set()
        self.__init_config_section()


    def __init_config_section(self):
        self.config = self.app.get_config()
        if self.config.has_section(self.section):
            options = self.config.options(self.section)
            if len(options) == 0:
                self.log.debug("Section %s empty. Initializing with default values" % self.section)
                settings = self.get_default_settings()
                self.config[self.section] = settings
                self.save_config()


    def ajax_complete(self, driver):
        try:
            return 0 == driver.execute_script("return jQuery.active")
        except WebDriverException:
            pass


    def wait_for_page_load(self, driver):
        driver.implicitly_wait(0.5)
        try:
            WebDriverWait(driver, 30).until(lambda d: (d.execute_script('return document.readyState') == 'complete'))
            #~ WebDriverWait(driver, 30).until(lambda d: (d.execute_script('return window.performance.timing.loadEventEnd') > 0))
        except Exception as error:
            #~ self.log.warning(self.get_traceback())
            self.log.warning(error)
            time.sleep(5)


    def check_webdriver(self):
        found = False
        driver = self.get_webdriver()
        if driver:
            driver.quit()
            found = True

        return found


    def build_stats(self, bag=None):
        if bag is None:
            bag = self.sapnotes
        self.dstats = {}
        self.compstats = {}
        alltasks = set()

        for sid in bag:
            # tasks
            try:
                tasks = self.sapnotes[sid]['tasks']
                for task in tasks:
                    alltasks.add(task)
            except: pass
            self.tasks = self.app.get_service('Tasks')
            self.tasks.save_tasks_from_stats(alltasks)

            # components
            compkey = self.sapnotes[sid]['componentkey']
            comptxt = self.sapnotes[sid]['componenttxt']
            component = escape("%s (%s)" % (compkey, comptxt))
            sep = compkey.find('-')
            if sep > 0:
                maincomp = compkey[0:sep]
            else:
                maincomp = compkey

            # categories
            category = category = escape(self.sapnotes[sid]['category'])
            try:
                cont = self.stats['cats'][category]
                self.stats['cats'][category] = cont + 1
            except:
                self.stats['cats'][category] = 1

            # Build al (sub)keys from given component key
            # useful for display stats with pygal
            compkeys = compkey.split('-')
            total = len(compkeys)
            key = ''
            i = 0
            for subkey in compkeys:
                key = key + '-' + subkey
                if key[:1] == '-':
                    key = key[1:]

                # update stats
                try:
                    count = self.compstats[key]
                    self.compstats[key] = count + 1
                except Exception as error:
                    self.compstats[key] = 1

            try:
                cont = self.stats['maincomp'][maincomp]
                self.stats['maincomp'][maincomp] = cont + 1
            except:
                self.stats['maincomp'][maincomp] = 1

            category = escape(self.sapnotes[sid]['category'])
            priority = escape(self.sapnotes[sid]['priority'])
            ntype = escape(self.sapnotes[sid]['type'])
            version = escape(self.sapnotes[sid]['version'])
            releaseon = escape(self.sapnotes[sid]['releaseon'])
            self.stats['component'].add(component)
            self.stats['category'].add(category)
            self.stats['priority'].add(priority)
            self.stats['type'].add(ntype)
            self.stats['version'].add(version)
            #~ self.stats['releaseon'].add(releaseon)
            #~ self.stats[''].add(version)
        #~ self.log.debug(self.compstats)
        #~ self.log.debug("==")
        #~ self.log.debug(self.stats)
        self.log.debug(self.stats['maincomp'])



    def get_stats(self):
        return self.stats


    def download_note(self, sapnote, driver):
        downloaded = False
        try:
            self.log.debug("Downloading SAP Note %s" % sapnote)
            self.log.debug("Waiting for page %s..." % (ODATA_NOTE_URL % sapnote))
            driver.get(ODATA_NOTE_URL % sapnote)
            #wait for ajax items to load
            #~ WebDriverWait(driver, 60).until(self.ajax_complete,  "Timeout waiting for page to load")
            time.sleep(5)
            self.log.debug("Page loaded")
            downloaded = self.add_note(sapnote, driver.page_source)
        except:
            self.log.error("SAP Note %s coud not be downloaded" % sapnote)

        return downloaded


    def connect(self):
        driver = self.get_webdriver()
        if driver is not None:
            self.login_sso(driver)
            self.log.debug ("Connectig to SAP...")

        return driver


    def get_default_settings(self):
        settings = {}
        settings['CNF_SAP_SUser'] = 'SXXXXXXXXXX'
        settings['CNF_SAP_SPass'] = 'MyP455w0rD'
        settings['CNF_SAP_Login'] = LOGIN_PAGE_URL
        settings['CNF_SAP_Logout'] = LOGOUT_PAGE_URL
        settings['CNF_SAP_OData_Notes'] = ODATA_NOTE_URL
        settings['CNF_SAP_Notes_URL'] = SAP_NOTE_URL
        settings['CNF_SAP_CONN_TIMEOUT'] = TIMEOUT

        return settings


    def get_custom_settings(self):
        settings = {}
        settings['CNF_SAP_SUser'] = self.get_config_value('CNF_SAP_SUser')
        settings['CNF_SAP_SPass'] = self.get_config_value('CNF_SAP_SPass')
        settings['CNF_SAP_Login'] = self.get_config_value('CNF_SAP_Login')
        settings['CNF_SAP_Logout'] = self.get_config_value('CNF_SAP_Logout')
        settings['CNF_SAP_OData_Notes'] = self.get_config_value('CNF_SAP_OData_Notes')
        settings['CNF_SAP_Notes_URL'] = self.get_config_value('CNF_SAP_Notes_URL')

        return settings


    def get_webdriver(self):
        '''
        FIXME: check supported webdrivers and return the webdriver
        which best fits:
        1.- PhantomJS
        2.- Firefox
        '''

        driver = None
        self.log.debug("Loading webdriver...")

        phantomjs = which('phantomjs')

        if phantomjs is not None:
            driver = webdriver.PhantomJS()
            self.log.debug("PhantomJS driver available")
        else:
            driver = webdriver.Firefox()
            self.log.debug("Firefox driver available")

        return driver

        #~ if sys.platform == 'linux':
            #~ # First we try with PhantomJS
            #~ try:
                #~ driver = webdriver.PhantomJS()
                #~ self.log.debug("PhantomJS available")
            #~ except:
                #~ self.log.warning("PhantomJS not available")
                #~ try:
                    #~ driver = webdriver.Firefox()
                    #~ self.log.debug ("Firefox available")
                #~ except:
                    #~ self.log.error("Firefox not available")
                    #~ driver = None
        #~ elif sys.platform == 'win32':
            #~ try:
                #~ driver = webdriver.Ie("C:\\windows\\system32\\IEDriverServer.exe")
                #~ self.log.debug ("IE available")
            #~ except:
                #~ self.log.error("IE not available")
                #~ driver = None
        #~ return driver


    def logout(self, driver):
        driver.get(LOGOUT_PAGE_URL)
        driver.quit()


    def login_sso(self, driver):
        '''
        Login into SAP Support
        '''
        self.log.debug("Waiting for page...")
        myuser = self.get_config_value('CNF_SAP_SUser')
        mypass = self.get_config_value('CNF_SAP_SPass')
        myloginpage = self.get_config_value('CNF_SAP_Login')

        driver.get(myloginpage)
        self.wait_for_page_load(driver)
        self.log.debug("Page loaded")
        username = driver.find_element_by_id('j_username')
        username.send_keys(myuser)
        password = driver.find_element_by_id('j_password')
        password.send_keys(mypass)
        login = driver.find_element_by_id('logOnFormSubmit')
        login.click()
        # FIXME: Wait time as editable property
        #~ time.sleep(5)


    def feedparser_parse(self, thing):
        try:
            return feedparser.parse(thing)
        except TypeError:
            if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                return feedparser.parse(thing)
            else:
                self.log.error(self.get_traceback())
                raise



    def get_notes(self):
        '''
        Return all sapnotes
        '''
        return self.sapnotes


    def get_total(self):
        '''
        Return total sapnotes
        '''
        return len(self.sapnotes)


    def load_notes(self):
        '''
        If notes.json exists, load notes
        '''
        try:
            fnotes = self.get_file('SAP')
            with open(fnotes, 'r') as fp:
                self.sapnotes = json.load(fp)
                self.log.debug ("Loaded %d notes" % len(self.sapnotes))
        except Exception as error:
            self.log.info("SAP Notes database not found. Creating a new one")
            self.save_notes()


    def get_node(self, sid):
        try:
            return self.sapnotes[sid]
        except Exception as KeyError:
            return None


    def get_note(self, note):
        '''
        Get xml from SAP Support Notes service
        '''
        self.driver.get(ODATA_NOTE_URL % note)
        return self.driver.page_source


    def add_note(self, sapnote, content):
        '''
        Get header details from SAP Note
        '''
        try:
            f= self.feedparser_parse(content)
            f = feedparser.parse(content)
            sid = f.entries[0].d_sapnotesnumber
            self.sapnotes[sid] = {}
            self.sapnotes[sid]['id'] = sid
            self.sapnotes[sid]['componentkey'] = f.entries[0].d_componentkey
            self.sapnotes[sid]['componenttxt'] = f.entries[0].d_componenttext
            self.sapnotes[sid]['category'] = f.entries[0].d_category_detail['value']
            self.sapnotes[sid]['language'] = f.entries[0].d_languagetext_detail['value']
            self.sapnotes[sid]['title'] = f.entries[0].d_title_detail['value']
            self.sapnotes[sid]['priority'] = f.entries[0].d_priority_detail['value']
            self.sapnotes[sid]['releaseon'] = f.entries[0].d_releasedon
            self.sapnotes[sid]['type'] = f.entries[0].d_type_detail['value']
            self.sapnotes[sid]['version'] = f.entries[0].d_version_detail['value']
            self.sapnotes[sid]['feedupdate'] = f.entries[0].updated
            self.sapnotes[sid]['bookmark'] = False
            self.log.info ("Added SAP Note %s" % sapnote)
            return True
        except Exception as error:
            self.log.error("SAP Note %s could not be analyzed" % sapnote)
            return False


    def browse_notes(self, sapnotes):
        driver = webdriver.Firefox()
        self.login_sso(driver)
        for sapnote in sapnotes:
            self.log.debug("Browsing SAP Note %s" % sapnote)
            body = driver.find_element_by_tag_name("body")
            body.send_keys(Keys.CONTROL + 't')
            driver.get(SAP_NOTE_URL % sapnote)
            self.wait_for_page_load(driver)


    def save_notes(self, filename='', bag={}):
        '''
        Save SAP Notes to file
        '''
        if len(filename) == 0:
            filename = self.get_file('SAP')
            bag = self.sapnotes

        fnotes = open(filename, 'w')
        json.dump(bag, fnotes)
        fnotes.close()
        self.log.info ("Saved %d notes to %s" % (len(bag), filename))




    def apply_preferences(self, *args):
        self.gui = self.app.get_service('GUI')
        settings = self.get_default_settings()
        new_settings = {}
        for key in settings:
            widget = self.gui.get_widget(key)
            value = widget.get_text()
            new_settings[key] = value
        #~ self.log.debug(new_settings)
        self.config[self.section] = new_settings
        self.save_config()
        self.log.debug("Settings saved")



    def default_preferences(self, *args):
        self.gui = self.app.get_service('GUI')
        settings = self.get_default_settings()
        for key in settings:
            widget = self.gui.get_widget(key)
            widget.set_text(settings[key])

        #~ self.log.debug(settings)
        self.config[self.section] = settings
        self.save_config()
        infobar = self.gui.get_widget('infobar')
        infobar.set_markup("<b>Settings reverted to default</b>")


    def get_linked_projects(self, sapnote):
        try:
            projects = self.sapnotes[sapnote]['projects']
        except Exception as error:
            projects = []

        return projects


    def get_linked_tasks(self, sapnote):
        try:
            tasks = self.sapnotes[sapnote]['tasks']
        except Exception as error:
            tasks = []
        self.log.debug("Tasks: %s" % tasks)
        return tasks


    #~ def link_to_project(self, sapnotes, projects):
        #~ for sapnote in sapnotes:
            #~ try:
                #~ self.sapnotes[sapnote]['projects'] = projects
                #~ self.log.debug("Linked SAP Note %s to project(s): %s" % (sapnote, projects) )
            #~ except:
                #~ self.log.error(self.get_traceback())


    def link_to_task(self, sapnotes, tasks):
        for sapnote in sapnotes:
            try:
                self.sapnotes[sapnote]['tasks'] = tasks
                self.log.info("Linked SAP Note %s to task(s): %s" % (sapnote, tasks) )
            except:
                self.log.error(self.get_traceback())


    def import_sapnotes(self, bag):
        for sid in bag:
            # Check if SAP Note exists in main database
            found = self.get_node(sid)
            if found is None:
                self.sapnotes[sid] = bag[sid]
            else:
                # Import only tasks
                try:
                    imptasks = bag[sid]['tasks']
                    tasks = self.sapnotes[sid]['tasks']
                    tasks.extend(imptasks)
                    self.sapnotes[sid]['tasks'] = tasks
                except: pass
                # Import other metadata


    def set_bookmark(self, sapnotes):
        for sapnote in sapnotes:
            self.log.info("SAP Note %s bookmarked: True" % sapnote)
            self.sapnotes[sapnote]['bookmark'] = True
        self.save_notes()


    def set_no_bookmark(self, sapnotes):
        for sapnote in sapnotes:
            self.log.info("SAP Note %s bookmarked: False" % sapnote)
            self.sapnotes[sapnote]['bookmark'] = False
        self.save_notes()


    def is_bookmark(self, sapnote):
        try:
            return self.sapnotes[sapnote]['bookmark']
        except:
            return False


    def delete_sapnote(self, sapnote):
        deleted = False
        try:
            del (self.sapnotes[sapnote])
            deleted = True
        except:
            deleted = False

        return deleted


    def run(self):
        self.load_notes()
        self.build_stats()


    def quit(self):
        self.driver.quit()


    def end(self):
        self.save_notes()

