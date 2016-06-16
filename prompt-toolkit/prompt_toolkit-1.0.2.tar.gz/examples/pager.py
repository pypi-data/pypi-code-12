#!/usr/bin/env python
"""
"""
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, TokenListControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.processors import HighlightSearchProcessor
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.layout.toolbars import SearchToolbar
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.styles import PygmentsStyle

from pygments.token import Token

def get_statusbar_tokens(cli):
    b = cli.buffers[DEFAULT_BUFFER]
    return [
        (Token.Status, '%s' % (b.document.cursor_position_row + 1)),
    ]


layout = HSplit([
    Window(content=TokenListControl(get_statusbar_tokens, align_right=True,
                                    default_char=Char(token=Token.Status)),
           height=D.exact(1)),

    # The main content.
    Window(
        content=BufferControl(buffer_name=DEFAULT_BUFFER,
                              input_processors=[HighlightSearchProcessor(preview_search=True)]),
#        always_hide_cursor=True
        ),

    SearchToolbar(),
])

# Key bindings.
manager = KeyBindingManager(enable_search=True, enable_extra_page_navigation=True)

@manager.registry.add_binding('q')
def _(event):
    " Quit. "
    event.cli.set_return_value(None)

text = open('./pager.py', 'rb').read().decode('utf-8')

style = PygmentsStyle.from_defaults({
    Token.Status: 'bg:#444444 #ffffff',
})

# create application.
application = Application(
    layout=layout,
    buffer=Buffer(initial_document=Document(text=text, cursor_position=0), read_only=True),
    key_bindings_registry=manager.registry,

    # Let's add mouse support!
    mouse_support=True,
    style=style,

    # Using an alternate screen buffer means as much as: "run full screen".
    # It switches the terminal to an alternate screen.
    use_alternate_screen=True)


def run():
    eventloop = create_eventloop()

    try:
        cli = CommandLineInterface(application=application, eventloop=eventloop)
        cli.run(reset_current_buffer=False)

    finally:
        eventloop.close()

if __name__ == '__main__':
    run()
