# External libraries
import sarge
import os

from trectools import TrecRun

class TrecTerrier:

    def __init__(self, bin_path):
        self.bin_path = bin_path

    def run(self, index, topics, debug=True, model="PL2", results_dir=None, results_file="trec_terrier.run", terrierc=1, qexp=False, expTerms=5, expDocs=3, expModel="Bo1"):

        if results_dir is None:
            # Current dir is used if results_dir is not set
            results_dir = os.getcwd()

        cmd = "%s -r -c %d -Dtrec.topics=%s -Dtrec.model=%s -Dtrec.results=%s -Dtrec.results.file=%s" % (self.bin_path,
                terrierc, topics, model, results_dir, results_file)

        if qexp == True:
            cmd += " -q -Dexpansion.terms=%d -Dexpansion.documents=%d -Dtrec.qe.model=%s" % (expTerms, expDocs, expModel)

        if debug:
            print "Running: %s " % (cmd)

        sarge.run(cmd).returncode

        return TrecRun(os.path.join(results_dir, results_file))

#tt = TrecTerrier(bin_path="/data/palotti/terrier/terrier-4.0-trec-cds/bin/trec_terrier.sh")
#tr = tt.run(index="/data/palotti/terrier/terrier-4.0-trec-cds/var/index", topics="/data/palotti/trec_cds/metamap/default_summary.xml.gz", qexp=False)


