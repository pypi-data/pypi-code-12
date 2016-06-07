import os
import pandas as pd

import wrenlab.ncbi.gene
from wrenlab.util import memoize

@memoize
def NoaLTP():
    """
    Noa (from Zoltan Ungvari's lab) manually annotated a list of mouse genes as
    "pro" or "anti"-LTP.

    Returns
    -------
    A :class:`pandas.Series` indexed with Entrez Gene IDs and with integer values in {-1,1},
    indicating anti- or pro-LTP genes, respectively.
    """
    path = os.path.join(os.path.dirname(__file__), "NoaLTP.xlsx")
    df = pd.read_excel(path)

    genes = wrenlab.ncbi.gene.info(10090)
    symbol_id = dict(list(map(reversed, genes.loc[:,["Symbol"]].to_records())))

    df = df.loc[:,["Abbrev. ", "PRO vs ANTI LTP"]].dropna(how="any")
    df = df.ix[df.iloc[:,1].isin(["PRO", "ANTI"]),:]
    df = df.ix[df.iloc[:,0].isin(symbol_id.keys()),:]

    return pd.Series(dict([(symbol_id[k],int(v == "PRO")) for k,v in df.to_records(index=False)]))

