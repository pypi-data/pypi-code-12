# standard distribution imports
import os

# pdbParser imports
from pdbParser.Utilities.Collection import get_path
from pdbParser import pdbParser
from pdbParser.Utilities.Construct import AmorphousSystem
from pdbParser.Utilities.Database import __WATER__

# create pdbWATER
pdbWATER = pdbParser()
pdbWATER.records = __WATER__
pdbWATER.set_name("water")

# get pdb molecules
pdbDMPC = pdbParser(os.path.join(get_path("pdbparser"),"Data","DMPC.pdb" ) )
pdbNAGMA = pdbParser(os.path.join(get_path("pdbparser"),"Data","NAGMA.pdb" ) )
pdbNALMA = pdbParser(os.path.join(get_path("pdbparser"),"Data","NALMA.pdb" ) )

# construct amorphous system, adding restrictions and existing micelle in universe
pdbAMORPH = AmorphousSystem([pdbWATER, pdbDMPC, pdbNAGMA, pdbNALMA],
                             boxSize = [150,150,150], 
                             density = 0.25,
                             restrictions = "np.sqrt(x**2+y**2+z**2)<25" ).construct()
                             
# visualize amorphous system
pdbAMORPH.get_pdb().visualize()
