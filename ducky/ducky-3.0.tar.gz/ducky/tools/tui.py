import curses
import logging
import sys
import time

from curtsies import fsarray, fmtstr, FullscreenWindow
from curtsies.window import FIRST_COLUMN
from functools import partial
from six import itervalues

RED = partial(fmtstr, fg = 'red')
GREEN = partial(fmtstr, fg = 'green')
BLUE = partial(fmtstr, fg = 'blue')
GRAY = partial(fmtstr, fg = 'gray')


COLOR_DISABLED = GRAY
COLOR_ENABLED  = GREEN
COLOR_FOCUS    = RED

class Widget(object):
  def __init__(self, width = None, height = None, left = None, top = None, enabled = False, visible = True, logger = None):
    super(Widget, self).__init__()

    self.logger = logger or logging.getLogger()

    self.logger.debug('%s.__init__: width=%d, height=%d, left=%d, top=%d, enabled=%s, visible=%s', self.__class__.__name__, width, height, left, top, enabled, visible)

    assert width is not None
    assert height is not None
    assert left is not None
    assert top is not None

    self.width  = width
    self.height = height
    self.left   = left
    self.top    = top

    self.handle = None

    self._enabled      = enabled
    self._visible      = visible
    self._needs_redraw = False
    self._focus        = False

  def on_needs_redraw(self, value):
    self._needs_redraw = value
    return True

  def on_focus(self, value):
    self._focus = value
    self.needs_redraw = True
    return True

  def on_enabled(self, value):
    self._enabled = value
    self.needs_redraw = True
    return True

  def on_visible(self, value):
    self._visible = value
    if value is True:
      self.needs_redraw = True
    return True

  needs_redraw = property(lambda self: self._needs_redraw, lambda self, value: self.on_event(('needs_redraw', value)))
  focus = property(lambda self: self._focus, lambda self, value: self.on_event(('focus', value)))
  enabled = property(lambda self: self._enabled, lambda self, value: self.on_event(('enabled', value)))
  visible = property(lambda self: self._visible, lambda self, value: self.on_event(('visible', value)))

  def attach_handle(self, handle):
    self.handle = handle

  def _deliver_local_event(self, e):
    if isinstance(e, tuple):
      name, value = e
      return getattr(self, 'on_%s' % name)(value)

    return None

  def on_event(self, e):
    if self._deliver_local_event(e) is True:
      return True

    handler = 'on_%s' % e
    if not hasattr(self, handler):
      return False

    return getattr(self, handler)(e)

  def clear(self):
    self.logger.debug('%s.clear', self.__class__.__name__)

    self.handle.clear()

  def erase(self):
    self.logger.debug('%s.erase', self.__class__.__name__)

    self.handle.erase()

  def border_color(self):
    self.logger.debug('%s.border_color: focus=%s, enabled=%s', self.__class__.__name__, self.focus, self.enabled)

    return curses.color_pair(2 if self.focus is True else (1 if self.enabled is True else 0))

  def apply_border(self):
    self.logger.debug('%s.apply_border: %s %s', self.__class__.__name__, self.handle, self.border_color())

    self.handle.attron(self.border_color())
    self.handle.border('|', '|', '-', '-', '+', '+', '+', '+')
    self.handle.attroff(self.border_color())

  def do_draw(self):
    raise NotImplementedError()

  def draw(self):
    self.logger.debug('%s.draw', self.__class__.__name__)

    self.do_draw()
    self.apply_border()
    self.handle.noutrefresh()
    self.needs_redraw = False

  def do_update(self, model):
    raise NotImplementedError()

  def update(self, model):
    self.logger.debug('%s.draw', self.__class__.__name__)

    if self.visible is not True:
      return

    self.do_update(model)

    if self.needs_redraw is not True:
      return

    self.draw()

class Container(Widget):
  def __init__(self, *args, **kwargs):
    super(Container, self).__init__(*args, **kwargs)

    self._children = []

  def __getitem__(self, key):
    return self._children[key]

  def __setitem__(self, key, item):
    self._children[key] = item
    self.dirty = True

  def __delitem__(self, key):
    del self._children[key]
    self.dirty = True

  def __iter__(self):
    i = 0
    try:
      while True:
        v = self[i]
        yield v
        i += 1
    except IndexError:
      return

  def append(self, item):
    self._children.append(item)

  def remove(self, item):
    self._children.remove(item) 

  def on_event(self, e):
    if self._deliver_local_event(e) is True:
      return True

    for widget in self:
      if widget.focus is not True:
        continue

      return widget.on_event(e)

    return None

class Window(Container):
  def __init__(self, title = None, **kwargs):
    super(Window, self).__init__(**kwargs)

    assert title is not None

    self.title = title

  def __repr__(self):
    return '<%s: title="%s">' % (self.__class__.__name__, self.title)

  def apply_border(self):
    super(Window, self).apply_border()

    self.handle.addstr(0, 2, ' %s ' % self.title)

class Button(Widget):
  def __init__(self, width, label, on_click = None, **kwargs):
    super(Button, self).__init__(width, 3, **kwargs)

    self.label = label
    self.on_click = on_click

  def __repr__(self):
    return '<%s: %s>' % (self.__class__.__name__, self.label)

  def on_Enter(self, e):
    if self.on_click is not None:
      self.on_click(e)

    return True

  def do_update(self, model):
    return True

  def do_draw(self):
    self.handle.addstr(self.top + 2, self.left + 2, self.label)

class Page(Container):
  def __init__(self, name = None, *args, **kwargs):
    kwargs['width'] = 0
    kwargs['height'] = 0
    kwargs['left'] = 0
    kwargs['top'] = 0

    super(Page, self).__init__(*args, **kwargs)

    assert name is not None

    self.name = name

  def __repr__(self):
    return '<%s: name=%s, widgets=[%s]>' % (self.__class__.__name__, self.name, ', '.join([repr(widget) for widget in self]))

class Screen(Container):
  def __init__(self, width = None, height = None, logger = None):
    super(Screen, self).__init__(width = width, height = height, left = 0, top = 0, logger = logger)

    self.pages = {}
    self.current_page = None

  def __repr__(self):
    return '<%s>' % self.__class__.__name__

  def add_page(self, page):
    self.logger.debug('%s.add_page: page=%r', self.__class__.__name__, page)

    assert page.name not in self.pages

    self.pages[page.name] = page

  def set_page(self, name):
    self.logger.debug('%s.set_page: name=%s', self.__class__.__name__, name)

    assert name in self.pages

    self.current_page = self.pages[name]

  def commit(self):
    self.logger.debug('%s.commit', self.__class__.__name__)

    curses.doupdate()

  def on_event(self, e):
    self.logger.debug('%s.on_event: e=%r', self.__class__.__name__, e)

    if e == '<Ctrl-j>':
      e = 'Enter'

    if self._deliver_local_event(e) is True:
      return True

    v = False

    if self.current_page is not None:
      v = self.current_page.on_event(e)

    if v is not True:
      print >> sys.stderr, 'Unhandled event: e=%s' % e

  def create_attrs(self, color = 0, blink = False, bold = False):
    attrs = curses.color_pair(color)

    if blink is True:
      attrs |= curses.A_BLINK

    if bold is True:
      attrs |= curses.A_BOLD

    return attrs

def render_loop(logger, screen, event_quit, delay = 0.1):
  import fcntl
  import os
  import sys

  #from ..streams import fd_blocking
  #fd_blocking(sys.stdout.fileno(), block = True)

  def loop(stdscr):
    # Setup colors
    curses.use_default_colors()

    for i in range(0, curses.COLORS):
      curses.init_pair(i, i, -1);

    screen.attach_handle(stdscr)

    for page in itervalues(screen.pages):
      for widget in page:
        widget.attach_handle(curses.newwin(widget.height, widget.width, widget.top, widget.left))

    while not event_quit.is_set():
      screen.update()
      screen.commit()
      #time.sleep(delay)

    screen.erase()
    screen.commit()

  curses.wrapper(loop)

def event_loop(logger, screen, event_quit):
  import sys
  from curtsies import Input

  with Input(keynames='curtsies') as input_generator:
    for e in Input():
      logger.debug('event_loop: event=%s', repr(e))

      screen.on_event(e)

      if event_quit.is_set():
        logger.debug('event_loop: quit')
        break
