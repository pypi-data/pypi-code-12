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
import textwrap
import sys

from .. import command
from .. import defaultconfig


class HelpCommand(command.Command):
    def get_name(self):
        return 'help'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='show help messages about rules & setting detail. etc.',
            description=(
                'show help messages about rules & setting detail. etc.\n\n'
                'include following topic:\n'
                '  rules    - lolinote ruleset.\n'
                '  config   - how to configure lolikit.\n'
                '  selector - how to use lolikit selector.\n'
                ))

        parser.add_argument(
            'topic', nargs='?', choices=['rules', 'config', 'selector'],
            help='select a topic')

        self.parser = parser

    def run(self, args):
        if len(sys.argv) == 2:
            self.parser.print_help()
            sys.exit(1)
        elif args.topic == 'rules':
            self.show_rules()
        elif args.topic == 'config':
            self.show_config()
        elif args.topic == 'selector':
            self.show_selector()

    # def show(self, message):
    #     show_text = textwrap.dedent(message)
    #     print(show_text)

    def show_rules(self):
        message = textwrap.dedent("""\
            # Loli's Rules #

            1. One note. One file. Every notes are INDEPENDENTLY.
            2. Note files are MARKDOWN format.
            3. Note's filename equiv to "title + .md".
            4. All notes in a multi-level directory tree.
            5. Note's order is the filename string order.
            6. Root folder should have a directory which be named as ".loli".
            7. Note content must encoding as "utf8".

            Check https://bitbucket.org/civalin/lolinote for more detail.""")
        print(message)

    def show_config(self):
        message = textwrap.dedent("""\
            # Lolikit Configuration #



            ## Basic ##

            Lolikit have 3 level settings files.

            - default - in lolikit source code "defaultconfig.py" file.
            - user    - in "~/.lolikitrc".
            - project - in "project/.loli/lolikitrc"

            The default setting will be overwrited by user's setting, and
            user's setting will be overwrited by project's setting.



            -----------------------------------------------------------------



            ## Configuration Format ##

            The lolikitrc files is a kind of "ini" format. It look like...

                [selector]
                reverse = on             # on, off: boolean value
                editor  = vim

                [project]
                ignore_patterns = .swp$  # This is a multi-line format
                                  ~$     # use this format to set multi-values
                [fix]
                newline_mode = posix



            -----------------------------------------------------------------



            ## Variables ##



            ### [user] section ###

            Variables in `user` section can only meaningful within the
            "user configure file" & cannot put in to project configure file.



            #### default_project ####

            Set your default project dir. If your are not under
            any loli project and run `loli` command, the program
            will try to using the `default_project` as your default
            project folder.

            You can let it blank to disable this feature. (default)

            example:
                ~/.notes

            (default: "{default[user][default_project]}")


            -----------------------------------------------------------------


            ### [project] section ###

            Variables in `project` section can only meaningful within the
            "project configure file".



            #### ignore_patterns ####

            Determine which path will be ignore by lolikit in current project.
            It is a list of regex patterns and splitted by newline.

            PS: The "^.loli" pattern will be appended automatically and cannot
            be removed.

            (default: {default[project][ignore_patterns]})


            -----------------------------------------------------------------


            ### [selector] section ###

            Control default selector behavior.



            #### editor ####

            Some lolikit command may use a editor. This setting
            define which editor should be used (by default).

            example:
                vim
                gedit "{{path}}"

            (default: "{default[selector][editor]}")



            #### file_browser ####

            Some lolikit command may use a file browser. This setting
            define which file browser should be used (by default).

            example:
                nautilus
                ranger "{{path}}"

            (default: "{default[selector][file_browser]}")



            #### reverse ####

            Some lolikit command will show a list of notes. This setting
            define the list should be reversed or not.

            (default: {default[selector][reverse]})



            #### page_size ####

            Some lolikit command will show a list of notes. This setting
            define how much notes in one page.

            (default: {default[selector][page_size]})



            #### find_format ####

            Define the output format with "find" command.

            (default: "{default[selector][find_format]}")



            #### list_format ####

            Define the output format with "list" command.

            (default: "{default[selector][list_format]}")


            -----------------------------------------------------------------

            > Special hint:
            >
            > You can use following variables in *_format:
            >
            >   - {{title}}
            >   - {{filename}}
            >   - {{parent_dirname}}
            >   - {{absolute_path}}
            >   - {{root_relative_path}}
            >   - {{root_relative_dirname}}
            >   - {{top_dirname}}
            >   - {{mtime}}
            >   - {{atime}}
            >   - {{prepend_resourced_icon}}
            >   - {{append_resourced_icon}}
            >   - {{category}}

            -----------------------------------------------------------------


            ### [check] section ###



            #### danger_pathname_chars ####

            Define what chars is danger in pathname.

            (default: "{default[check][danger_pathname_chars]}")



            #### danger_pathname_chars_fix_to ####

            Set which char will be used to replace the danger chars when
            fixing.

            (default: "{default[check][danger_pathname_chars_fix_to]}")



            #### newline_mode ####

            Define which newline mode should be used in note files.

            available mode:
                - posix
                - windows
                - mac

            (default: "{default[check][newline_mode]}")


            -----------------------------------------------------------------


            ### [serve] section ###

            Control lolinote server behavior.



            #### port ####

            Which port should be used? The value must a positive integer.

            example:
                8080

            (default: {default[serve][port]})



            #### allow_remote_access ####

            This server can be accessed by remote users?
            For secure reason the default value is "no".

            (default: {default[serve][allow_remote_access]})



            #### debug ####

            Server should expose the error messages to browser?
            For secure reason the default value is "no".

            (default: {default[serve][debug]})



            #### users ####

            A multi-value field. Each line should contain a string look like
            "username:passname". If not set any user & password, server will
            turn off all user checking mechanism.

            (default: {default[serve][users]})



            #### ssl_cert_file ####

            A certification file path. If this value not blank then https
            protocal will be used for the default web browser.

            For test purpose, user can create a self-signed cert file by...

            openssl req -new -x509 -keyout loliserver.pem -out loliserver.pem -days 365 -nodes

            (default: {default[serve][users]})
            """).format(
            default=defaultconfig.DEFAULT_CONFIG)
        print(message)

    def show_selector(self):
        message = textwrap.dedent("""\
            # Selector #

            Some sub-command, like "list", may startup a command-line UI
            which be used to select you note or note-related element.

            We call it "selector".



            ## How It Work? ##

            Basically, input the "leading number" (e.g., 9) of a note you want
            to open, then press enter. Just it!

            If you want to scrolling the page, press "next" or "prev".

            If you want to exit, press "exit" or a simple blank line.



            ## Advanced Usage ##

            You can press a "number" + "special character" + "arguments" to
            trigger more functions. For example...

              - `3`: open a note with default editor.
              - `3@gvim`: open a note with gvim.
              - `3/`: open directory of this note with default file browser.
              - `3/ranger`: open directory of this note with ranger.
              - `3.`: open attachment selector for this note.



            > User can pass "?" or "help" in selector to check more detail.

            """).format(
            default=defaultconfig.DEFAULT_CONFIG, current=self.config)
        print(message)
