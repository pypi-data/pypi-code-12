import os

from pdbParser.Utilities.Collection import get_path
from pdbParser import pdbParser
from pdbParser.Utilities.Construct import Micelle

# load molecules pdbs from pdbParser database
pdbSDS = pdbParser(os.path.join(get_path("pdbparser"),"Data/SDS.pdb" ) )  
pdbCTAB = pdbParser(os.path.join(get_path("pdbparser"),"Data/CTAB.pdb" ) ) 

# constuct hybrid micelle 
pdbMICELLE = Micelle([pdbCTAB,pdbSDS],
                     flipPdbs = [True,True],
                     positionsGeneration = "symmetric").construct().solvate(density = 0.25, restrictions = "np.sqrt(x**2+y**2+z**2)<25")

# solvate micelle with density = 0.5
#pdbMICELLE.solvate(density = 0.5)

# visualize solvate micelle
pdbMICELLE.get_pdb().visualize()
