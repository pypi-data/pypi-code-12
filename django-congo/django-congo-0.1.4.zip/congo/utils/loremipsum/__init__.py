# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
import os
import random
import re

class LoremIpsum(object):
    LOREM_IPSUM = 'lorem_ipsum'
    PAN_TADEUSZ = 'pan_tadeusz'
    HAMLET = 'hamlet'
    GOSPODIN_PROKHARCHIN = 'gospodin_prokharchin'
    DER_ERLKONIG = 'der_erlkonig'

    GENERATOR_NAMES = (LOREM_IPSUM, PAN_TADEUSZ, HAMLET, GOSPODIN_PROKHARCHIN, DER_ERLKONIG)

    RE_SPACE = re.compile(r"[\s]+", re.UNICODE)
    RE_NON_WORD = re.compile(r"[^ \w']", re.UNICODE)
    MIN_WORD_LEN = 2

    def __init__(self, generator = None):
        if generator is None or generator not in self.GENERATOR_NAMES:
            generator = self.LOREM_IPSUM

        self.words = []

        text_path = self._get_file_path(generator)
        if os.path.exists(text_path):
            with open(text_path, 'r') as text_file:
                text = text_file.read().decode('utf-8')

                for word in self._escape(text).split():
                    if len(word) > self.MIN_WORD_LEN and word not in self.words:
                        self.words.append(word)

    @classmethod
    def _get_file_path(cls, filename):
        dirname = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dirname, 'sources', '%s.txt' % filename)

    @classmethod
    def _escape(cls, text):
        text = force_text(text)
        text = cls.RE_SPACE.sub(" ", text) # Standardize spacing.
        text = cls.RE_NON_WORD.sub("", text) # Remove non-word characters.
        return unicode(text.lower().strip())

    @classmethod
    def _make_sentence(cls, sentence):
        return "%s%s." % (sentence[0].upper(), sentence[1:])

    def get_words(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 3, 5
            else:
                max_len = min_len

        num = random.randint(min_len, max_len)
        if num > len(self.words):
            num = len(self.words)
        return random.sample(self.words, num)

    def get_phrase(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 3, 5
            else:
                max_len = min_len

        sentence = ' '.join(self.get_words(min_len, max_len))
        return "%s%s" % (sentence[0].upper(), sentence[1:])

    def get_sentence(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 7, 12
            else:
                max_len = min_len

        sentence = ' '.join(self.get_words(min_len, max_len))
        return self._make_sentence(sentence)

    def get_sentences(self, num, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 7, 12
            else:
                max_len = min_len

        return [self.get_sentence(min_len, max_len) for i in range(num)]

    def get_paragraph(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 4, 6
            else:
                max_len = min_len

        return ' '.join(self.get_sentences(random.randint(min_len, max_len)))

    def get_paragraphs(self, num, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 4, 6
            else:
                max_len = min_len

        return [self.get_paragraph(min_len, max_len) for i in range(num)]
