import re
from copy import deepcopy

from lxml import html
from lxml.etree import ParserError, XMLSyntaxError, Comment
from lxml.html import builder
from .Importer.QtCore import *

from .SettingsConvenience import settings_get_bool

class ThemeEngine(object):
    """Parse HTML to strip or alter colours or other appearance details.

    Strips out white and black colours to let these be handled natively. Allows
    customisation of font size. Can rewrite timestamps to local time. Also
    provides some parsing helpers such as pulling out timestamps and plain text
    for logging."""
    def __init__(self, parent=None):
        self.parent = parent
        if parent:
            self.set_font()

    def set_font(self):
        settings = QSettings()
        self.font = settings.value("config/font", None)
        self.local_time = settings_get_bool("config/local_time", settings=settings)

    def timestamp_to_local(self, timestamp):
        # this is a messy method for converting a datetime object in UTC
        # (provided by the server) to a local timezone string. python
        # timezone handling is hopeless, so use Qt. note that this returns a
        # QDateTime, since it's only ever used with toString
        ts = list(timestamp.timetuple()[:6]) + [0,Qt.UTC]
        dt = QDateTime(*ts)
        return dt.toLocalTime()

    def theme(self, text, notime=False, forcetime=False):
        # correct unclosed p tags, which tend to get closed by the parser in
        # interesting places. rendering isn't quite the same, but using <p />
        # or <p></p> does other weird things to the layout (<em> goes on a new
        # line and the space above the welcome message is MASSIVE)
        text = text.replace("<p>", "<br>")
        try:
            parse = html.fragment_fromstring(text, create_parent="span")
        except (ParserError, XMLSyntaxError) as err:
            if isinstance(err, XMLSyntaxError):
                debug.debug("XML Syntax error: " + str(err) + " in: " + text)
            if (self.parent is not None) & (not notime):
                return None, "", ""
            else:
                return ""

        if self.parent:
            if self.font is not None:
                parse.attrib["style"] = 'font-size:{}pt; font-family:"{}";'.format(self.font.pointSize(), self.font.family())
                for i in parse.xpath("descendant-or-self::font"):
                    i.tag = "span"
                    i.attrib["style"] = ""
                    if "size" in i.attrib:
                        delta = int(i.attrib["size"])
                        if delta > 0:
                            delta *= 2
                        i.attrib["style"] += "font-size:" + str(self.font.pointSize() + delta) + "pt;"
                        del i.attrib["size"]
                    if "color" in i.attrib:
                        if i.attrib["color"] != "black":
                            i.attrib["style"] += "color:" + i.attrib["color"] + ";"
                        del i.attrib["color"]

        for i in parse.xpath("descendant-or-self::font[@color = 'black']"):
            i.set("color", "")
        for i in parse.xpath("descendant-or-self::body[@bgcolor = 'white']"):
            i.set("bgcolor", "")
        for i in parse.xpath("descendant-or-self::body[@text = 'black']"):
            i.set("bgcolor", "")

        last_time = ""
        for i in parse.iter(tag=Comment):
            last_time = i

        if (self.parent is not None) & (not notime):
            if self.font is None:
                tss = parse.xpath("font[@size='-4']")
            else:
                # if we're rewriting the font sizes we uses spans and styles
                # rather than font tags
                tss = parse.xpath("span[contains(@style, 'font-size:{}pt;')]".format(self.font.pointSize() - 4))
            if self.local_time:
                # convert timestamps
                for i in tss:
                    if not i.text:
                        continue
                    ts = self.timestamp_to_local(self.parent.parse_time(last_time))
                    if re.match(r"\(\d{2}\:\d{2}\:\d{2}\)$", i.text):
                        # short timestamp
                        i.text = ts.toString("(hh:mm:ss)")
                    elif re.match(r"\(\d{1,2}\/\d{1,2}\/\d{4}\, \d{2}\:\d{2}\:\d{2}\)$", i.text):
                        # long timestamp
                        i.text = "(" + ts.toString(Qt.SystemLocaleShortDate) + ")"

            if (last_time is not None) and forcetime and not tss:
                # append a timestamp
                ts = self.parent.parse_time(last_time)
                if ts:
                    if self.local_time:
                        timetext = self.timestamp_to_local(ts).toString(" (hh:mm:ss)")
                    else:
                        timetext = ts.strftime(" (%H:%M:%S)")
                    if self.font is None:
                        tag = builder.FONT(timetext, size="-4", color="#707070")
                    else:
                        tag = builder.SPAN(timetext, style="font-size: {}pt; color: #707070;".format(self.font.pointSize() - 4))
                    parse.insert(-1, tag)

            res = deepcopy(parse)
            # remove timestamps before plaintexting
            for i in tss:
                # bit of a hack - shrunken people speak in font size -4, but because of the way
                # it's arranged it has no text attribute, whereas timestamps do.
                if i.text:
                    i.drop_tree()
            return res, html.tostring(parse, method="text", encoding="unicode"), last_time
        return html.tostring(parse, encoding="unicode")

theme = ThemeEngine()
