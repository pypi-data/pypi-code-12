# -*- coding: utf-8 -*-
"""
Den-Den Extension for Python-Markdown
=======================================

Adds Den-Den Markdown handling to Python-Markdown.

See <https://github.com/muranamihdk/denden_extension>
for documentation.

Copyright (c) 2015 MURANAMI Hideaki

License: [MIT](http://opensource.org/licenses/MIT)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import Pattern
from markdown.inlinepatterns import SimpleTagPattern
from markdown.inlinepatterns import EscapePattern
from markdown.postprocessors import Postprocessor
from markdown import util
import re



"""
The actual regular expressions for patterns
---------------------------------------------------------------"""

# 改ページ（ファイル分割）：===
DOC_BREAK_RE = r'^[ ]{0,3}(=+[ ]{0,2}){3,}[ ]*'

# \<
ESCAPE_RE = r'\\(.)'

# ページ番号：[%5] or [%%5]
PAGE_NUM_RE = r'^\s*?\[(%%?)(\d+?)\]\s*$'
PAGE_NUM_INLINE_RE = r'\[(%%?)(\d+?)\]'

# ルビ：{電子書籍|でん|し|しょ|せき}
RUBY_RE = r'{([^\|]+?)((?:\|.+?)+?)}'

# ルビ文字：|でん|し|しょ|せき
RUBY_RTS_RE = r'\|([^\|]+)'

# 横中縦：^21^世紀
TATE_CHU_YOKO_RE = r'(\^)(.+?)\^'



"""
The DenDen Markdown Extension Class
---------------------------------------------------------------"""

class DenDenExtension(Extension):
    """ DenDen Extension for Python-Markdown. """

    def __init__(self, **kwargs):
        self.config = {
            'docbreak' : [True, 'Insert Documentation Breaks.'],
            'pagenum' : [True, 'Insert Page Numbers.'],
            'footnote' : [True, 'Substitute Footnotes for XHTML and Epub Format.']}
        super(DenDenExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):

        # Add preprocessors.
        md.preprocessors.add('two_bytes_space', TwoBytesSpacePreprocessor(), '_begin')

        # Add blockprocessors.
        if self.getConfig('docbreak'):
            md.parser.blockprocessors.add('doc_break', DocBreakProcessor(md.parser), '>hr')
        if self.getConfig('pagenum'):
            md.parser.blockprocessors.add('page_num', PageNumProcessor(md.parser), '<paragraph')

        # Add inline patterns.
        md.inlinePatterns['escape'] = DenDenEscapePattern(ESCAPE_RE, md)
        if self.getConfig('pagenum'):
            try:
                md.inlinePatterns.add('page_num', PageNumTagPattern(PAGE_NUM_INLINE_RE), '>strong2')
            except ValueError:
                md.inlinePatterns.add('page_num', PageNumTagPattern(PAGE_NUM_INLINE_RE), '>emphasis2')
        try:
            md.inlinePatterns.add('denden_ruby', RubyTagPattern(RUBY_RE, 'ruby,rt'), '>page_num')
        except ValueError:
            md.inlinePatterns.add('denden_ruby', RubyTagPattern(RUBY_RE, 'ruby,rt'), '_end')
        md.inlinePatterns.add('denden_tate_chu_yoko', TateChuYokoTagPattern(TATE_CHU_YOKO_RE, 'span'), '>denden_ruby')

        # Add postprocessors.
        if self.getConfig('pagenum'):
            md.postprocessors.add('page_num', PageNumPostprocessor(), '_end')
        if self.getConfig('footnote'):
            try:
                md.postprocessors.add('footnote_sub', FootnoteSubPostprocessor(), '>footnote')
            except ValueError:
                md.postprocessors.add('footnote_sub', FootnoteSubPostprocessor(), '_end')
        md.postprocessors.add('two_bytes_space', TwoBytesSpacePostprocessor(), '_end')



"""
The classes for DenDen Markdown syntax
---------------------------------------------------------------"""

class TwoBytesSpacePreprocessor(Preprocessor):
    """ Replace two bytes spaces with a placeholder. """

    def run(self, lines):
        new_lines = []
        for line in lines:
            new_lines.append(re.sub(r'　', 'klzzwxh:12288', line))
        return new_lines


class DocBreakProcessor(BlockProcessor):
    """ Process Doc Breaks. """

    SEARCH_RE = re.compile(DOC_BREAK_RE, re.MULTILINE)

    def test(self, parent, block):
        m = self.SEARCH_RE.search(block)
        if m and (m.end() == len(block) or block[m.end()] == '\n'):
            self.match = m
            return True
        return False

    def run(self, parent, blocks):
        block = blocks.pop(0)
        prelines = block[:self.match.start()].rstrip('\n')
        if prelines:
            self.parser.parseBlocks(parent, [prelines])
        el = util.etree.SubElement(parent, 'hr')
        el.set('class', 'docbreak')
        postlines = block[self.match.end():].lstrip('\n')
        if postlines:
            blocks.insert(0, postlines)


class PageNumProcessor(BlockProcessor):
    """ Process Page Numbers. """
    RE = re.compile(PAGE_NUM_RE)

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        el = util.etree.SubElement(parent, 'div')
        el.attrib = {
            'id': 'pagenum_{}'.format(m.group(2)),
            'class': 'pagenum',
            'title': m.group(2),
            'epub:type': 'pagebreak'}
        if m.group(1) == '%%':
            el.text = m.group(2).strip()


class DenDenEscapePattern(EscapePattern):
    """ Return an escaped character. """

    def handleMatch(self, m):
        char = m.group(2)
        ESCAPED_CHARS = self.markdown.ESCAPED_CHARS
        ESCAPED_CHARS.append('|')
        if char in ESCAPED_CHARS:
            return '%s%s%s' % (util.STX, ord(char), util.ETX)
        else:
            return None


class PageNumTagPattern(Pattern):
    """
    Return a 'pagenum' class element containing the matching text.
    """
    def handleMatch(self, m):
        if not m.group(1).strip() or m.group(1).endswith('\n'):  # There is no string before the matched part
            el = util.etree.Element('div')
        else:  # There is a string before the matched part
            el = util.etree.Element('span')
        el.attrib = {
            'id': 'pagenum_{}'.format(m.group(3)),
            'class': 'pagenum',
            'title': m.group(3),
            'epub:type': 'pagebreak'}
        if m.group(2) == '%%':
            el.text = m.group(3)
        return el


class RubyTagPattern(SimpleTagPattern):
    """Return a ruby element."""

    def handleMatch(self, m):
        tag1, tag2 = self.tag.split(",")
        ruby_texts = re.findall(RUBY_RTS_RE, m.group(3))
        if len(m.group(2)) == len(ruby_texts):
            el1 = util.etree.Element(tag1)
            el1.text = m.group(2)[0]
            for idx, ruby_text in enumerate(ruby_texts):
                el2 = util.etree.SubElement(el1, tag2)
                el2.text = ruby_text
                if idx < len(m.group(2)) - 1:
                    el2.tail = m.group(2)[idx+1]
        else:
            el1 = util.etree.Element(tag1)
            el1.text = m.group(2)
            el2 = util.etree.SubElement(el1, tag2)
            el2.text = re.sub(r'\|', '', m.group(3))
        return el1


class TateChuYokoTagPattern(SimpleTagPattern):
    """
    Return a 'tcy' class element containing the matching text.
    """
    def handleMatch(self, m):
        el = util.etree.Element(self.tag)
        el.text = m.group(3)
        el.set('class', 'tcy')
        return el


class PageNumPostprocessor(Postprocessor):
    """ Reorder attributes of page number elements. """

    DIV_RE = re.compile(r'<div class="pagenum" epub:type="pagebreak" id="pagenum_(\d+)" title="\d+">')
    SPAN_RE = re.compile(r'<span class="pagenum" epub:type="pagebreak" id="pagenum_(\d+)" title="\d+">')

    def sub_div(self, m):
        text = '<div id="pagenum_{}" class="pagenum" title="{}" epub:type="pagebreak">'.format(m.group(1), m.group(1))
        return text

    def sub_span(self, m):
        text = '<span id="pagenum_{}" class="pagenum" title="{}" epub:type="pagebreak">'.format(m.group(1), m.group(1))
        return text

    def run(self, text):
        text = self.DIV_RE.sub(self.sub_div, text)
        text = self.SPAN_RE.sub(self.sub_span, text)
        return text


class FootnoteSubPostprocessor(Postprocessor):
    """ Substitute Footnotes for XHTML and Epub Format. """

    FOOT_NOTE_ANCHOR_RE = re.compile(r'<sup id="fnref:(\d+)"><a class="footnote-ref" href="#fn:\d+" rel="footnote">(.*?)</a></sup>')
    FOOT_NOTE_TARGET_RE = re.compile(r'<li id="fn:(\d+)">\n(.*?)<a class="footnote-backref" href="#fnref:\d+" rev="footnote" title="Jump back to footnote \d+ in the text">&#8617;</a></p>\n</li>', re.DOTALL)

    def sub_anc(self, m):
        text = '<a id="fnref_{}" href="#fn_{}" rel="footnote" class="noteref" epub:type="noteref">{}</a>'.format(m.group(1), m.group(1), m.group(2))
        #text = '<a class="noteref" epub:type="noteref" href="#fn_{}" id="fnref_{}" rel="footnote" >{}</a>'.format(m.group(1), m.group(1), m.group(2))
        return text

    def sub_tgt(self, m):
        text = '<li>\n<div id="fn_{}" class="footnote" epub:type="footnote">\n{}<a href="#fnref_{}">&#9166;</a></p>\n</div>\n</li>'.format(m.group(1), m.group(2), m.group(1))
        #text = '<li>\n<div class="footnote" epub:type="footnote" id="fn_{}">\n{}<a href="#fnref_{}">&#9166;</a></p>\n</div>\n</li>'.format(m.group(1), m.group(2), m.group(1))
        return text

    def run(self, text):
        text = text.replace('<div class="footnote">', '<div class="footnotes" epub:type="footnotes">')
        text = self.FOOT_NOTE_ANCHOR_RE.sub(self.sub_anc, text)
        text = self.FOOT_NOTE_TARGET_RE.sub(self.sub_tgt, text)
        return text


class TwoBytesSpacePostprocessor(Postprocessor):
    """ Restore two bytes spaces. """

    def run(self, text):
        return text.replace('klzzwxh:12288', '　')



def makeExtension(**kwargs):
    """ Return an instance of the DenDenExtension """
    return DenDenExtension(**kwargs)
