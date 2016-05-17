from __future__ import print_function

import glob
import os
import re
import subprocess
import tempfile
from functools import reduce
from operator import add

from nltk.data import ZipFilePathPointer
from nltk.internals import find_binary
from nltk.parse.api import ParserI
from nltk.tag import RegexpTagger
from pymystem3 import Mystem
import numpy as np

from format import MorphyFormatConverter
from syntax.maltparser.dependencygraph import DependencyGraph

regex = re.compile("[,=]")


class MaltParser(ParserI):
    def __init__(self, tagger=None, mco=None, working_dir=None, additional_java_args=None):
        """
        An interface for parsing with the Malt Parser.

        :param mco: The name of the pre-trained model. If provided, training
            will not be required, and MaltParser will use the model file in
            ${working_dir}/${mco}.mco.
        :type mco: str
        """
        self.config_malt()
        self.mco = 'malt_temp' if mco is None else mco
        self.working_dir = tempfile.gettempdir() if working_dir is None \
            else working_dir
        self.additional_java_args = [] if additional_java_args is None else additional_java_args
        self._trained = mco is not None

        if tagger is not None:
            self.tagger = tagger
        else:
            self.tagger = RegexpTagger(
                [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
                 (r'(The|the|A|a|An|an)$', 'AT'),  # articles
                 (r'.*able$', 'JJ'),  # adjectives
                 (r'.*ness$', 'NN'),  # nouns formed from adjectives
                 (r'.*ly$', 'RB'),  # adverbs
                 (r'.*s$', 'NNS'),  # plural nouns
                 (r'.*ing$', 'VBG'),  # gerunds
                 (r'.*ed$', 'VBD'),  # past tense verbs
                 (r'.*', 'NN')  # nouns (default)
                 ])

    def config_malt(self, bin=None, verbose=False):
        """
        Configure NLTK's interface to the ``malt`` package.  This
        searches for a directory containing the malt jar

        :param bin: The full path to the ``malt`` binary.  If not
            specified, then nltk will search the system for a ``malt``
            binary; and if one is not found, it will raise a
            ``LookupError`` exception.
        :type bin: str
        """
        #: A list of directories that should be searched for the malt
        #: executables.  This list is used by ``config_malt`` when searching
        #: for the malt executables.
        _malt_path = ['.',
                      '/usr/lib/malt-1*',
                      '/usr/share/malt-1*',
                      '/usr/local/bin',
                      '/usr/local/malt-1*',
                      '/usr/local/bin/malt-1*',
                      '/usr/local/malt-1*',
                      '/usr/local/share/malt-1*']

        # Expand wildcards in _malt_path:
        malt_path = reduce(add, map(glob.glob, _malt_path))

        # Find the malt binary.
        self._malt_bin = find_binary('malt.jar', bin,
                                     searchpath=malt_path, env_vars=['MALT_PARSER'],
                                     url='http://www.maltparser.org/',
                                     verbose=verbose)

    def parse_sents(self, sentences, verbose=False):
        """
        Use MaltParser to parse multiple sentences. Takes multiple sentences as a
        list where each sentence is a list of words.
        Each sentence will be automatically tagged with this MaltParser instance's
        tagger.

        :param sentences: Input sentences to parse
        :type sentence: list(list(str))
        :return: iter(DependencyGraph)
        """
        tagged_sentences = [self.tagger.tag(sentence) for sentence in sentences]
        return iter(self.tagged_parse_sents(tagged_sentences, verbose))

    def tagged_parse(self, sentence, verbose=False):
        """
        Use MaltParser to parse a sentence. Takes a sentence as a list of
        (word, tag) tuples; the sentence must have already been tokenized and
        tagged.

        :param sentence: Input sentence to parse
        :type sentence: list(tuple(str, str))
        :return: iter(DependencyGraph) the possible dependency graph representations of the sentence
        """
        return next(self.tagged_parse_sents([sentence], verbose))

    def tagged_parse_sents(self, sentences, verbose=False):
        """
        Use MaltParser to parse multiple sentences. Takes multiple sentences
        where each sentence is a list of (word, tag) tuples.
        The sentences must have already been tokenized and tagged.

        :param sentences: Input sentences to parse
        :type sentence: list(list(tuple(str, str, str)))
        :return: iter(iter(``DependencyGraph``)) the dependency graph representation
                 of each sentence
        """

        if not self._malt_bin:
            raise Exception("MaltParser location is not configured.  Call config_malt() first.")
        if not self._trained:
            raise Exception("Parser has not been trained.  Call train() first.")

        input_file = tempfile.NamedTemporaryFile(prefix='malt_input.conll',
                                                 dir=self.working_dir,
                                                 delete=False)
        output_file = tempfile.NamedTemporaryFile(prefix='malt_output.conll',
                                                  dir=self.working_dir,
                                                  delete=False)

        try:
            for sentence in sentences:
                for (i, (word, lemma, tag, features)) in enumerate(sentence, start=1):
                    input_str = u'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % \
                                (i, word, lemma if lemma else '_', tag, tag, features if features else '_', '0', 'a',
                                 '_', '_')
                    input_file.write(input_str.encode('utf-8'))
                input_file.write(b'\n\n')
            input_file.close()

            cmd = ['java'] + self.additional_java_args + ['-jar', self._malt_bin,
                                                          '-w', self.working_dir,
                                                          '-c', self.mco, '-i', input_file.name,
                                                          '-o', output_file.name, '-m', 'parse']

            #print('MaltCommand:')
            #rint(' '.join(cmd))
            ret = self._execute(cmd, verbose)
            if ret != 0:
                raise Exception("MaltParser parsing (%s) failed with exit "
                                "code %d" % (' '.join(cmd), ret))

            # Must return iter(iter(Tree))
            return (iter([dep_graph]) for dep_graph in DependencyGraph.load(output_file.name))
        finally:
            print(output_file.read())
            input_file.close()
            os.remove(input_file.name)
            output_file.close()
            os.remove(output_file.name)

    def train(self, depgraphs, verbose=False):
        """
        Train MaltParser from a list of ``DependencyGraph`` objects

        :param depgraphs: list of ``DependencyGraph`` objects for training input data
        """
        input_file = tempfile.NamedTemporaryFile(prefix='malt_train.conll',
                                                 dir=self.working_dir,
                                                 delete=False)
        try:
            input_str = ('\n'.join(dg.to_conll(10) for dg in depgraphs))
            input_file.write(input_str.encode("utf8"))
            input_file.close()
            self.train_from_file(input_file.name, verbose=verbose)
        finally:
            input_file.close()
            os.remove(input_file.name)

    def train_from_file(self, conll_file, verbose=False):
        """
        Train MaltParser from a file

        :param conll_file: str for the filename of the training input data
        """
        if not self._malt_bin:
            raise Exception("MaltParser location is not configured.  Call config_malt() first.")

        # If conll_file is a ZipFilePathPointer, then we need to do some extra
        # massaging
        if isinstance(conll_file, ZipFilePathPointer):
            input_file = tempfile.NamedTemporaryFile(prefix='malt_train.conll',
                                                     dir=self.working_dir,
                                                     delete=False)
            try:
                conll_str = conll_file.open().read()
                conll_file.close()
                input_file.write(conll_str)
                input_file.close()
                return self.train_from_file(input_file.name, verbose=verbose)
            finally:
                input_file.close()
                os.remove(input_file.name)

        cmd = ['java', '-jar', self._malt_bin, '-w', self.working_dir,
               '-c', self.mco, '-i', conll_file, '-m', 'learn']

        ret = self._execute(cmd, verbose)
        if ret != 0:
            raise Exception("MaltParser training (%s) "
                            "failed with exit code %d" %
                            (' '.join(cmd), ret))

        self._trained = True

    @staticmethod
    def _execute(cmd, verbose=False):
        output = None if verbose else subprocess.PIPE
        p = subprocess.Popen(cmd, stdout=output, stderr=output)
        return p.wait()


class RussianMalt:
    def __init__(self, working_dir, mco="russiantrain-2", additional_java_args=None):
        os.environ['MALT_PARSER'] = working_dir
        self._malt_parser = MaltParser(working_dir=working_dir,
                                       mco=mco,
                                       additional_java_args=additional_java_args)
        self._mystem = Mystem(grammar_info=False)
        self._mystem._mystemargs.append('-i')
        self._mystem._mystemargs.append('-s')

    def starts(self):
        self._mystem.start()

    def close(self):
        self._mystem.close()

    def parse_texts(self, raw_texts):
        texts = []
        for text in raw_texts:
            sentence_analyzed = self._mystem.analyze(text)
            sentences = []
            sentence = []
            for i, word_analyzed in enumerate(sentence_analyzed):
                if word_analyzed['text'].strip():
                    if 'analysis' in word_analyzed and len(word_analyzed['analysis']) > 0:
                        gr = regex.split(word_analyzed['analysis'][0]['gr'].upper())
                        h = MorphyFormatConverter.mystem_2_syntagrus_en(gr)
                        pos = sorted(h)[0]
                        feat = set(h[1:]) if len(h) > 1 else []
                        sentence.append((word_analyzed['text'], word_analyzed['text'], pos,
                                         '|'.join((sorted(feat))) if len(''.join(feat)) > 0 else '_'))
                if word_analyzed['text'] == '\\s' or i == len(sentence_analyzed) - 1:
                    sentences.append(sentence)
                    sentence = []
            texts.append(sentences)

        texts = np.array(texts)
        malt_text = []
        for text in texts:
            for sentence in text:
                if len(sentence) > 0:
                    malt_text.append(sentence)
                    #print('|'+' '.join(sentence))

        parsed_texts = []
        parsed_sentences = list(self._malt_parser.tagged_parse_sents(malt_text))

        #print(len(malt_text))
        #print(len(parsed_sentences))
        k = 0
        for i in xrange(len(texts)):
            sentences = []
            for j in xrange(len(texts[i])):
                if len(texts[i][j])>0:
                    sentences.append(list(parsed_sentences[k]))
                    k += 1
            parsed_texts.append(sentences)
        return parsed_texts

    def get_mystem(self):
        return self._mystem

    def parse_text(self, text):
        return self.parse_texts(self, [text])


if __name__ == '__main__':
    print('wow')
