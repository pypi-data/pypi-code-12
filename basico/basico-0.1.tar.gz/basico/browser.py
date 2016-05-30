#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: browser.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Browse module
#~ Source code borrowed from:
#~ https://raw.githubusercontent.com/jaka/browser2/master/browser2
#~ https://github.com/jaka
#~ but adapted to Gtk3

from gettext import gettext as _

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import WebKit


class BrowserPage(WebKit.WebView):

  def __init__(self):
    WebKit.WebView.__init__(self)
    settings = self.get_settings()
    settings.set_property('enable-developer-extras', True)
    settings.set_property('enable-default-context-menu', True)

    settings.set_property('default-encoding', 'utf-8')
    settings.set_property('enable-private-browsing', True)
    settings.set_property('enable-html5-local-storage', True)

    # disable plugins, like Adobe Flash and Java
    settings.set_property('enable-plugins', True)

    # scale other content besides from text as well
    self.set_full_content_zoom(True)

class TabLabel(Gtk.HBox):
  """A class for Tab labels"""

  __gsignals__ = {
    'close': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_OBJECT,))
  }

  def __init__(self, title, scrolled_window):
    """initialize the tab label"""

    Gtk.HBox.__init__(self, False, 4)
    self.title = title
    self.scrolled_window = scrolled_window
    self.label = Gtk.Label(title)
    self.label.props.max_width_chars = 30
    #~ self.label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
    self.label.set_alignment(0.0, 0.5)

    close_image = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
    close_button = Gtk.Button()
    close_button.set_relief(Gtk.ReliefStyle.NONE)
    close_button.set_image(close_image)
    close_button.connect('clicked', lambda x: self.emit('close', self.scrolled_window))

    self.pack_start(self.label, True, True, 0)
    self.pack_start(close_button, False, False, 0)

    self.connect('style-set', self._tab_label_style_set)

  def _tab_label_style_set(self, tab_label, style):
    try:
        context = tab_label.get_pango_context()
        metrics = context.get_metrics(tab_label.style.font_desc, context.get_language())
        char_width = metrics.get_approximate_digit_width()
        (width, height) = Gtk.icon_size_lookup(Gtk.ICON_SIZE_MENU)
        tab_label.set_size_request(10 * Pango.PIXELS(char_width) + 2 * width,
        Pango.PIXELS(metrics.get_ascent() + metrics.get_descent()) + 4)
    except: pass

class ContentPane(Gtk.Notebook):

  __gsignals__ = {
    'focus-entry': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    'update-title': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_OBJECT, GObject.TYPE_STRING, GObject.TYPE_STRING)),
    }

  def __init__(self, app):
    """initialize the content pane"""
    Gtk.Notebook.__init__(self)
    self.app = app
    self.props.scrollable = True
    self.set_show_tabs(True)
    self.popup_enable()
    #~ self.set_property('homogeneous', True)
    self.set_show_border(True)
    self.connect('switch-page', self._switch_page)

    self.show_all()
    self._hovered_uri = None

  def new_tab(self, url = None, show_new = True, web_view = None):
    """Creates a new page in a new tab"""

    if web_view:
      browser = web_view
    else:
      browser = BrowserPage()

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.AUTOMATIC
    scrolled_window.props.vscrollbar_policy = Gtk.PolicyType.AUTOMATIC
    scrolled_window.title = None
    scrolled_window.url = None

    browser.connect('title-changed', self._title_changed, scrolled_window)
    browser.connect('load-committed', self._url_changed, scrolled_window)
    browser.connect('load-finished', self._load_finished, scrolled_window)
    browser.connect('hovering-over-link', self._hovering_over_link)

    # disable file chooser
    #~ browser.connect('run-file-chooser', returntrue)

    # disable file transfering (downloading)
    #~ browser.connect('download-requested', returntrue)

    # disable printing
    #~ browser.connect('print-requested', returntrue)

    browser.connect('create-web-view', self._new_web_view_request)
    browser.connect('button-press-event', self._on_button_press_event)

    scrolled_window.add(browser)
    scrolled_window.show_all()

    label = TabLabel(url, scrolled_window)
    label.connect('close', self.close_tab)
    label.show_all()

    new_tab_number = self.append_page(scrolled_window, label)
    #~ self.set_tab_label_packing(scrolled_window, False, True, Gtk.PACK_START)
    self.set_tab_label(scrolled_window, label)

    #~ self.set_show_tabs(self.get_n_pages() > 1)
    self.show_all()

    if url:
      scrolled_window.url = url
      browser.load_uri(url)
    else:
      scrolled_window.title = "New Tab"
      scrolled_window.url = ""
      label.label.set_label("New Tab")

    if show_new:
      self.set_current_page(new_tab_number)
      if not url:
        self.emit('focus-entry')


  def close_tab(self, label, scrolled_window):
    page_num = self.page_num(scrolled_window)
    if page_num != -1:
      browser = scrolled_window.get_child()
      browser.destroy()
      self.remove_page(page_num)
    #~ self.set_show_tabs(self.get_n_pages() > 1)

  def close_current_tab(self):
    if (self.get_n_pages() > 1):
        self.close_tab(None, self.get_nth_page(self.get_current_page()))

  def go_back(self):
    child = self.get_nth_page(self.get_current_page())
    view = child.get_child()
    view.go_back()

  def go_forward(self):
    child = self.get_nth_page(self.get_current_page())
    view = child.get_child()
    view.go_forward()

  def refresh(self):
    child = self.get_nth_page(self.get_current_page())
    view = child.get_child()
    view.reload()

  def zoom_in(self):
    """Zoom into the page"""
    child = self.get_nth_page(self.get_current_page())
    view = child.get_child()
    view.zoom_in()

  def zoom_out(self):
    """Zoom out of the page"""
    child = self.get_nth_page(self.get_current_page())
    view = child.get_child()
    view.zoom_out()

  def load (self, text):
    """Load the given uri in the current web view"""

    child = self.get_nth_page(self.get_current_page())
    view = child.get_child()
    view.open(text)

  def _on_button_press_event(self, widget, event):
    if event.type == Gdk.EventType.BUTTON_PRESS and self._hovered_uri:
      if event.button == 2:
        self.new_tab(self._hovered_uri, False)
        return True

  def _hovering_over_link(self, view, title, uri):
    self._hovered_uri = uri

  def _switch_page(self, notebook, page, page_num):
    scrolled_window = self.get_nth_page(page_num)
    self._update_app(scrolled_window)

  def _new_web_view_request(self, web_view, web_frame):
    view = BrowserPage()
    self.new_tab(web_view = view)
    return view

  def _get_title(self, web_view):
    title = web_view.get_title()
    if not title:
      frame = web_view.get_main_frame()
      title = frame.props.title
      if not title:
        title = frame.get_uri()
    return title

  def _load_finished(self, web_view, frame, scrolled_window):
    scrolled_window.title = self._get_title(web_view)
    #~ print (scrolled_window.title)
    scrolled_window.url = frame.get_uri()
    if web_view.get_can_focus():
      web_view.grab_focus()
      try:
        # FIXME: this only MUST BE executed when load http://launchpad.support.sap.com
        sap = self.app.get_service('SAP')
        SUSER = sap.get_config_value('CNF_SAP_SUser')
        SPASS = sap.get_config_value('CNF_SAP_SPass')
        web_view.execute_script("document.getElementById('j_username').value='%s';" % SUSER)
        web_view.execute_script("document.getElementById('j_password').value='%s';" % SPASS)
        web_view.execute_script("document.getElementById('logOnFormSubmit').click();")
      except Exception as error:
        print(error)


  def _title_changed(self, web_view, frame, title, scrolled_window):
    scrolled_window.title = title
    scrolled_window.url = frame.get_uri()
    self._update_title(scrolled_window)

  def _url_changed(self, web_view, frame, scrolled_window):
    scrolled_window.title = self._get_title(web_view)
    scrolled_window.url = frame.get_uri()
    self._update_title(scrolled_window)

  def _update_title(self, scrolled_window):
    label = self.get_tab_label(scrolled_window)
    label.label.set_label(scrolled_window.title)
    if self.page_num(scrolled_window) == self.get_current_page():
      self._update_app(scrolled_window)

  def _update_app(self, scrolled_window):
    title, url = scrolled_window.title, scrolled_window.url
    self.emit('update-title', scrolled_window.get_child(), title, url)

class WebToolbar(Gtk.Toolbar):

  __gsignals__ = {
    "go-back-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    "go-forward-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    "go-refresh-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    "go-home-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    "zoom-in-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    "zoom-out-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    "load-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "new-tab-requested": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
  }

  def __init__(self, location_enabled=True, toolbar_enabled=True):
    Gtk.Toolbar.__init__(self)

    self.set_style(Gtk.ToolbarStyle.ICONS)
    self.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)

    self.back_button = Gtk.ToolButton(Gtk.STOCK_GO_BACK)
    self.forward_button = Gtk.ToolButton(Gtk.STOCK_GO_FORWARD)
    self.refresh_button = Gtk.ToolButton(Gtk.STOCK_REFRESH)
    self.home_button = Gtk.ToolButton(Gtk.STOCK_HOME)

    self.back_button.connect('clicked', lambda x: self.emit('go-back-requested'))
    self.forward_button.connect('clicked', lambda x: self.emit('go-forward-requested'))
    self.refresh_button.connect('clicked', lambda x: self.emit('go-refresh-requested'))
    self.home_button.connect('clicked', lambda x: self.emit('go-home-requested'))

    self.add(self.back_button)
    self.add(self.forward_button)
    self.add(self.refresh_button)
    self.add(self.home_button)

    if True:
      self.add(Gtk.SeparatorToolItem())
      self.entry = Gtk.Entry()
      self.entry.connect('activate', lambda x: self.emit('load-requested', self.entry.props.text))
      entry_item = Gtk.ToolItem()
      entry_item.set_expand(True)
      entry_item.add(self.entry)
      self.entry.show()
      self.insert(entry_item, -1)
      entry_item.show()

    self.add(Gtk.SeparatorToolItem())
    self.zoom_in_button = Gtk.ToolButton(Gtk.STOCK_ZOOM_IN)
    self.zoom_out_button = Gtk.ToolButton(Gtk.STOCK_ZOOM_OUT)

    self.zoom_in_button.connect('clicked', lambda x: self.emit('zoom-in-requested'))
    self.zoom_out_button.connect('clicked', lambda x: self.emit('zoom-out-requested'))

    self.add(self.zoom_in_button)
    self.add(self.zoom_out_button)

    if True:
      self.add(Gtk.SeparatorToolItem())
      self.addTabButton = Gtk.ToolButton(Gtk.STOCK_ADD)
      self.addTabButton.connect('clicked', lambda x: self.emit('new-tab-requested'))
      self.insert(self.addTabButton, -1)
      self.addTabButton.show()

class WebBrowser(Gtk.Box):

  def __init__(self, app):
    Gtk.Box.__init__(self)
    self.app = app
    self.start_url = 'https://launchpad.support.sap.com'

    self.toolbar = WebToolbar()
    self.content_tabs = ContentPane(app)

    self.content_tabs.connect('focus-entry', lambda x: self.toolbar.entry.grab_focus())
    self.content_tabs.connect('update-title', self._update_title)

    self.toolbar.connect('new-tab-requested', lambda x: self.content_tabs.new_tab(None, True))
    self.toolbar.connect('go-back-requested', lambda x: self.content_tabs.go_back())
    self.toolbar.connect('go-forward-requested', lambda x: self.content_tabs.go_forward())
    self.toolbar.connect('go-refresh-requested', lambda x: self.content_tabs.refresh())
    self.toolbar.connect('go-home-requested', lambda x: self.content_tabs.load(self.start_url))
    self.toolbar.connect('zoom-in-requested', lambda x: self.content_tabs.zoom_in())
    self.toolbar.connect('zoom-out-requested', lambda x: self.content_tabs.zoom_out())
    self.toolbar.connect('load-requested', self.load_requested)

    vbox = Gtk.VBox(spacing = 0)
    vbox.pack_start(self.toolbar, False, False, False)
    vbox.pack_start(self.content_tabs, True, True, True)
    self.pack_start(vbox, True, True, True)
    #~ self.connect('destroy', self.quit)
    #~ self.connect('key-press-event', self._key_pressed)

    #~ self.icon_theme = Gtk.icon_theme_get_default()
    #~ self.set_icon(self.icon_theme.load_icon("stock_internet", 16, 0))

    #~ self.set_default_size(800, 600)

    self.show_all()
    self.content_tabs.new_tab(self.start_url, True)



  #~ def quit(self, window):
    #~ num_pages = self.content_tabs.get_n_pages()
    #~ while num_pages != -1:
      #~ scrolled_window = self.content_tabs.get_nth_page(num_pages)
      #~ if scrolled_window:
        #~ web_view = scrolled_window.get_child()
        #~ web_view.destroy()
      #~ num_pages = num_pages - 1
    #~ self.destroy()
    #~ Gtk.main_quit()


  def get_content_tabs(self):
      return self.content_tabs


  def load_requested(self, entry, text):
    if not text:
      return
    try:
      text.index("://")
    except:
      if (' ' in text and '/' not in text) or ('.' not in text):
        text = 'https://www.google.si/search?q=' + text
      else:
        text = "http://" + text
    self.content_tabs.load(text)


  def _update_title(self, notebook, web_view, title, url):
    #~ if not title is None:
      #~ self.set_title(_("%s") % title)
    if not url is None:
      self.toolbar.entry.set_text(url)
    self.toolbar.back_button.set_sensitive(web_view.can_go_back())
    self.toolbar.forward_button.set_sensitive(web_view.can_go_forward())

  def _key_pressed(self, widget, event):
    mapping = {
     'r': self.content_tabs.refresh,
     'w': self.content_tabs.close_current_tab,
     't': self.content_tabs.new_tab,
     'l': self.toolbar.entry.grab_focus
    }
    if event.state & Gdk.ModifierType.CONTROL_MASK and Gdk.keyval_name(event.keyval).lower() in mapping:
      mapping[Gdk.keyval_name(event.keyval)]()
    elif event.state & Gdk.ModifierType.MOD1_MASK:
      if Gdk.keyval_name(event.keyval) == 'F4':
        self.quit(self)

def returntrue(*args):
  return True

#~ if __name__ == "__main__":
  #~ webbrowser = WebBrowser()
  #~ Gtk.main()
