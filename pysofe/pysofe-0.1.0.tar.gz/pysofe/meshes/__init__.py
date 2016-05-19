"""
Provides the data structures for the finite element meshes.

The main purpose of the mesh in the finite element environment 
is to discretize the spatial domain of the considered partial 
differential equation. Furthermore, it gives access to its 
topological entities such as vertices, edges, faces and cells
and provides methods for refinement.

The mesh data structure in |PySOFE| is represented by the |Mesh| class
and encapsulates the classes |MeshGeometry| and |MeshTopology|.  It
also has an instance of the |ReferenceMap| class as an attribute to
connect the physical mesh entities with the reference domain.
"""

import mesh
import geometry
import topology
import reference_map
import refinements

from .mesh import Mesh, UnitSquareMesh
