import seaborn
from .plots import *
from .graphs import *
from .maps import *

def __init__():
    seaborn.set_style("whitegrid")
    d = os.path.dirname(sys.modules['ipyplots'].__file__)

    d3_content = open(os.path.join(d, 'd3.v3.min.js'), 'r').read()

    d3 = Javascript(data=d3_content)
    display_javascript(d3)
