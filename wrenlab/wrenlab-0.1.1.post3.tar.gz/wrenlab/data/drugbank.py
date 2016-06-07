import collections
import zipfile

import pandas as pd
import lxml.etree

import wrenlab.util
from wrenlab.util import memoize
import wrenlab.ncbi.gene

Drug = collections.namedtuple("Drug", "drugbank_id,name,synonyms,indication,targets")
Target = collections.namedtuple("Target", "gene_id,actions")

@memoize
def parse_drugbank():
    NS = "{http://www.drugbank.ca}"
    genes = wrenlab.ncbi.gene.info(9606)
    symbol_id = dict(zip(genes["Symbol"], list(map(int, genes.index))))

    def tag(key):
        return "{}{}".format(NS, key)

    def find(n, *keys):
        for k in keys:
            if n is None:
                return
            n = n.find(tag(k))
        return n

    def find_text(n, *keys):
        n = find(n, *keys)
        if n is not None:
            return n.text

    def findall(n, *keys):
        # find on all but the last key, findall on last
        keys = list(keys)
        n = find(n, *keys[:-1])
        if n is not None:
            o = n.findall(tag(keys[-1]))
            if o is not None:
                return o
        return []

    def handle_drug(e):
        drugbank_id = set()
        for n in e.findall(tag("drugbank-id")):
            drugbank_id.add(n.text)

        name = e.find(tag("name")).text

        synonyms = set()
        for n in findall(e, "synonym", "synonym"):
            synonyms.add(n.text)

        indication = e.find(tag("indication")).text

        targets = []
        for n in findall(e, "targets", "target"):
            actions = set([a.text.lower() for a in findall(n, "actions", "action")])
            symbol = find_text(n, "polypeptide", "gene-name")
            gene_id = symbol_id.get(symbol)
            if gene_id is not None:
                target = Target(gene_id, actions)
                targets.append(target)

        return Drug(drugbank_id, name, synonyms, indication, targets)

    url = "http://www.drugbank.ca/system/downloads/current/drugbank.xml.zip"
    path = wrenlab.util.download(url)
    o = []
    with zipfile.ZipFile(path) as zf:
        with zf.open("drugbank.xml") as h:
            ctx = lxml.etree.iterparse(h, events=("end",))
            for event, e in ctx:
                if (event == "end") and (e.tag == tag("drug")):
                    drug = handle_drug(e)
                    o.append(drug)
    return o


class DrugBank(object):
    def __init__(self):
        self._items = parse_drugbank()
        self._synonyms = wrenlab.util.CaseInsensitiveDict()
        for drug in self._items:
            self._synonyms[drug.name] = drug
            for s in drug.synonyms:
                self._synonyms[s] = drug

    def by_name(self, name):
        return self._synonyms.get(name)

    @property
    def targets(self):
        SIGN_MAP = {
            "agonist": 1,
            "stimulator": 1,
            "activator": 1,
            "antagonist": -1,
            "inhibitor": -1,
        }
        rows = []
        for drug in self._items:
            for target in drug.targets:
                signs = [SIGN_MAP.get(t) 
                        for a in target.actions
                        for t in a.split()
                        if t in SIGN_MAP]
                sign = signs[0] if len(signs) == 1 else 0
                rows.append((drug.name, target.gene_id, sign))
        return pd.DataFrame.from_records(rows,
                columns=["Drug", "Target", "Direction"])


if __name__ == "__main__":
    import pprint
    db = DrugBank()
    print(db.targets.head())
