#!/usr/bin/env python
"""
Example of a prompt with autocompletion, where pressing the Enter key accepts
the completion.
"""
from __future__ import unicode_literals

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.filters import HasCompletions
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys


animal_completer = WordCompleter([
    'alligator', 'ant', 'ape', 'bat', 'bear', 'beaver', 'bee', 'bison',
    'butterfly', 'cat', 'chicken', 'crocodile', 'dinosaur', 'dog', 'dolphine',
    'dove', 'duck', 'eagle', 'elephant', 'fish', 'goat', 'gorilla', 'kangoroo',
    'leopard', 'lion', 'mouse', 'rabbit', 'rat', 'snake', 'spider', 'turkey',
    'turtle',
], ignore_case=True)


def main():
    key_bindings_manager = KeyBindingManager.for_prompt()

    @key_bindings_manager.registry.add_binding(Keys.ControlJ, filter=HasCompletions())
    def _(event):
        event.current_buffer.complete_state = None

    text = prompt('Give some animals: ',
                  completer=animal_completer,
                  key_bindings_registry=key_bindings_manager.registry)

    print('You said: %s' % text)


if __name__ == '__main__':
    main()
