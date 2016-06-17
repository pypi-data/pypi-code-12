from .cubical_complex import *
from .simplicial_complex import *
from .prod_simplicial_complex import *
from .generalized_complex import *
from .algorithms import *
from .read import read
from .version import __version__
import persistence

def config():
    from .impl import capd_impl
    impl = capd_impl.GetConfig()
    capd_impl.Logger.init()
    return impl

def dev_default_config():
    conf = config()
    conf.setDefaultSimplicialType(21) # 20 - old, 21 - new
    conf.setDefaultGeneralizedType(7) # 6 - old, 7 - new
    conf.setDefaultComputationModel(2) # 0-auto, 1-std, 2-tbb
    conf.setDefaultDiscreteVectorFieldMethod(2) # 100-legacy, 1-coreduce, 2-reduce, 3-inParallelCoreduce, 4-inParallelReduce
    conf.setBettiNumbersFlags("1111")
