import os

from pdbParser.Utilities.Collection import get_path
from pdbParser import pdbParser
from pdbParser.Utilities.Construct import Liposome
from pdbParser.Utilities.Modify import reset_sequence_identifier_per_model

# read SDS molecule from pdbParser database
pdbSDS = pdbParser(os.path.join(get_path("pdbparser"),"Data/SDS.pdb" ) ) 

# create liposome
pdbLIPOSOME= Liposome(pdbSDS,
                      innerInsertionNumber = 1000,
                      positionsGeneration = "symmetric").construct()

# visualize liposome
pdbLIPOSOME.get_pdb().visualize()
