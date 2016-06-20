#!/usr/bin/env python
"""
get_password function that displays asterisks instead of the actual characters.
With the addition of a ControlT shortcut to hide/show the input.
"""
from __future__ import unicode_literals
from prompt_toolkit import prompt
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import Condition
from prompt_toolkit.contrib.completers import WordCompleter

animal_completer = WordCompleter([
    'alligator',
    'ant',
    'ape',
    'bat',
    'bear',
    'beaver',
    'bee',
    'bison',
    'butterfly',
    'cat',
    'chicken',
    'crocodile',
    'dinosaur',
    'dog',
    'dolphine',
    'dove',
    'duck',
    'eagle',
    'elephant',
    'fish',
    'goat',
    'gorilla',
    'kangoroo',
    'leopard',
    'lion',
    'mouse',
    'rabbit',
    'rat',
    'snake',
    'spider',
    'turkey',
    'turtle',
], ignore_case=True)


def main():
    complete_wt = [False]

    def complete_while_typing():
        return complete_wt[0]

    key_bindings_manager = KeyBindingManager()

    @key_bindings_manager.registry.add_binding(Keys.ControlI)
    def _(event):
        complete_wt[0] = True

        b = event.current_buffer

        def second_tab():
            if b.complete_state:
                b.complete_next()
            else:
                event.cli.start_completion(select_first=True)

        # On the second tab-press, or when already navigating through
        # completions.
        if event.is_repeat or b.complete_state:
            second_tab()
        else:
            event.cli.start_completion(insert_common_part=True)

    prompt('Password: ',
           complete_while_typing=Condition(complete_while_typing),
           key_bindings_registry=key_bindings_manager.registry,
           completer=animal_completer)


if __name__ == '__main__':
    main()
