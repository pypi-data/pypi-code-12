from .Datapub import Datapub

def printUsage():
    print("""Usage:

import datapub

Datapub = datapub.Datapub()

ds = Datapub.get_ds(\'c9fa7898a7\')

ds = Datapub.get_paper_ds(\'pmid26111164\', 0)

print(Datapub.paper_datasets(\'4339fcd7ac\'))
""")
