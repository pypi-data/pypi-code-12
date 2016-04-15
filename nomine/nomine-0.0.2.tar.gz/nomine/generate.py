import statistics
from pykov import Vector
import random

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
echo = pp.pprint


class NomineException(Exception):
    pass

def split_letters(line, n=1):
    return [line[i:i+n] for i in range(0, len(line), n)]

class Nomine:
    def __init__(self, corpus=None, source=None, preset=None, splitter=None):
        if type(source) is str:
            with open(source) as f:
                content = f.readlines()
                content = [f.replace('\n', '') for f in content]
                self.corpus = content
        if type(preset) is str:
            with open("./nomine/names/{}.txt".format(preset)) as f:
                content = f.readlines()
                content = [f.replace('\n', '') for f in content]
                self.corpus = content
        elif type(corpus) is list:
            self.corpus = corpus
        else:
            raise NomineException("Corpus list or file location must be supplied.")

        self.corpus = [w.lower() for w in self.corpus]
        word_lengths = [len(w) for w in self.corpus]
        self.avg = sum(word_lengths) / len(self.corpus)
        self.std_dev = statistics.stdev(word_lengths)
        if splitter is None:
            splitter = split_letters
        word_char_list = [splitter(w) for w in self.corpus]

        freq = {}

        for word in word_char_list:
            for key, char in enumerate(word):
                try:
                    next_char = word[key + 1]
                    if char not in freq:
                        freq[char] = {}
                    if next_char in freq[char]:
                        freq[char][next_char] += 1
                    else:
                        freq[char][next_char] = 1
                except IndexError:
                    pass

        self.vectors = {}
        for letter1, letter_dict in freq.items():
            sum_keys = sum(list(letter_dict.values()))
            prob = {}
            for letter2, count in letter_dict.items():
                prob[letter2] = count / sum_keys
            self.vectors[letter1] = Vector(prob)


    def _generate(self, size=None):
        "Generates a new word"
        corpus_letters = list(self.vectors.keys())
        current_letter = random.choice(corpus_letters)
        if size is None:
            size = int(random.normalvariate(self.avg, self.std_dev))

        letters = [current_letter]

        for _ in range(size):
            if current_letter not in corpus_letters:
                # current_letter = random.choice(corpus_letters)
                break
            found_letter = self.vectors[current_letter].choose()
            letters.append(found_letter)
            current_letter = found_letter

        return ''.join(letters)

    def get(self, length=None):
        while True:
            word = self._generate(size=length)
            if word not in self.corpus:
                return word.capitalize()

    def max_names(self):
        names = []
        for _ in range(1000000):
            name = self.get()
            if name in names:
                return _
            else:
                names.append(name)
