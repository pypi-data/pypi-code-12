#!/usr/bin/env python3
"""
           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                   Version 2, December 2004

Copyright (C) 2015 Vincent Maillol <vincent.maillol@gmail.com>

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHAT THE FUCK YOU WANT TO.
"""

__version__ = "0.0.3"

import ast
import re
import sys



HEADER_TEMPLATE = """
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR {args.copyright_holder}
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: {args.package}\\n"
"Report-Msgid-Bugs-To: {args.bugs_address}\\n"
"POT-Creation-Date: {time}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset={args.charset}\\n"
"Content-Transfer-Encoding: 8bit\\n"

""".lstrip()


class Message:
    """
    One PO file entry has the following schematic structure:

        white-space
        #  translator-comments
        #. extracted-comments
        #: reference…
        #, flag…
        #| msgid previous-untranslated-string
        msgid untranslated-string
        msgstr translated-string
    """

    def __init__(self, msgid, msgid_plural=None):
        """
        msgid: the original untranslated  string singular
        msgid_plural: untranslated string plural
        """
        self.msgid = msgid
        self.msgid_plural = msgid_plural
        self.msgstr = ""
        self.references = []
        self.translator_comments = []
        self.extracted_comments = []
        self.flags = []

    def format_msgid(self, prefix):
        """
        prefix - must be msgid or msgid_plural.
        """
        if prefix == 'msgid':
            texts = self.msgid.split('\n')
        else:
            texts = self.msgid_plural.split('\n')

        if len(texts) > 1:
            out = prefix + ' ""\n'
            for text in texts[:-1]:
                out += '"{}\\n"\n'.format(text.replace('\\', '\\\\').replace('"', '\\"'))
            out += '"{}"'.format(texts[-1].replace('\\', '\\\\').replace('"', '\\"'))
        else:
            out = prefix + ' "{}"'.format(texts[0].replace('\\', '\\\\').replace('"', '\\"'))
        return out

    def format_references(self):
        """
        return references PO file formated.
        """
        prefix = '#: '
        line = prefix + self.references[0]
        lines = []
        for reference in self.references[1:]:
            if len(line) + len(reference) < 79:
                line += ' ' + reference
            else:
                lines.append(line)
                line = prefix + reference
        lines.append(line)
        return '\n'.join(lines)

    def __str__(self):
        if self.msgid_plural is None:
            return '\n'.join((
                self.format_references(),
                self.format_msgid('msgid'),
                'msgstr ""\n'))
        else:
            return '\n'.join((
                self.format_references(),
                self.format_msgid('msgid'),
                self.format_msgid('msgid_plural'),
                'msgstr[0] ""',
                'msgstr[1] ""\n'))

class MetaExtractor(type):
    
    extractors = {}

    def __init__(cls, name, parent, kwargs):
        if parent:
            type(cls).extractors[cls.extension] = cls
                

class Extractor(metaclass=MetaExtractor):
    """
    Abstract class to extract gettext strings from file.
    """
    extension = NotImplemented

    def is_parsable(self, file_name):
        """
        Return true if Extractor can extract gettext string
        from file_name
        """
        return file_name.rsplit('.', 1)[-1].lower() == self.extension

    def extract(self, messages_by_msgid, file_name):
        """
        Extract gettext string and store it in messages_by_msgid.
        """
        if self.is_parsable(file_name):
            with open(file_name) as input_file:
                self._extract(messages_by_msgid, input_file)
            return True
        return False

    def _extract(self, messages_by_msgid, input_file):
        """
        You must redefine this method
        messages_by_msgid - dict of Message object
        input_file - file object
        """
        raise NotImplementedError()


class PyExtractor(Extractor):
    """
    Class to extract gettext strings from python file.
    """

    extension = 'py'

    def _extract(self, messages_by_msgid, input_file):
        class MyVisitor(ast.NodeVisitor):
            """
            Visit python file and fill messages_by_msgid.
            """

            def visit_Call(self, node):
                """
                Called when visitor meet a method call.
                if method is gettext method, arguments are stored in
                messages_by_msgid
                """
                func = node.func
                gettext_name = ('_', 'gettext', 'ugettext', 'ugettext_lazy')
                if ((hasattr(func, 'id') and func.id in gettext_name)
                        or (hasattr(func, 'attr') and func.attr == 'translate')):
                    reference = "{}:{}".format(input_file.name, node.args[0].lineno)
                    try:
                        msgid = node.args[0].s
                    except AttributeError:
                        warning_msg = 'Warning: File "{}", line {}'.format(
                            input_file.name, node.args[0].lineno)
                        print(warning_msg, file=sys.stderr)
                        self.generic_visit(node)
                        return

                    message = messages_by_msgid.setdefault(msgid, Message(msgid))
                    message.references.append(reference)
                    if len(node.args) > 1:
                        message.msgid_plural = node.args[1].s

                self.generic_visit(node)

        node = ast.parse(input_file.read())
        MyVisitor().visit(node)


class TemplateExtractor(Extractor):
    """
    Class to extract gettext strings from
    tornado/Djanog template file.
    """

    extension = 'html'

    string = r'''("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')'''
    regex = re.compile(
        r'''{{\s*_\(\s*{0}(?:\s*,\s*{0}\s*,.*)?\s*\)\s*}}'''
        .format(string)
    )

    def _extract(self, messages_by_msgid, input_file):
        for line_number, line in enumerate(input_file, 1):
            match = self.regex.search(line)
            while match is not None:
                msgid = match.group(1)[1:-1]
                reference = "{}:{}".format(input_file.name, line_number)
                message = messages_by_msgid.setdefault(msgid, Message(msgid))
                message.references.append(reference)
                if match.group(2) is not None:
                    message.msgid_plural = match.group(2)[1:-1]
                match = self.regex.search(line, match.end())


