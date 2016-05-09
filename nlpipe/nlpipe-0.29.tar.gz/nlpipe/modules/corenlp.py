"""
Wrapper around the CoreNLP parser
The module expects CORENLP_HOME to point to the CoreNLP installation dir.
If run with all annotators, it requires around 3G of memory,
and it will keep the process in memory indefinitely.
See: http://nlp.stanford.edu/software/corenlp.shtml#Download
Tested with
http://nlp.stanford.edu/software/stanford-corenlp-full-2014-01-04.zip
"""

import datetime
import io
import itertools
import logging
import os
import re
import subprocess
import threading
import time
import collections
from io import BytesIO

from corenlp_xml.document import Document
from unidecode import unidecode
from KafNafParserPy import KafNafParser

log = logging.getLogger(__name__)

LEMMATIZER = ['tokenize', 'ssplit', 'pos', 'lemma','ner']
PARSER = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'dcoref']

def _get_corenlp_version():
    "Return the corenlp version pointed at by CORENLP_HOME, or None"
    corenlp_home = os.environ.get("CORENLP_HOME")
    if corenlp_home:
        for fn in os.listdir(corenlp_home):
            m = re.match("stanford-corenlp-([\d.]+)-models.jar", fn)
            if m:
                return m.group(1)


_CORENLP_VERSION = None
def get_corenlp_version():
    global _CORENLP_VERSION
    if _CORENLP_VERSION is None:
        _CORENLP_VERSION = _get_corenlp_version()
    return _CORENLP_VERSION


class StanfordCoreNLP(object):

    _singletons = {}  # annotators : object

    @classmethod
    def get_singleton(cls, annotators=None, **options):
        """
        Get or create a corenlp parser with the given annotator and options
        Note: multiple parsers with the same annotator and different options
              are not supported.
        """
        if annotators is not None:
            annotators = tuple(annotators)
        if annotators not in cls._singletons:
            cls._singletons[annotators] = cls(annotators, **options)
        return cls._singletons[annotators]

    def __init__(self, annotators=None, timeout=1000, memory="3G"):
        """
        Start the CoreNLP server with a system call.
        @param annotators: Which annotators to use, e.g.
                           ["tokenize", "ssplit", "pos", "lemma"]
        @param memory: Java heap memory to use
        """
        self.annotators = annotators
        self.memory = memory
        self.start_corenlp()

    def start_corenlp(self):
        cmd = get_command(memory=self.memory, annotators=self.annotators)
        log.warn("Starting corenlp: {cmd}".format(**locals()))
        self.corenlp_process = subprocess.Popen(cmd, shell=True,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
        self.lock = threading.Lock()
        self.read_thread = threading.Thread(target=self.read_output_lines)
        self.read_thread.daemon = True
        self.read_thread.start()
        log.warn("Waiting for prompt")
        self.communicate(input=None, wait_for_output=False)

    def read_output_lines(self):
        "intended to be run as background thread to collect parser output"
        while True:
            chars = self.corenlp_process.stdout.readline()
            if chars == '':  # EOF
                break
            self.out.write(chars)

    def communicate(self, input, wait_for_output=True):
        log.warn("Sending {} bytes to corenlp".format(input and len(input)))
        if self.corenlp_process.poll() is not None:
            logging.warn("CoreNLP process died, respawning")
            self.start_corenlp()
        with self.lock:
            self.out = io.BytesIO()
            if input:
                self.corenlp_process.stdin.write(input)
                self.corenlp_process.stdin.write("\n\n")
                self.corenlp_process.stdin.flush()

            # wait until we get a prompt
            logging.warn("Waiting for NLP>")
            err_buffer = io.BytesIO()
            while True:
                char = self.corenlp_process.stderr.read(1)
                err_buffer.write(char)
                err_buffer.seek(-5, 2)
                if err_buffer.read() == "NLP> ":
                    break

        # give stdout a chance to flush
        # is there a better way to do this?
        while True:
            time.sleep(.1)
            result = self.out.getvalue()
            if ((result and result.strip().endswith("</root>"))
                or not wait_for_output):
                return result

    def parse(self, text):
        """Call the server and return the raw results."""
        if isinstance(text, bytes):
            text = text.decode("ascii")
        text = re.sub("\s+", " ", unidecode(text))
        return self.communicate(text + "\n")


def parse(text, annotators=None, **options):
    if not text.strip():
        return None
    s = StanfordCoreNLP.get_singleton(annotators, **options)
    return s.parse(text)




def get_command(annotators=None, memory=None):
    "Return the system (shell) call to run corenlp"
    corenlp_home = os.environ.get("CORENLP_HOME")
    if not corenlp_home:
        raise Exception("CORENLP_HOME not set")
    cmd = 'java'
    if memory:
        cmd += ' -Xmx{memory}'.format(**locals())
    cmd += ' -cp "{}"'.format(os.path.join(corenlp_home, "*"))
    cmd += " edu.stanford.nlp.pipeline.StanfordCoreNLP -outputFormat xml"
    if annotators:
        cmd += ' -annotators {}'.format(",".join(annotators))
    return cmd


def corenlp2naf(xml_bytes, annotators):
    """
    Call from on the text and return a Naf object
    """
    naf = KafNafParser(type="NAF")

    try:
        doc = Document(xml_bytes)
    except:
        log.exception("Error on parsing xml")
        raise

    terms = {} # (xml_sentid, xml_tokenid) : term
    for sent in doc.sentences:
        for t in sent.tokens:
            wf = naf.create_wf(t.word, sent.id, t.character_offset_begin)
            term = naf.create_term(t.lemma, POSMAP[t.pos], t.pos, [wf])
            terms[sent.id, t.id] = term
            if t.ner not in (None, 'O'):
                naf.create_entity(t.ner, [term.get_id()])
        if sent.collapsed_ccprocessed_dependencies:
            dependencies = True
            for dep in sent.collapsed_ccprocessed_dependencies.links:
                if dep.type != 'root':
                    child = terms[sent.id, dep.dependent.idx]
                    parent = terms[sent.id, dep.governor.idx]
                    comment = "{t}({o}, {s})".format(s=child.get_lemma(), t=dep.type, o=parent.get_lemma())
                    naf.create_dependency(child.get_id(), parent.get_id(), dep.type, comment=comment)

    if doc.coreferences:
        for coref in doc.coreferences:
            cterms = set()
            for m in coref.mentions:
                cterms |= {terms[m.sentence.id, t.id].get_id() for t in m.tokens}
            naf.create_coreference("term", cterms)
        
    for annotator in annotators:
        if annotator in LAYERMAP:
            naf.create_linguistic_processor(LAYERMAP[annotator], "CoreNLP {annotator}".format(**locals()),
                                            get_corenlp_version())
    s = BytesIO()
    naf.dump(s)
    return s.getvalue()

def corenlp_naf(text, annotators=PARSER, **options):
    xml = parse(text, annotators, **options)
    return corenlp2naf(xml, annotators=annotators)

LAYERMAP = {'tokenize': 'text',
            'lemma': 'term',
            'ner': 'entities',
            'parse': 'deps',
            'dcoref': 'coreferences'}
            
POSMAP = {
    # P preposition
    'IN': 'P',
    # G adjective
    'JJ': 'G',
    'JJR': 'G',
    'JJS': 'G',
    'WRB': 'G',
    # C conjunction
    'LS': 'C',
    # V verb
    'MD': 'V',
    'VB': 'V',
    'VBD': 'V',
    'VBG': 'V',
    'VBN': 'V',
    'VBP': 'V',
    'VBZ': 'V',
    # N noun
    'NN': 'N',
    'NNS': 'N',
    'FW': 'N',
    # R proper noun 
    'NNP': 'R',
    'NNPS': 'R',
    # D determiner
    'PDT': 'D',
    'DT': 'D',
    'WDT': 'D',
    # A adverb
    'RB': 'A',
    'RBR': 'A',
    'RBS': 'A',
    # O other
    'CC': 'O',
    'CD': 'O',
    'POS': 'O',
    'PRP': 'O',
    'PRP$': 'O',
    'EX': 'O',
    'RP': 'O',
    'SYM': 'O',
    'TO': 'O',
    'UH': 'O',
    'WP': 'O',
    'WP$': 'O',
    ',': 'O',
    '.': 'O',
    ':': 'O',
    '``': 'O',
    '$': 'O',
    "''": 'O',
    "#": 'O',
    '-LRB-': 'O',
    '-RRB-': 'O',
}
