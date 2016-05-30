import re
from collections import Counter
import random
import itertools
try:
    import inflect
    inflector = inflect.engine()
except:
    inflector = None
from collections import namedtuple


TAG_REGEX_STR = r'\w+(-\+\*\$\w)*'


TAG_REGEX = re.compile('[/]\w+(-\+\*\$\w)*')

FORMAT_REGEX = re.compile(r'\{([^\}]+)\}')
RHYME_FORMAT_REGEX = re.compile(r'\{([^\}]+\#[^\}]+)\}')


class WordField(namedtuple('WordField', ['example', 'inflection', 'poses', 'rhyme', 'const', 'value'])):
    def inflect(self, word, pos):
        if pos and inflector and self.count is not None:
            pos_upper = pos.upper()
            if self.count == 1:
                if pos_upper == 'NNS':
                    word = inflector.singular_noun(word)
            else:
                if pos_upper.startswith('N') and not pos_upper.endswith('S'):
                    word = inflector.plural_noun(word)
                elif pos_upper == 'VBZ':
                    word = inflector.plural_verb(word)

        if self.example:
            if self.example.startswith('?'):
                return ''
            if self.example.lower().startswith('a ') or self.example.lower().startswith('an '):
                if inflector:
                    word = inflector.a(word)
                else:
                    if word[0] in 'aeiou':
                        word = 'an {}'.format(word)
                    else:
                        word = 'a {}'.format(word)

            if self.example == self.example.capitalize():
                word = word.capitalize()
            elif self.example.isupper():
                word = word.upper()

        return word

    def __count(self, pos):
        pos_upper = pos.upper()
        if pos_upper.startswith('N'):
            return 2 if pos_upper.endswith('S') else 1
        if pos_upper == 'VBZ':
            return 1
        elif pos_upper == 'VB':
            return 2
        return None

    @property
    def count(self):
        return int(self.inflection) if self.inflection else None


def expand_wordfield(field, pos_fixer=lambda x: [x], valdefs={}):
    try:
        field = field.group(1)
    except:
        pass
    field = field.strip().strip('{}').strip()
    original_field = field

    if '/' in field:
        example, field = field.split('/', 1)
    else:
        example = None

    if example and ':' in example:
        example, inflection = example.split(':', 1)
    else:
        inflection = None

    if '=' in field:
        field, def_name = field.split('=', 1)
    else:
        def_name = None

    if '#' in field:
        field, rhyme_name = field.split('#', 1)
    else:
        rhyme_name = None

    if def_name in valdefs:
        value = valdefs[def_name]
    else:
        value = None

    return WordField(example, inflection, pos_fixer(field), rhyme_name, def_name, value)




def _iter_range_out(index, start, stop=None, step=1):
    if stop is None:
        start, stop = 0, start

    top = index
    bottom = index - step
    while top < stop or bottom >= start:
        if top < stop:
            yield top
            top += step
        if bottom >= start:
            yield bottom
            bottom -= step


class TaggedText(object):
    def __init__(self, text, dictionary=None, syllables=True):
        self.__dictionary = dictionary
        self.__syllables = syllables

        if isinstance(text, str):
            if text.count('/') > text.count(' ') / 4:
                self.__words = [w.rsplit('/', 1) for w in text.split() if '/' in w]
            else:
                import nltk
                self.__words = nltk.word_tokenize(text)
        elif isinstance(text[0], str):
            self.__words = nltk.word_tokenize(text)
        else:
            self.__words = text

        self.__sel = dict()
        self.__tags = set(w[1] for w in self.__words)
        self.__allupper = all(tag == tag.upper() for tag in self.__tags)
        self.__alllower = all(tag == tag.lower() for tag in self.__tags)

        if self.__dictionary:
            self.__prep = dict()
            for i, (word, pos) in enumerate(self.__words):
                for syllable_count in self.__syllable_counts(word):
                    rhyme = self.__dictionary.vowel_syllables(word)
                    if rhyme:
                        rhyme = rhyme[-1]
                        key = (pos, syllable_count)
                        if key not in self.__prep:
                            self.__prep[key] = dict()
                        if rhyme not in self.__prep[key]:
                            self.__prep[key][rhyme] = (set(), set())
                        self.__prep[key][rhyme][0].add(i)
                        self.__prep[key][rhyme][1].add(word.lower())
        else:
            self.__prep == None

        self.__reset()

    def __reset(self, pointer=-1):
        self.__p = pointer if 0 <= pointer < len(self.__words) else random.randrange(len(self.__words))
        self.__locations = Counter()
        self.__rhymes = dict()
        self.__used = Counter()
        self.__defs = dict()
        return self

    def __use(self, field, location):
        self.__locations[location] += 1
        word, pos = self.__words[location]
        self.__used[word.lower()] += 1

        if field.rhyme and field.rhyme not in self.__rhymes:
            self.__rhymes[field.rhyme] = word
        if field.const:
            self.__defs[field.const] = (word, pos)
        return field.inflect(word, pos)

    def __use_count(self, location):
        return self.__locations.get(location, 0) + self.__used.get(self.__words[location][0].lower(), 0)

    def __fix_pos(self, pos):
        pos = pos.strip()
        pos = pos.strip('/')
        if self.__allupper:
            pos = pos.upper()
        if self.__alllower:
            pos = pos.lower()
        return tuple(p.strip() for p in pos.split('/') if p.strip() in self.__tags)

    def __syllable_count(self, word):
        if word and self.__dictionary and self.__syllables:
            return self.__dictionary.syllable_count(word)
        else:
            return 0

    def __syllable_counts(self, word):
        if word and self.__dictionary:
            yield self.__dictionary.syllable_count(word)
        yield 0

    def __fix_field(self, field):
        return expand_wordfield(field, self.__fix_pos, self.__defs)

    def format(self, text):
        if self.__prep:
            rhyme_keys = dict()
            for match in RHYME_FORMAT_REGEX.finditer(text):
                field = self.__fix_field(match)
                if field.rhyme not in rhyme_keys:
                    rhyme_keys[field.rhyme] = list()
                rhyme_keys[field.rhyme].append([(pos, self.__syllable_count(field.example)) for pos in field.poses])

            for rhyme_name, keys in rhyme_keys.items():
                if len(keys) <= 1:
                    continue
                for syllable_multiplier in ((1, 0) if self.__syllables else (0,)):
                    try:
                        allowed_rhymes = list(
                            set.intersection(*(
                                set.union(*(
                                    set(self.__prep[key[0], key[1] * syllable_multiplier].keys()) for key in keylist
                                )) for keylist in keys
                            ))
                        )
                    except KeyError:
                        continue
                    random.shuffle(allowed_rhymes)

                    best_rhymes = None
                    best_rhymes_indices = None
                    best_rhymes_distance = float('inf')
                    for allowed_rhyme in allowed_rhymes:
                        if len(set.union(*(
                                itertools.chain.from_iterable(
                                    (self.__prep[key[0], key[1] * syllable_multiplier][allowed_rhyme][0] for key in keylist)
                                    for keylist in keys
                                )
                            ))) < len(keys):
                            continue
                        word_lowers = set()
                        rhyming_words = list()
                        rhyming_indices = list()
                        distance = 0
                        for keylist in keys:
                            locations = set.union(*(self.__prep[key[0], key[1] * syllable_multiplier][allowed_rhyme][0] for key in keylist))
                            for i in _iter_range_out(self.__p, len(self.__words)):
                                if i not in locations:
                                    continue
                                word = self.__words[i][0]
                                word_lower = word.lower()
                                if word_lower not in word_lowers:
                                    word_lowers.add(word_lower)
                                    rhyming_words.append(word)
                                    rhyming_indices.append(i)
                                    distance += abs(i - self.__p) + 100 * self.__use_count(i)
                                    break
                            else:
                                break  # Didn't find permissible result
                        else:
                            # Still ok
                            if best_rhymes is None or distance < best_rhymes_distance:
                                best_rhymes = rhyming_words
                                best_rhymes_indices = rhyming_indices
                                best_rhymes_distance = distance
                    if best_rhymes and len(best_rhymes) >= len(keys):
                        text = re.sub(
                            r'\{([^\}]+\#' + rhyme_name + r'(=[^\}]*)?)\}',
                            lambda m: self.__use(self.__fix_field(m), best_rhymes_indices.pop(0)),
                            text
                        )
                        break

        return FORMAT_REGEX.sub(self.get, text)

    def get(self, pos):
        """

        :param pos: a part-of-speech of format `[example[:N]/]pos[/pos][/pos][...][#rhyme][=equals]`
        :return:
        """
        original_pos = pos
        field = self.__fix_field(pos)

        syllable_count = self.__syllable_count(field.example)

        if field.const:
            val = self.__defs.get(field.const, None)
            if val:
                return field.inflect(*val)

        rhyming_word = self.__rhymes.get(field.rhyme)

        if not field.poses:
            if field.example:
                return field.inflect(field.example, None)
            else:
                raise RuntimeError('No tags {} in file! (Originally `{}`)'.format(pos, original_pos))

        best = None
        best_count = float('inf')

        for nextp in _iter_range_out(self.__p, len(self.__words)):
            word, wpos = self.__words[nextp]
            if wpos in field.poses:
                if syllable_count != self.__syllable_count(word):
                    continue
                if self.__dictionary and rhyming_word:
                    if self.__dictionary.rhymed_syllables(rhyming_word, word) >= 2:
                        pass
                    else:
                        continue

                count = self.__use_count(nextp)
                if not count:
                    break
                elif best is None or count < best_count:
                    best = nextp
                    best_count = count
        else:
            if best is not None:
                nextp = best
            elif field.example:
                return field.example
            else:
                raise RuntimeError('Could not find pos `{}`'.format(pos))

        self.__p = nextp
        return self.__use(field, nextp)
