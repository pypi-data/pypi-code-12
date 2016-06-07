import glob
import os
import shutil
import sqlite3

import wrenlab.util.aspera

from wrenlab.util import LOG

SRAMETADB = [
    "http://gbnci.abcc.ncifcrf.gov/backup/SRAmetadb.sqlite.gz",
    "http://watson.nci.nih.gov/~zhujack/SRAmetadb.sqlite.gz",
    "http://dl.dropbox.com/u/51653511/SRAmetadb.sqlite.gz"
]

REFERENCE = {
    "GRCh38.p7": "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCF_000001405.33_GRCh38.p7/GCF_000001405.33_GRCh38.p7_genomic.fna.gz"
}


def reference(key):
    pass

class ReferenceGenome(object):
    def __init__(self, path):
        pass

class Aligner(object):
    def align(self, ):
        raise NotImplementedError

class Bowtie2Aligner(Aligner):
    pass


class SeqDB(object):
    def __init__(self, root):
        self._root = root
        os.makedirs(root, exist_ok=True)

        self._metadb_connect()

    def _metadb_connect(self):
        path = str(wrenlab.util.download(SRAMETADB[0], decompress=True))
        self._cx = sqlite3.connect(path)

    def __del__(self):
        self._cx.close()

    def sync(self):
        c = self._cx.cursor()
        c.execute("""
        SELECT DISTINCT(sample_accession)
            FROM sra
            WHERE 
                taxon_id=9606
                AND library_source="TRANSCRIPTOMIC"
                AND library_strategy="RNA-Seq"
                AND library_selection="RANDOM"--polyA
            ;""")

        o = os.path.join(self._root, "reads")
        os.makedirs(o, exist_ok=True)

        base = "/sra/sra-instant/reads/BySample/sra/"
        client = wrenlab.util.aspera.Client(host="ftp-trace.ncbi.nlm.nih.gov")

        for row in c:
            id = row[0]
            src = "/".join([base, id[:3], id[:6], id])
            target = os.path.join(o, id)
            try:
                client.download(src, target)
                LOG.info("Download success: SRA sample {}".format(id))
            except:
                LOG.error("Download failed: SRA sample {}".format(id))

            for file in glob.glob(os.path.join(target, "*", "*.sra")):
                shutil.move(file, target)
                shutil.rmtree(os.path.dirname(file))

    def align(self, index_name, index):
        reads_dir = os.path.join(self._root, "reads")
        for sample_id in os.listdir(reads_dir):
            sample_dir = os.path.join(reads_dir, sample_id)
