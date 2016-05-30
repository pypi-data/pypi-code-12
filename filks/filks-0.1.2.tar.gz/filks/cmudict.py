import itertools
import string
import re
import pkgutil
try:
    import inflect
    inflection = inflect.engine()
except:
    inflection = None


VOWELS = set('AEIOU')


def _is_vowel_phoneme(phoneme):
    return phoneme[0] in VOWELS


SPLIT_LETTERS_AND_NUMBERS_REGEX = re.compile('\d+|\D+')


RESOURCE_PACKAGE = 'filks.resources.cmudict'


def resource(resource_name, encoding='utf-8'):
    return pkgutil.get_data(RESOURCE_PACKAGE, resource_name).decode(encoding)


class CmuDict(object):
    DEFAULT_ENCODING = 'latin1'
    DEFAULT_COMMENT = ';;;'

    def __init__(
            self,
            path=None,
            encoding=DEFAULT_ENCODING,
            comment=DEFAULT_COMMENT,
    ):
        """
        Load the dictionary.

        :param path: Path to dictionary file to load; `None` to use packaged file (if present).
        :param url: URL to fetch if dictionary filename does not exist.
        :param encoding:
        :param comment:
        :return:
        """
        self.path = path

        if not path:
            from nltk.corpus import cmudict
            data = cmudict.raw()
        else:
            with open(self.path, 'r', encoding=encoding) as f:
                data = f.read()

        # TODO: handle multiple pronunciations, etc.

        self.__pron = dict()
        for line in data.splitlines(False):
            line = line.strip().upper()
            if not line or line.startswith(comment):
                continue
            parts = line.split()
            if len(parts) > 1:
                self.__pron[parts[0]] = tuple(parts[1:])

    def phonemes(self, word):
        if not word:
            return ()
        while word.startswith('$'):
            word = word[1:] + '-DOLLARS'
        word = word.replace('%', '-PERCENT-')
        word = word.strip('.,;:-(){}[]"\'`!?@#& /')
        word = word.replace('/', '-OVER-')
        word = word.replace('.', '-POINT-')
        word = word.replace('+', '-PLUS-')
        word = word.replace('*', '-STAR-')
        word = word.replace(':', '-')
        word = word.replace(' ', '-')
        word = word.replace(',', '')
        word = word.upper()
        if not word:
            return ()
        pron = self.__pron.get(word)
        if pron:
            return pron
        elif '-' in word:
            return tuple(itertools.chain.from_iterable(self.phonemes(part) for part in word.split('-')))
        elif len(set(word) & set(string.digits)) > 0 and not word.isdigit():
            # Contains digits & non-digits, split into sections
            return tuple(itertools.chain.from_iterable(self.phonemes(part) for part in SPLIT_LETTERS_AND_NUMBERS_REGEX.findall(word)))
        elif inflection and word.isdigit():
            return self.phonemes(inflection.number_to_words(word, comma=''))
        else:  # Try to find "perfect" split
            longest_index = None
            longest_ending = None
            for i in range(1, len(word)):
                w0, w1 = word[:i], word[i:]
                p0, p1 = self.__pron.get(w0), self.__pron.get(w1)
                if p0 and p1:
                    return p0 + p1
                elif longest_ending is None and p1:
                    longest_index = i
                    longest_ending = p1
            # No perfect split, see if we can find overlap with longest ending
            if not longest_ending:
                print([ord(c) for c in word])
                raise RuntimeError('Could not find {}'.format(word)) # Shouldn't happen because dict has every letter, I think?

            for i in range(longest_index+1, len(word)-1):
                w0 = word[:i]
                p0 = self.__pron.get(w0)
                if p0:
                    for i in range(min(len(p0), len(longest_ending)), 0, -1):
                        if p0[-i:] == longest_ending[:i]:
                            return p0[:-i] + longest_ending
                    else:
                        return p0 + longest_ending
            else:
                # This is a really dumb hack, but may help for rhymes, etc.
                return (word[:longest_index],) + longest_ending

    def vowel_syllables(self, word):
        syllables = list()
        parts = list()
        for phoneme in self.phonemes(word):
            if _is_vowel_phoneme(phoneme):
                if parts:
                    syllables.append(''.join(parts))
                parts = list()
            parts.append(phoneme)
        if parts:
            syllables.append(''.join(parts))
        return tuple(syllables)

    def syllable_count(self, word):
        return len(list(phoneme for phoneme in self.phonemes(word) if _is_vowel_phoneme(phoneme)))

    def rhymed_syllables(self, *words):
        ps = list(set(syllables) for syllables in zip(*(reversed(self.vowel_syllables(word)) for word in words)))
        for i in range(len(ps)):
            if len(ps[i]) > 1:
                return i
        else:
            return len(ps)

    def rhymed_phonemes(self, *words):
        ps = list(set(phonemes) for phonemes in zip(*(reversed(self.phonemes(word)) for word in words)))
        for i in range(len(ps)):
            if len(ps[i]) > 1:
                return i
        else:
            return len(ps)
