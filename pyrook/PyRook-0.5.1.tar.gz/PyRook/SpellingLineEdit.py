import os
import platform
import re
from collections import deque

from .Importer.QtCore import *
from .Importer.QtGui import *
import pkg_resources

from .SettingsConvenience import settings_get_bool
from .Externals import enchant, hunspell
from .Debug import debug


class HunspellDict:
    """Hunspell wrapper mirroring Enchant interface."""
    def __init__(self, *args):
        lang = QLocale().system().name()
        if (platform.system() == "Linux" and
                os.path.exists(os.path.join("/usr/share/hunspell", lang + ".dic"))):
            # system dictionary for our language exists
            self.hun = hunspell.Hunspell("/usr/share/hunspell", lang)
        else:
            # if the system dictionary isn't there or we're not on a Linux
            # system, for the moment just fall back to the US dictionary we
            # ship
            dic, aff = [pkg_resources.resource_filename(__name__, "data/en_US." + i) for i in ("dic", "aff")]
            self.hun = hunspell.Hunspell(os.path.split(dic)[0])

    def check(self, word):
        return self.hun.check(word)

    def suggest(self, word):
        return self.hun.suggest(word)

    def add(self, word):
        # for the moment we don't support a persistent dictionary on hunspell
        return self.add_to_session(word)

    def add_to_session(self, word):
        return self.hun.add(word)


class SpellingLineEdit(QPlainTextEdit):
    """A widget with the behaviour of a QLineEdit, but with the addition of syntax
    highlighted spelling checking.

    Note that this is actually a QPlainTextEdit altered to behave like a LineEdit,
    as the LineEdit does not allow syntax highlighting."""
    returnPressed = Signal()
    def __init__(self, specified_size=None, *args, **kwargs):
        QPlainTextEdit.__init__(self, *args, **kwargs)

        self.history = deque(maxlen=20)
        self.history_index = 0
        self.current_message = ""
        self.textChanged.connect(self.update_msg)

        # mimic LineEdit
        self.v_size_hint = specified_size

        self.setTabChangesFocus(True)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.document().setDocumentMargin(2)
        self.setFixedHeight(self.sizeHint().height())

        QApplication.instance().settings_changed.connect(self.settings_changed)

        self.dict = None
        if enchant:
            try:
                self.dict = enchant.Dict()
            except enchant.errors.DictNotFoundError:
                self.dict = enchant.Dict("en_US")
        elif hunspell:
            try:
                self.dict = HunspellDict()
            except (FileNotFoundError, hunspell.HunspellError):
                debug.debug("could not load hunspell", e)
        if self.dict:
            self.highlighter = SpellingHighlighter(self.dict, self.document())
        self.settings_changed()

    def keyPressEvent(self, event):
        # act like LineEdit when enter is pressed
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.history.append(self.text())
            self.history_index = len(self.history)
            self.returnPressed.emit()
        # scroll through message history
        elif event.key() in (Qt.Key_Up, Qt.Key_Down):
            delta = 1 if event.key() == Qt.Key_Down else -1
            new_index = self.history_index + delta
            if new_index == len(self.history):
                self.history_index = new_index
                self.setText(self.current_message)
            elif 0 <= new_index < len(self.history):
                self.history_index = new_index
                self.setText(self.history[new_index])
        else:
            QPlainTextEdit.keyPressEvent(self, event)

    def update_msg(self):
        if self.history_index == len(self.history):
            self.current_message = self.text()

    def sizeHint(self):
        # attempt to mimic sizeHint of LineEdit
        # (this is unreliable on some styles, notably Win7)
        font_metric = QFontMetrics(self.font())
        if self.v_size_hint is not None:
            # override guess
            h = self.v_size_hint
        else:
            h = max(font_metric.height(), 14) + 10
        w = font_metric.width("x") * 17 + 4
        try:
            opt = QStyleOptionFrameV2()
        except NameError:
            opt = QStyleOptionFrame()
        opt.initFrom(self)
        return self.style().sizeFromContents(QStyle.CT_LineEdit, opt, QSize(w, h).expandedTo(QApplication.globalStrut()), self)

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)
        c = self.textCursor()
        c.movePosition(QTextCursor.End)
        self.setTextCursor(c)

    def insertPlainText(self, text):
        text = text.replace("\n", " ")
        QPlainTextEdit.insertPlainText(self, text)

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())

    def settings_changed(self):
        if not enchant and not hunspell:
            self.check_enabled = False
            return
        self.check_enabled = settings_get_bool("config/spelling")
        if self.check_enabled:
            self.highlighter.enable()
        else:
            self.highlighter.disable()
        self.highlighter.rehighlight()

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        if self.check_enabled:
            cursor = self.cursorForPosition(event.pos())
            cursor.select(QTextCursor.WordUnderCursor)

            if cursor.hasSelection():
                self.spelling_word = cursor.selectedText()
                if not self.dict.check(self.spelling_word):
                    spell_menu = QMenu("Spelling Suggestions")
                    spell_menu.setIcon(QIcon.fromTheme("tools-check-spelling"))

                    insertion_point = menu.actions()[0]
                    menu.insertMenu(insertion_point, spell_menu)
                    menu.insertSeparator(insertion_point)

                    for suggestion in self.dict.suggest(self.spelling_word):
                        spell_menu.addAction(SpellingAction(cursor, suggestion, spell_menu))
                    if len(spell_menu.actions()) == 0:
                        unavailable = spell_menu.addAction("(no suggestions)")
                        unavailable.setEnabled(False)

                    spell_menu.addSeparator()
                    spell_menu.addAction(QIcon.fromTheme("list-add"), "Add to Dictionary", self.add_to_dict)
                    spell_menu.addAction(QIcon.fromTheme("list-remove"), "Ignore All", self.ignore_all)
                    self.spell_menu = spell_menu

        menu.popup(event.globalPos())
        self.menu = menu

    def add_to_dict(self):
        self.dict.add(self.spelling_word)
        self.highlighter.rehighlight()

    def ignore_all(self):
        self.dict.add_to_session(self.spelling_word)
        self.highlighter.rehighlight()


class SpellingHighlighter(QSyntaxHighlighter):
    def __init__(self, dic, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self.enabled = False
        self.words = re.compile(r"(?u)(?<!\w)((\w[\w\']*\w)|(\w))(?!\w)")
        self.dict = dic

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def highlightBlock(self, text):
        if not self.enabled:
            return

        spelling_format = QTextCharFormat()
        spelling_format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        spelling_format.setUnderlineColor(Qt.red)

        # note: enchant provides a tokenizer, but it seems to be buggy (whitespace
        # doesn't break a word after numbers, e.g. "fred123 bill jim" is parsed as a
        # single word), so use our own regex.
        for word in self.words.finditer(text):
            if not self.dict.check(word.group()):
                self.setFormat(word.start(), word.end() - word.start(), spelling_format)


class SpellingAction(QAction):
    """An action to correct a misspelled word."""
    def __init__(self, cursor, replacement, *args):
        QAction.__init__(self, replacement, *args)
        self.cursor = cursor
        self.replacement = replacement
        self.triggered.connect(self.replace)

    def replace(self):
        self.cursor.beginEditBlock()
        self.cursor.removeSelectedText()
        self.cursor.insertText(self.replacement)
        self.cursor.endEditBlock()
