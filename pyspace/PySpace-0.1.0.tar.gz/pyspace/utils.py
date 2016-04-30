#!usr/bin/env python
from pyspace.planet import PlanetArray
from pyevtk.hl import pointsToVTK

def dump_vtk(pa, filename, base = ".", **data):
    """Dumps vtk output to file 'base/filename'"""
    if not data:
        data = {'v_x': pa.v_x, 'v_y': pa.v_y, 'v_z': pa.v_z}
    pointsToVTK(base + "/" + filename, pa.x, pa.y, pa.z, data = data)

def get_planet_array(*args, **kwargs):
    """Returns a PlanetArray"""
    pa = PlanetArray(*args, **kwargs)
    return pa

