# -*- coding: UTF-8 -*-
#!/usr/bin/python
import re
import os

from .shared import Header, Alphabet
from .transducer import Transducer
from .transducer import TransducerW

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_MORPHAN_FILE = os.path.join(BASE_DIR, 'files/tatar_last.hfstol')
WORDS_FILE = os.path.join(BASE_DIR, 'files/words.csv')
EXCEPTIONS_FILE = os.path.join(BASE_DIR, 'files/exceptions.txt')

class Morphan:
    def __init__(self, 
                 transducerfile=None, 
                 wordsfile=None, 
                 exceptionsfile=None, 
                 params={}):
        '''
            Read a transducer from filename
        '''
        self.params = {'sdelimiter': u'\n',
                       'fdelimiter': u'\n'
                      }
        if not transducerfile:
            transducerfile = DEFAULT_MORPHAN_FILE
        if not wordsfile:
            wordsfile = WORDS_FILE
        if not exceptionsfile:
            exceptionsfile = EXCEPTIONS_FILE
        self.params.update(params)
            

        # loads the transducer
        handle = open(transducerfile, "rb")
        self.header = Header(handle)
        self.alphabet = Alphabet(handle, self.header.number_of_symbols)
        if self.header.weighted:
            self.transducer = TransducerW(handle, self.header, self.alphabet)
        else:
            self.transducer = Transducer(handle, self.header, self.alphabet)
        handle.close()

        # loads words and exceptions for better performance
        self.words = {}
        with open(exceptionsfile, 'rb') as stream:
            lines = stream.read().decode('UTF-8').split('\n')
        for line in lines:
            splits = line.split('\t')
            if len(splits) == 2:
                self.words[splits[0]] = splits[1]
        with open(wordsfile, 'rb') as stream:
            lines = stream.read().decode('UTF-8').split('\n')
        for line in lines:
            splits = line.split('\t')
            if len(splits) == 2:
                if splits[0] not in self.words:
                    self.words[splits[0]] = splits[1]

    def analyse(self, string):
        '''
            Take string to analyse, return a vector of (string, weight) pairs.
        '''
        if not isinstance(string, unicode):
            string = string.decode('utf8')
        if string.lower() in self.words:
            # return self.words[string.lower().decode('utf8')].encode('utf8')
            return self.words[string.lower()]

        if self.transducer.analyze(string):
            result = self.transducer.displayVector
            if len(result) == 0:
                return None
            # delete '+' sign in the end of analysis
            result = [row[0] if row[0][-1] != u'+' else row[0][:-1] for row in result]
            # delete duplicates and sort, then join with ';' delimiter
            return ';'.join(sorted(list(set(result)))) + ';'
        return None

    def lemma(self, string):
        """
            Returns the lemma of the word
        """
        analysed = self.analyse(string).strip(';')
        if analysed:
            return sorted(list(set([res.split(u'+')[0] for res in analysed.split(';')])))

    def pos(self, string):
        """
            Returns the part-of-speech of the word
            !TODO
        """
        analysed = self.analyse(string).strip(';')
        if analysed:
            return sorted(list(set([res.split(u'+')[1] for res in analysed.split(';')])))

    def process_text(self, text):
        """
            Parses text and analyses each lexical unit
        """
        sdelim = self.params.get('sdelimiter', u'\n')
        fdelim = self.params.get('fdelimiter', u'\n')
        if not isinstance(text, unicode):
            text = text.decode('utf8')

        letters = {u'ђ':u'ә', u'њ':u'ү', u'ќ':u'җ', u'љ':u'ө', u'ћ':u'ң',
                   u'џ':u'һ', u'Ә':u'ә', u'Ү':u'ү', u'Ө':u'ө', u'Җ':u'җ',
                   u'Һ':u'һ', u'Ң':u'ң', u'c':u'с', u'a':u'а'}
        # some texts contains words with not right letters, need to replace to right
        for letter in letters:
            text = text.replace(letter, letters[letter])

        # replace some errors
        text = text.replace(u'-\r\n', u'').replace(u'-\n\r', u'')\
                   .replace(u'-\n', u'').replace(u'-\r', u'')\
                   .replace(u'¬', u'').replace(u'...', u'…')\
                   .replace(u'!..', u'!').replace(u'?..', u'?')\
                   .replace(u' -', u' - ').replace(u'- ', u' - ')

        words = re.split(u"([ .,!?\n\r\t“”„‘«»≪≫\{\}\(\)\[\]:;\'\"+=*\—_^… ]|[0-9]+)", text)

        result = u''
        for word in words:
            if word.lower() in self.words:
                result += u'%s%s%s%s' % (word, sdelim, self.words[word.lower()], fdelim)
            elif word in [u'.', u'!', u'?', u'…']:
                result += u'%s%sType1%s' % (word, sdelim, fdelim)
            elif word in [u',', u':', u';', u'—', u'–', u'_']:
                result += u'%s%sType2%s' % (word, sdelim, fdelim)
            elif word in [u'(', u')', u'[', u']', u'{', u'}']:
                result += u'%s%sType3%s' % (word, sdelim, fdelim)
            elif word in [u'“', u'”', u'"', u"'", u'»', u'«', u'≪', u'≫', u'„', u'‘']:
                result += u'%s%sType4%s' % (word, sdelim, fdelim)
            elif word in [u' ', u' ', u'', u'\n', u'\n\r', u'\r', u'\t']:
                pass
            elif re.match('^[а-эА-ЭөүһңҗҺҮӨҖҢЁё]$', word):
                result += u'%s%sLetter%s' % (word, sdelim, fdelim)
            elif word.isdigit():
                result += u'%s%sNum%s' % (word, sdelim, fdelim)
            elif re.match('^[a-zA-Z]+$', word):
                result += u'%s%sLatin%s' % (word, sdelim, fdelim)
            elif re.match('^[^а-яА-ЯөүһңҗәҺҮӨҖҢӘЁё]$', word):
                result += u'%s%sSign%s' % (word, sdelim, fdelim)
            elif (re.match(u'[а-яА-ЯөӨүҮһҺңҢҗҖәӘЁё]+$', word)) \
                 or (re.match(u'[а-яА-ЯөӨүҮһҺңҢҗҖәӘЁё]+\-[а-яА-ЯөӨүҮһҺңҢҗҖЁёәӘ]+$', word)):
                if word.count("-") > 1:
                    result += u'%s%sError%s' % (word, sdelim, fdelim)
                else:
                    res = self.analyse(word)
                    if not res:
                        word = word.lower()
                        res = self.analyse(word)
                        if not res:
                            word = word.replace(u'һ', u'х')
                            res = self.analyse(word)
                            if not res:
                                word = word.replace(u'-', u'')
                                res = self.analyse(word)
                                if not res:
                                    result += u'%s%sNR%s' % (word, sdelim, fdelim)
                                    continue
                    result += u'%s%s%s%s' % (word, sdelim, res, fdelim)
            else:
                result += u'%s%sError%s' % (word, sdelim, fdelim)
        return result

    def disambiguated(self, text):
        """
            Parses text, analyses it and disambiguate morphological ambiguities
        """
        return self.process_text(text)
