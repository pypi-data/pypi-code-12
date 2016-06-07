import functools
import tarfile
from collections import namedtuple

import pandas as pd

from wrenlab.util import memoize, download

Taxon = namedtuple("Taxon", "id,name")

@memoize
def names():
    scientific = {}
    common = {}
    url = "ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"
    path = str(download(url))
    tar = tarfile.open(path, "r:gz")
    handle = tar.extractfile("names.dmp")
    for i,line in enumerate(handle):
        fields = [c.strip("\t") for c in
                line.decode("utf-8")\
                        .rstrip("\n").split("|")][:-1]
        taxon_id = int(fields[0])
        name = fields[1]
        unique_name = fields[2]
        name_class = fields[3]
        if name_class == "scientific name":
            scientific[taxon_id] = name
        elif "common name" in name_class:
            common[taxon_id] = name

    records = [(taxon_id, scientific[taxon_id], common.get(taxon_id)) 
            for taxon_id in scientific]
    return pd.DataFrame(records, columns=["Taxon ID", "Scientific Name", "Common Name"])\
            .set_index(["Taxon ID"])

def by_id(taxon_id):
    assert isinstance(taxon_id, int)

    df = names()
    name = df.loc[taxon_id, "Scientific Name"]
    return Taxon(taxon_id, name)
