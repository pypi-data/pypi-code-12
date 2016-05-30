import signal
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject

import queue
import _thread as thread
APPINDICATOR_ID = 'myappindicator'

def build_menu():
    menu = gtk.Menu()
    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu
 
def quit(source):
    gtk.main_quit()

def main():
    # indicator = appindicator.Indicator.new(APPINDICATOR_ID, 'whatever', appindicator.IndicatorCategory.SYSTEM_SERVICES)
    # indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    # indicator.set_menu(build_menu())
    # GObject.threads_init()

    gdk.threads_enter()
    gtk.main()
    gdk.threads_leave()

def main_t():
    thread.start_new_thread(main, (),)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    gdk.threads_init()
    main_t()
    import time
    while 1:
        # time.sleep(20)
        pass
