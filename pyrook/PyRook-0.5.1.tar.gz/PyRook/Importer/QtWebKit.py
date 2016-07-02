try:
    from PyQt5.QtWebKitWidgets import *
    from PyQt5.QtWebKit import *
except ImportError:
    try:
        from PyQt4.QtWebKit import *
    except RuntimeError:
        # this catches the case where PyQt5 is available and loaded, but it
        # doesn't provide WebKit, but PyQt4 *does*
        raise ImportError
