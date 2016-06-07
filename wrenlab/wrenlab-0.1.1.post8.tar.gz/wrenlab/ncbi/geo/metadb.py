import functools
import sqlite3
import urllib.request

import pandas as pd

import wrenlab.ncbi.taxonomy
from wrenlab.util import LOG, download

def _get_path():
    urls = [
        "http://gbnci.abcc.ncifcrf.gov/geo/GEOmetadb.sqlite.gz",
        "http://watson.nci.nih.gov/~zhujack/GEOmetadb.sqlite.gz",
        "http://dl.dropbox.com/u/51653511/GEOmetadb.sqlite.gz"
    ]
    for url in urls:
        try:
            return download(url, decompress=True, expire=30)
        except urllib.request.HTTPError:
            LOG.debug("HTTP 404: {}".format(url))
            continue
    raise Exception("Could not retrieve GEOmetadb SQLite database.")

def connect():
    path = str(_get_path())
    return GEOMetaDB(path)

class GEOMetaDB(sqlite3.Connection):
    def __init__(self, path):
        super(GEOMetaDB, self).__init__("file:///{}?mode=ro".format(path), uri=True)

        self._taxonomy = wrenlab.ncbi.taxonomy.names()
        self._taxon_name_id = dict(zip(self._taxonomy["Scientific Name"], 
            self._taxonomy.index))
        
    def __del__(self):
        self.close()

    @property
    @functools.lru_cache()
    def experiment_sample(self):
        q = """
        SELECT
            CAST(SUBSTR(gse,4) AS int) as 'ExperimentID',
            CAST(SUBSTR(gsm,4) AS int) as 'SampleID'
        FROM gse_gsm;
        """
        return pd.read_sql(q, self)

    @property
    @functools.lru_cache()
    def samples(self):
        o = []
        for i in range(1, 3):
            q = """
            SELECT 
                CAST(SUBSTR(gsm,4) AS int) AS 'SampleID', 
                {i} as Channel, 
                CAST(SUBSTR(gpl,4) AS int) AS 'PlatformID',
                organism_ch{i} as 'TaxonID',
                title as Title, 
                characteristics_ch{i} as Characteristics
            FROM gsm
            WHERE channel_count >= {i};
            """.format(i=i)
            o.append(pd.read_sql(q, self))
        o = pd.concat(o)

        ################################
        # TODO: handle multiple channels
        ################################
        o = o.query("Channel == 1").copy()#.drop("Channel", axis=1)
        o = o.set_index(["SampleID", "Channel"])

        o["TaxonID"] = [self._taxon_name_id.get(name) for name in o["TaxonID"]]
        o = o.dropna(subset=["TaxonID"])
        o["TaxonID"] = o["TaxonID"].astype(int)
        return o
