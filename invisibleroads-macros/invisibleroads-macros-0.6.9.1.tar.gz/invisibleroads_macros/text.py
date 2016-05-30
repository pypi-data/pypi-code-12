import re


WHITESPACE_PATTERN = re.compile(r'\s+', re.MULTILINE)
PUNCTUATION_PATTERN = re.compile(r'[^a-zA-Z\s]+')


def parse_words(x):
    return x.replace(',', ' ').split()


def strip_whitespace(string):
    return WHITESPACE_PATTERN.sub('', string)


def compact_whitespace(string):
    return WHITESPACE_PATTERN.sub(' ', string).strip()


def remove_punctuation(string):
    return compact_whitespace(PUNCTUATION_PATTERN.sub(' ', string))
