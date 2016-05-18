# -*- encoding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import math
import codecs
import bs4
from collections import namedtuple
from .logger import logger


# This magic number scales the document size distribution of the 2016 Internet
# to a pretty-looking maximum error count distribution. Based on a sample of
# 3000+ documents and eyeballing the distribution.
# https://www.getguesstimate.com/models/5034
MAGIC_NUMBER = 100000


# To minimize the chance that the replacement character/string is contained in
# the original document, we use a longer string.
MAGIC_STRING = '[utilofies decoding error]'

def replace_with_string(exc):
    return (MAGIC_STRING, exc.end)
codecs.register_error('replace-with-string', replace_with_string)


# UnicodeDammit was refactored a lot recently.
# It now falls back on cchardet if it’s in the path.
# Otherwise, we have to make sure that it does *not* fall back on
# chardet as it is slow and has only minimal charset coverage.
if not 'cchardet' in bs4.dammit.__dict__:
    # Either chardet or nothing
    bs4.dammit.chardet_dammit = lambda string: None


Candidate = namedtuple('Candidate', ['markup', 'encoding', 'error_count'])
MockDammit = namedtuple('MockDammit', ['contains_replacement_characters', 'detector', 'is_html',
                                       'markup', 'original_encoding', 'tried_encodings',
                                       'unicode_markup'])


def intelligent_decode(markup, override_encodings=None, is_html=False, max_error_interval=(0, 0)):
    """
    A wrapper for UnicodeDammit that is still a bit better in my opinion.

    A common problem is that the declared encoding is human-correct (the human would say it’s
    correct) but can’t decode one erroneous character somewhere in the document. Hence decoders
    usually fall back on some encoding that is completely human-wrong and breaks lots of characters
    – sometimes silently because the encoding may actually recognize the byte strings but
    associate them with human-wrong characters.

    The idea is that of all candidate encodings that work with `errors='replace'` set, first the
    first declared encoding is chosen. If it results in enough errors to exceed some threshold, the
    second is chosen and so on. Only in the case where all encodings result in error counts that
    exceed the threshold do we fall back on the first declared encoding.

    `max_error_interval` defines the range of the absolute number of errors to tolerate, which is
    larger for larger documents.

    # = error
    v = max_absolute_errors
    < = selected encoding

    Encoding    Error count  Exceeds limit  Selected
                   v
    Encoding 1: #####        False
    Encoding 2: ###          True           <
    Encoding 3:              True

                   v
    Encoding 1: #####        False          <
    Encoding 2: ######       False
    Encoding 3: #####        False
    """
    if isinstance(markup, unicode):
        logger.warn('Tried to decode Unicode!')
        return MockDammit(
            contains_replacement_characters='�' in markup,
            original_encoding=None,
            detector=None,
            is_html=is_html,
            markup=markup,
            tried_encodings=[],
            unicode_markup=markup)
    detector = bs4.dammit.EncodingDetector(markup, override_encodings, is_html)
    detector.declared_encoding = \
        detector.find_declared_encoding(markup, is_html)
    # This formula maps the length of the document to a maximum error count. The arctan can
    # assume values of up to pi/2, so by dividing by that I first scale it to [0, 1] and then,
    # with the multiplication and addition, up again to the desired interval. In the default
    # case of max_error_interval=(0, 0), the result is 0. See also the magic number comment above.
    low, high = max_error_interval
    max_absolute_errors = math.atan(len(markup) / 120000) / (math.pi/2) * (high-low) + low
    # I use override_encodings for the HTTP encoding,
    # which seems about as reliable to me as the declared encoding
    # if it is present.
    potential_encodings = \
        filter(bool, [detector.sniffed_encoding, detector.declared_encoding]
                     + list(detector.override_encodings)) + ['utf-8']
    candidates = []
    best_candidate = None
    for encoding in potential_encodings:
        try:
            markup = detector.markup.decode(encoding, 'replace-with-string')
        except UnicodeDecodeError as excp:
            logger.info('Unsuccessfully tried forcing encoding %s: %s(%r, %r, %r, %r)',
                        encoding, type(excp).__name__, excp.encoding, excp.start, excp.end,
                        excp.reason)
        else:
            error_count = markup.count(MAGIC_STRING)
            candidate = Candidate(markup.replace(MAGIC_STRING, '�'), encoding, error_count)
            candidates.append(candidate)
            if error_count <= max_absolute_errors:
                # Shortcut: If one of them, in order, is below the error ratio, we’re done.
                best_candidate = candidate
                break
    if not best_candidate:
        # Now we have to fall back on the least bad solution.
        best_candidate = candidates[0]
        logger.warn('All candidate decodings exceed the maximum error count of %s. '
                    'Falling back on %s with error count %s.',
                    max_absolute_errors, best_candidate.encoding, best_candidate.error_count)
    return MockDammit(
        contains_replacement_characters=bool(best_candidate.error_count),
        original_encoding=best_candidate.encoding,
        detector=detector,
        is_html=detector.is_html,
        markup=detector.markup,
        tried_encodings=[candidate.encoding for candidate in candidates],
        unicode_markup=best_candidate.markup)


def intelligent_detect_encoding(markup, is_html=False):
    """ Don’t use this function at this time.
    """
    chardet_dammit = bs4.dammit.chardet_dammit
    bs4.dammit.chardet_dammit = lambda string: None
    dammit = bs4.dammit.UnicodeDammit(markup, is_html=is_html)
    bs4.dammit.chardet_dammit = chardet_dammit
    if dammit.contains_replacement_characters:
        return None
    return dammit.original_encoding
