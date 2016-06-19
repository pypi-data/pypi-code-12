import re
from html.entities import name2codepoint
from html.parser import HTMLParser


class HTMLTools:
    @staticmethod
    def html_to_text(html):
        """
        Cleans html tags
        """
        parser = _HTMLToText()
        parser.feed(html)
        parser.close()
        return parser.get_text()

    @staticmethod
    def text_to_html(text):
        def f(mo):
            t = mo.group()
            if len(t) == 1:
                return {'&': '&amp;', "'": '&#39;', '"': '&quot;', '<': '&lt;', '>': '&gt;'}.get(t)
            return '<a href="%s">%s</a>' % (t, t)

        return re.sub(r'https?://[^] ()"\';]+|[&\'"<>]', f, text)


class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(chr(n))

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))
