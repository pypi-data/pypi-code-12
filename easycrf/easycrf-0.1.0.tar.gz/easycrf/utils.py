"""
Contains a collection of utility functions
"""

from __future__ import print_function
from crfutils import readiter, output_features
from nltk import word_tokenize
import re

def write_crf_file(filename, document, separator=' '):
    """
    Takes a tagged document (a list of tagged sentences) and writes it
    to a file which is structured like y w pos. Here y denotes the label
    of the token, w is the token itself and pos is the pos tag of the token

    Example:
    Input: [[(0, 6, 'Verden', 'O', 'NE'), (6, 7, '/', 'O', '$['), (7, 19, 'MünchenNeuer', 'O', 'NE'), (20, 32, 'gigantischer', 'O', 'ADJA'), (33, 38, 'Daten', 'O', 'NN'), ... ]]

    Output:
    O Verden NE
    O / $[
    O MünchenNeuer NE
    O gigantischer ADJA
    O Daten NN
    ...

    :param filename: the file to write the output to
    :param document: the tagged documents data that should be transformed into a crf file
    :param seperator: the seperator to use in oder to sperate the elements
    """
    output = open(filename, 'w')
    for sentence in document:
        for token in sentence:
            output.write(token[3] + separator + token[2] + separator + token[4] + "\n")
        output.write("\n")
    output.close()


def read_ann_file(filename):
    """
    Read the annotation (*.ann) file which contains the annotations produced by the brat tool
    :param filename: the file to read the annotations from
    :return: a dictionary with all the read in annotations. Format { LABEL : [ANNOTATIONS] }
    Example:
        {
            COMP : [(T1, COMP, 33, 39, Prokon), ...],
            ORG : [ ..., (T4, ORG, 817, 826, Foodwatch), ...]
        }
    """
    pattern = re.compile('(T\d+)\t([A-Za-z0-9-]+)\s(\d+)\s(\d+)\t(.*)')
    elements = {}

    with open(filename.rstrip(), 'r') as file:
        lines = file.readlines()
        for line in lines:
            match = pattern.match(line)
            if match:
                elements[match.group(2)] = elements.get(match.group(2), []) + [
                    (match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))]
            else:
                raise Exception(file.name+': '+line, 'Could not match the line.')

    return elements


def read_txt_file(filename):
    """
    Read the txt file containing all sentences from brat.
    :param filename: the txt file to read.
    :return: a list of all sentences in the txt file.
    Example:
        [Sentence1, Sentence2, Sentence3, ...]
    """
    result = []
    with open(filename.rstrip(), 'r') as file:
        lines = file.readlines()
        for line in lines:
            result.append(line)
        file.close()

    return result

def read_pos_file(filename):
    """
    Read the txt file containing all sentences from brat.
    :param filename: the txt file to read.
    :return: a list of all sentences in the txt file.
    Example:
        [Sentence1, Sentence2, Sentence3, ...]
    """
    result = []
    with open(filename.rstrip(), 'r') as file:
        lines = file.readlines()

        sentence = []
        for line in lines:
            splitted_line = line.split(' ')

            if len(splitted_line) > 1:
                sentence.append((splitted_line[0], splitted_line[1], splitted_line[2].strip()))
            else:
                result.append(sentence)
                sentence = []

        if len(sentence) > 0:
            result.append(sentence)

    return result


def remove_unicode_chars(input):
    """
    This function removes all unicode characters contained in the chars
    array from the input string.

    Example:

    '³Beisp²iel¹' ---> 'Beispiel'

    :param input: the string to remove unicode chars from
    :return: the string with removed unicode chars
    """
    chars = ['¹', '²', '³']

    for char in chars:
        input = input.replace(char, '')

    return input


def tokenize_text(text):
    """
    Tokenize the given text.
    :param text: the text to be tokenized
    :return: a list of tokens
    """
    splitted_annotations = []
    text = remove_unicode_chars(text)
    tokenized_text = word_tokenize(text, language='german')

    # do dome further post processing
    for token in tokenized_text:
        splitted_words = re.split('(\W)', token)
        splitted_annotations.extend(splitted_words)

    return list(filter(None, splitted_annotations))


def apply_feature_extractor(crf_file, out_file, feature_extractor, fields='y w pos', separator=' '):
    """
    This function takes a feature extractor and applies it to the crf input file. It generates
    a feature file which can be used to train a model using crfsuite.

    :param crf_file: the crf file the feature extractor operates on
    :param out_file: the result of applying the feature extractor
    :param feature_extractor: the feature extractor that should be used
    :param fields: the fields in the crf file
    :param separator: the separator that should be used
    """
    file_in = open(crf_file, 'r')
    file_out = open(out_file, 'w')
    fields = fields.split(' ')

    # The generator function readiter() reads a sequence from a
    for X in readiter(file_in, fields, separator):
        feature_extractor(X)
        output_features(file_out, X, 'y')

    file_in.close()
    file_out.close()

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from crfutils import readiter, output_features

