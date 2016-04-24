"""
Wrapper to call the frog server and parse the results as NAF

Assumes that a frog server is listening on FROG_HOST, defaulting to localhost:9887

With 'la machine', this can be done with the following command:
sudo docker run -dp 9887:9887 proycon/lamachine frog -S 9887 --skip=pm

Note that on some machines you need to add --net=host to get port forwarding to work,
possibly related to https://github.com/docker/docker/issues/13914

See: http://languagemachines.github.io/frog/
"""
import os
from io import BytesIO

from pynlpl.clients.frogclient import FrogClient
from KafNafParserPy import *
from collections import namedtuple

Token = namedtuple("Token", ["sent", "offset", "word", "lemma", "pos", "morphofeat", "ner", "chunk"])

_POSMAP = {"VZ" : "P",
          "N" : "N",
          "ADJ" : "G",
          "LET" : "O",
          "VNW" : "O",
          "LID" : "D",
          "SPEC" : "R",
          "TW" : "O",
          "WW" : "V",
          "BW" : "A",
          "VG" : "C",
          "TSW" : "O",
          "MWU" : "O",
          "" : "O"}

_FROG_VERSION = os.environ.get("FROG_VERSION")
def get_frog_version():
    global _FROG_VERSION
    if _FROG_VERSION is None:
        try:
            _FROG_VERSION = subprocess.check_output("frog -V 2>&1", shell=True).split()[1]
        except:
            _FROG_VERSION = "0.0"
    return _FROG_VERSION

def call_frog(text):
    """
    Call frog on the text and return (sent, offset, word, lemma, pos, morphofeat) tuples
    """
    
    host, port = os.environ.get('FROG_HOST', 'localhost:9887').split(":")
    frogclient = FrogClient(host, port, returnall=True)
    sent = 1
    offset = 0
    for word, lemma, morph, morphofeat, ner, chunk, _p1, _p2 in frogclient.process(text):
        if word is None:
            sent += 1
        else:
            pos = _POSMAP[morphofeat.split("(")[0]]
            yield Token(sent, offset, word, lemma, pos, morphofeat, ner, chunk)
            offset += len(word)

def frog_naf(text):
    """
    Call from on the text and return a Naf object
    """
    naf = KafNafParser(type="NAF")
    frogclient = FrogClient('localhost', 9887)
    for token in call_frog(text):
        wf = naf.create_wf(token.word, token.sent, token.offset)
        term = naf.create_term(token.lemma, token.pos, token.morphofeat, [wf])

    naf.create_linguistic_processor("text", "Frog tokenizer", get_frog_version())
    naf.create_linguistic_processor("term", "Frog MBT", get_frog_version())
    s = BytesIO()
    naf.dump(s)
    return s.getvalue()
