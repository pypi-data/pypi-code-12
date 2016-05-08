#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import print_function, unicode_literals
# import prompt_toolkit
# from prompt_toolkit import prompt
# from prompt_toolkit.contrib.completers import WordCompleter
# from prompt_toolkit.history import InMemoryHistory
# from prompt_toolkit.interface import AbortAction
# from prompt_toolkit import auto_suggest
# from ec3.boto_cache import BotoCache

# def main_shell(conf):
#     print('conf: ', conf)
#     boto_cache = BotoCache.get_or_create()
#     all_keys = set()
#     all_pairs = set()
#     for tag in boto_cache.iter_tags():
#         all_keys.add(tag.key)
#         all_pairs.add('%s=%s' % (tag.key, tag.value))

#     words = ['fish', 'cat', 'gorilla', 'ssh']
#     words = list(set(words) | all_keys | all_pairs)
#     completer = WordCompleter(words, ignore_case=True)
#     history = InMemoryHistory()
#     text = prompt('yes? ', completer=completer,
#         # history = history,
#         # auto_suggest=auto_suggest.AutoSuggestFromHistory(),
#         display_completions_in_columns=True,
#         # enable_history_search=True
#     )
#     print('yeah : "%s"' % text)
