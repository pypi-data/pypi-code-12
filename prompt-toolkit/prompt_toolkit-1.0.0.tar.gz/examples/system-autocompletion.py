#!/usr/bin/env python
"""
Example of autocompletion using filenames.
"""
from __future__ import unicode_literals

from prompt_toolkit.contrib.completers.system import SystemCompleter
from prompt_toolkit import prompt


def main():
    text = prompt('Shell: ', completer=SystemCompleter())
    print('You said: %s' % text)


if __name__ == '__main__':
    main()
