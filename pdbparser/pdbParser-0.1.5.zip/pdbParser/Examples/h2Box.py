import numpy as np
from pdbParser.log import Logger
from pdbParser import pdbParser
from pdbParser.Utilities.Construct import AmorphousSystem
from pdbParser.Utilities.Database import __WATER__

# create pdbWATER
pdbWATER = pdbParser()
pdbWATER.records = __WATER__
pdbWATER.set_name("water")
Logger.info("Create water box")
pdbWATER = AmorphousSystem(pdbWATER, density = 0.25, boxSize=np.array([10,10,10])).construct().get_pdb()
pdbWATER.visualize()

