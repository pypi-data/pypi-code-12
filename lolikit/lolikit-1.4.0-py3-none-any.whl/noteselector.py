#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2016 CIVA LIN (林雪凡)
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

import datetime as DT
import subprocess
import re
import sys

import termcolor as TC

from . import itemselector as IS
from . import utils


class NoteInfo():
    """A note info warper"""
    def __init__(self, path, rootdir, ignore_patterns):
        self.path = path
        self.rootdir = rootdir
        self.ignore_patterns = ignore_patterns

    @property
    def title(self):
        return self.path.stem

    @property
    def filename(self):
        return self.path.name

    @property
    def parent_dirname(self):
        return self.path.parent.name

    @property
    def grandparent_dirname(self):
        return self.path.parent.parent.name

    @property
    def absolute_path(self):
        return str(self.path.resolve())

    @property
    def absolute_parent_dirpath(self):
        return str(self.path.parent.resolve())

    @property
    def root_relative_path(self):
        return str(self.path.relative_to(self.rootdir))

    @property
    def root_relative_dirname(self):
        return str(self.path.relative_to(self.rootdir).parent)

    @property
    def top_dirname(self):
        return self.path.relative_to(self.rootdir).parts[0]

    @property
    def mtime(self):
        return DT.datetime.fromtimestamp(self.path.stat().st_mtime)

    @property
    def atime(self):
        return DT.datetime.fromtimestamp(self.path.stat().st_atime)

    @property
    def prepend_resourced_icon(self):
        icon = '+ ' if utils.is_rmd(
            self.path, self.rootdir, self.ignore_patterns) else '  '
        if sys.platform.startswith('win'):
            return icon
        else:
            return TC.colored(icon, 'green', attrs=['bold'])

    @property
    def append_resourced_icon(self):
        icon = ' +' if utils.is_rmd(
            self.path, self.rootdir, self.ignore_patterns) else '  '
        if sys.platform.startswith('win'):
            return icon
        else:
            return TC.colored(icon, 'green', attrs=['bold'])

    @property
    def category(self):
        if utils.is_rmd(self.path, self.rootdir, self.ignore_patterns):
            return self.grandparent_dirname
        else:
            return self.parent_dirname

    def get_properties(self):
        return {
            'title': self.title,
            'filename': self.filename,
            'parent_dirname': self.parent_dirname,
            'absolute_path': self.absolute_path,
            'root_relative_path': self.root_relative_path,
            'root_relative_dirname': self.root_relative_dirname,
            'top_dirname': self.top_dirname,
            'mtime': self.mtime,
            'atime': self.atime,
            'prepend_resourced_icon': self.prepend_resourced_icon,
            'append_resourced_icon': self.append_resourced_icon,
            'category': self.category,
            }


def note_item_factory(path, rootdir, text_format,
                      default_editor, default_file_browser, config):
    ignore_patterns = config['project']['ignore_patterns']

    def text_func(data):
        return text_format.format(**data.get_properties())

    def task(data, line):
        def line_decode(line):
            kwargs = {}
            match = re.search(r'^([@/.])(.*)', line.strip())
            if match is None:
                kwargs['task_mode'] = 'open'
                kwargs['opener'] = None
            else:
                kwargs['opener'] = match.group(2)
                if match.group(1) == '@':
                    kwargs['task_mode'] = 'open'
                elif match.group(1) == '/':
                    kwargs['task_mode'] = 'file_browsing'
                elif match.group(1) == '.':
                    kwargs['task_mode'] = 'attachment_browsing'
            return kwargs['task_mode'], kwargs['opener']

        def call_opener(task_mode, opener):
            if task_mode == 'open':
                opener = opener if opener else default_editor
                path = data.absolute_path
                e_msg = '[cancel]: editor "{}" not found.'
            elif task_mode == 'file_browsing':
                opener = opener if opener else default_file_browser
                path = data.absolute_parent_dirpath
                e_msg = '[cancel] file_browser "{}" not found.'

            command = utils.get_opener_command(opener, path)
            e_msg = e_msg.format(command[0])

            try:
                subprocess.call(command)
                return True
            except FileNotFoundError:
                print(e_msg)
                return False

        task_mode, opener = line_decode(line)

        if task_mode in ('open', 'file_browsing'):
            return call_opener(task_mode, opener)
        elif task_mode == 'attachment_browsing':
            if utils.is_rmd(data.path, rootdir, ignore_patterns):
                start_attachment_selector(data, config)
            else:
                print('[cancel]: "{}" not a resourced note.'.format(
                    data.title))
            return False

    noteinfo = NoteInfo(path, rootdir, ignore_patterns)
    return IS.Item(text=text_func, task=task, data=noteinfo)


def start_note_selector(note_items, config):
    usage = (
        '\n'
        'How to use\n'
        '==================================================\n'
        '## Open a note ##\n'
        '    <number>               => e.g., 9\n'
        '    <number> @             => e.g., 9@\n'
        '        - open file with default editor\n'
        '    <number> @ <editor>    => e.g., 9@gedit\n'
        '        - open file with special editor\n'
        '\n'
        '## Open a note directory ##\n'
        '    <number> /             => e.g., 9/\n'
        '        - open folder with default filebrowser\n'
        '    <number> / <file_browser>    => e.g., 9/ranger\n'
        '        - open folder with special filebrowser\n'
        '\n'
        '## Open attachment selector ##\n'
        '    <number> .             => e.g., 9.\n'
        '        - view attachments of one of note\n\n')
    prompt = 'note> '
    intro = ('Select a Note (press "help" for usage)\n'
             '=============================================\n')

    return IS.start_selector(
        note_items,
        usage=usage,
        prompt=prompt,
        intro=intro,
        page_size=int(config['selector'].get('page_size')),
        reverse=config['selector'].getboolean('reverse'))


def start_attachment_selector(noteinfo, config):
    usage = (
        '\n'
        'How to use\n'
        '==================================================\n'
        '## Open a attach ##\n'
        '    <number>               => e.g., 9\n'
        '    <number> @             => e.g., 9@\n'
        '        - open file with default program\n'
        '    <number> @ <opener>    => e.g., 9@firefox\n'
        '        - open file with special program\n\n')
    prompt = 'attachment> '
    intro = ('Select a Attachment (press "help" for usage)\n'
             '=============================================\n')

    def attachment_item_factory(res_path):
        def task(data, line):
            def decode_line(line):
                match = re.search(r'^([@])(.*)', line.strip())
                if match is None:
                    opener = utils.get_default_opener()
                elif match.group(2):
                    opener = match.group(2)
                return utils.get_opener_command(opener, res_path)

            command = decode_line(line)
            try:
                subprocess.call(command)
            except FileNotFoundError:
                print('opener: "{}" not found. cancel.'.format(command[0]))

        return IS.Item(text=res_path.name,
                       task=task)

    items = [attachment_item_factory(res_path) for res_path
             in sorted(utils.get_resource_paths(noteinfo.path))]

    return IS.start_selector(
        items,
        usage=usage,
        prompt=prompt,
        intro=intro,
        page_size=int(config['selector'].get('page_size')),
        reverse=config['selector'].getboolean('reverse'))
