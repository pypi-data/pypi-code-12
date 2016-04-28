"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations


###############################################################################
#
# MPI HH TUTORIAL PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# Cell properties list
netParams['cellParams'] = []

## PYR cell properties
cellRule = {'label': 'PYR', 'conditions': {'cellType': 'PYR'},  'sections': {}}   # cell rule dict
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}, 'Izhi2007Type': 'RS'}  # soma properties
soma['geom'] = {'diam': 6.3, 'L': 5, 'Ra': 123.0, 'pt3d': []}
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
cellRule['sections'] = {'soma': soma}   
netParams['cellParams'].append(cellRule)    

# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 10}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 10, 'noise': 0.5, 'source': 'random'})  # background inputs

# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'NMDA', 'mod': 'ExpSyn', 'tau': 0.1, 'e': 0})

# Connectivity parameters
netParams['connParams'] = []  
netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'weight': 0.0001,                    # weight of each connection
    'delay': '0.2+gauss(13.0, 1.4)',    # delay function (min=0.2, mean=13, var=1.4)
    'threshold': 10,                    # threshold
    'convergence': 'uniform(0, 10)'})   # convergence function (num of presyn conns per postsyn)      


netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR'}, # background -> PYR
    'connFunc': 'fullConn',
    'weight': 0.5, 
    'synMech': 'NMDA',
    'delay': 5})  

###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 5*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = False  # show detailed messages 
simConfig['timing'] = True  # plot timing
simConfig['saveTiming'] = True  # save timing to file


# Recording 
simConfig['recordTraces'] = {'NMDA_i': {'sec':'soma', 'loc':0.5, 'synMech':'NMDA', 'var':'i'}} #'V':{'sec':'soma', 'pos':0.5, 'var':'v'}} 
simConfig['recordStim'] = False  # record spikes of cell stims
simConfig['recordStep'] = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = '../IzhiNet'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = 0 # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = 1 # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = 0 # Whether or not to write spikes etc. to a .mat file
simConfig['saveHDF5'] = 0 # save spikes and conn to txt file
simConfig['saveDpk'] = 0 # save to a .dpk pickled file
simConfig['saveCSV'] = 0 # save to a .dpk pickled file

# Analysis and plotting 
simConfig['plotRaster'] = 0 # Whether or not to plot a raster
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['orderRasterYnorm'] = False # Order cells in raster by yfrac (default is by pop and cell id)
simConfig['plotCells'] = [0] # plot recorded traces for this list of cells
simConfig['plotLFPSpectrum'] = False # plot power spectral density (not yet implemented)

from netpyne import init
init.createAndSimulate(netParams = netParams, simConfig = simConfig)  # create and simulate network
