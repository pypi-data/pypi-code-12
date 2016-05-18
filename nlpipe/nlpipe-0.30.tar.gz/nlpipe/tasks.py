from subprocess import Popen, PIPE

from .module import NLPSystemModule, NLPipeModule
from .celery import app
from .modules import frog as _frog, corenlp, amcatmeta as _amcatmeta

@app.task(base=NLPSystemModule, cmd="$NEWSREADER_HOME/run_parser.sh parse")
def morphosyntactic(text):
    """
    Run the newsreader morphosyntactic parser.

    Requires NEWSREADER_HOME to be defined and point at the
    root newsreader folder, containing a run_parser script
    """
    pass

@app.task(base=NLPSystemModule, cmd="$NEWSREADER_HOME/run_parser.sh annotate", input_doc_type="morphosyntactic__0_0")
def annotate(text):
    """
    Run the newsreader opinion mining.

    Requires NEWSREADER_HOME to be defined and point at the
    root newsreader folder, containing a run_parser script
    """
    pass

@app.task(base=NLPipeModule, input_doc_type="annotate__0_0", bind=True)
def amcatmeta(self, doc):
    return _amcatmeta.add_amcatmeta(doc, self.id)

@app.task(base=NLPipeModule)
def frog(text):
    """
    Call the frog lemmatizer/tagger

    Requires a frog server to be listening at port FROG_PORT (default: 9887)
    """
    return _frog.frog_naf(text)
    

@app.task(base=NLPipeModule)
def corenlp_parse(text):
    """
    Call the Stanford CoreNLP parser

    Requires CORENLP_HOME to point to the stanford corenlp folder
    """
    return corenlp.corenlp_naf(text, annotators=corenlp.PARSER)

@app.task(base=NLPipeModule)
def corenlp_lemmatize(text):
    """
    Call the Stanford CoreNLP lemmatizer (and NER)

    Requires CORENLP_HOME to point to the stanford corenlp folder
    """
    return corenlp.corenlp_naf(text, annotators=corenlp.LEMMATIZER)
