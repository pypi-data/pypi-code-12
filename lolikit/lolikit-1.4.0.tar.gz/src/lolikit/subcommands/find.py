#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import argparse
import re

from .. import command
from .. import noteselector as NS


class FindCommand(command.Command):
    def get_name(self):
        return 'find'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='find some notes which contain some special patterns',
            description='find some notes which contain some special patterns')

        parser.add_argument(
            'patterns', metavar='PATTERN', type=str, nargs='+',
            help='string or regex patterns for finding')

        parser.add_argument(
            '-p', '--path-patterns', dest="path_patterns", metavar='PATTERN',
            type=str, nargs='*',
            help=('filter patterns should match on pathname of notes\n'
                  '(not include parents of project\'s root)'))

    def run(self, args):
        def start_find_selector():
            note_items = [NS.note_item_factory(
                path=data[0],
                rootdir=self.rootdir,
                text_format=self.config['selector']['find_format'],
                default_editor=self.config['selector']['editor'],
                default_file_browser=self.config['selector']['file_browser'],
                config=self.config,
                )
                for data in sorted(
                    self.get_all_matches(args.patterns, args.path_patterns),
                    key=lambda data: self.calculate_score(*data),
                    reverse=True)]
            if len(note_items) > 0:
                NS.start_note_selector(note_items, self.config)

        self.require_rootdir()
        start_find_selector()

    def get_all_matches(self, patterns, path_patterns):
        """
        yield: (path, content, title_matches_list, content_matches_list)
        """
        def get_matches(path, progs):
            title_matches_list = [
                tuple(m for m in prog.finditer(path.stem))
                for prog in progs]
            with open(str(path), encoding='utf8') as f:
                content = f.read()
            content_matches_list = [
                tuple(m for m in prog.finditer(content))
                for prog in progs]
            return content, title_matches_list, content_matches_list

        progs = [re.compile(pattern, re.IGNORECASE)
                 for pattern in patterns]

        if path_patterns:
            path_progs = [re.compile(path_pattern, re.IGNORECASE)
                          for path_pattern in path_patterns]
            all_md_paths = (path for path in self.get_all_md_paths()
                            if any(
                                prog.search(
                                    str(path.relative_to(self.rootdir)))
                                for prog in path_progs
                                ))
        else:
            all_md_paths = self.get_all_md_paths()

        for path in all_md_paths:
            (content,
             title_matches_list,
             content_matches_list) = get_matches(path, progs)

            hit = all([any((title_matches, content_matches))
                      for title_matches, content_matches
                      in zip(title_matches_list, content_matches_list)])
            if hit:
                yield (path, content,
                       title_matches_list, content_matches_list)

    def calculate_score(self, path, content,
                        title_matches_list, content_matches_list):
        def get_title_score(title, title_matches_list):
            # title_matches_len = 0
            # for title_matches in title_matches_list:
            #     title_matches_len += len(
            #         ''.join(m.group(0) for m in title_matches))
            # return title_matches_len / len(title)
            return sum(len(tms) for tms in title_matches_list)

        def get_content_score(content, content_matches_list):
            content_matches_len = 0
            for content_matches in content_matches_list:
                content_matches_len += len(
                    ''.join(m.group(0) for m in content_matches))
            return content_matches_len / len(content)

        def get_repeat_score(content_score, content_matches_list):
            repeat_count = 0
            for content_matches in content_matches_list:
                repeat_count += len(content_matches)
            return repeat_count * content_score

        title_score = get_title_score(path.stem, title_matches_list)
        content_score = get_content_score(content, content_matches_list)
        repeat_score = get_repeat_score(content_score, content_matches_list)
        total_score = title_score + content_score + repeat_score
        return total_score
