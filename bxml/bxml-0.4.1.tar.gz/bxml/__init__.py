
import os
from bl.dict import Dict
from .xml import XML

NS = Dict(**{
    "bl": "http:blackearth.us/xml",
})

JARS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jars')
