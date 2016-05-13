"""
In this test two water amorphous box are constructed
one with a hollow sphere inside, the other only a shere of water is kept
"""
# standard distribution imports
import os

# pdbParser imports
from pdbParser.Utilities.Collection import get_path
from pdbParser import pdbParser
from pdbParser.log import Logger
from pdbParser.Utilities.Construct import AmorphousSystem, Micelle
from pdbParser.Utilities.Geometry import get_satisfactory_records_indexes, translate
from pdbParser.Utilities.Modify import delete_records_and_models_records

from pdbParser.Utilities.Database import __WATER__

# create pdbWATER
pdbWATER = pdbParser()
pdbWATER.records = __WATER__
pdbWATER.set_name("water")

Logger.info("Create water box")
pdbWATER = AmorphousSystem(pdbWATER, density = 0.5).construct().get_pdb()
pdbWATERhollow = pdbWATER.get_copy()

# make sphere
Logger.info("Create a water sphere of 15A radius")
sphereIndexes = get_satisfactory_records_indexes(pdbWATER.indexes, pdbWATER, "np.sqrt(x**2 + y**2 + z**2) >= 15")
delete_records_and_models_records(sphereIndexes, pdbWATER)

# make hollow
Logger.info("Remove a water sphere of 15A radius")
hollowIndexes = get_satisfactory_records_indexes(pdbWATERhollow.indexes, pdbWATERhollow, "np.sqrt(x**2 + y**2 + z**2) <= 15")
delete_records_and_models_records(hollowIndexes, pdbWATERhollow)

# translate hollow
translate(pdbWATERhollow.indexes, pdbWATERhollow, vector =[60,0,0])

# concatenate
pdbWATER.concatenate(pdbWATERhollow)

pdbWATER.visualize()
