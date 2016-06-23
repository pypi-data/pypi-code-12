from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import numpy as np
import os
import unittest

import properties
import steno3d


class TestResourceSurface(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_surface(self):
        P = steno3d.Project()
        myVerts = np.array([[0., 0, 0], [0, 1, 0], [1, 0, 0]])
        myTriangles = np.array([[0, 1, 2]])

        S = steno3d.Surface(
            project=P,
            mesh=dict(
                vertices=myVerts,
                triangles=myTriangles,
                opts={"wireframe": True}
            ),
            opts={"opacity": 0.3, "color": "red"},
        )
        S.validate()

        # Make sure getattr/setattr working ok
        assert S.mesh is S.mesh
        assert S.mesh.vertices is S.mesh.vertices
        assert S.mesh.triangles is S.mesh.triangles

        # Make sure the shortcuts are working

        # assert S.vertices is S.mesh.vertices
        # assert S.triangles is S.mesh.triangles
        # assert S.vertices is not myVerts
        # assert S.triangles is not myTriangles
        assert np.array_equal(S.mesh.vertices, myVerts)
        assert np.array_equal(S.mesh.triangles, myTriangles)

        # Test options
        # ----Surface
        # --------Color
        assert S.opts.color == (255, 0, 0)
        S.opts.color = 'darkred'

        assert S.opts.opacity == 0.3
        S.opts.opacity = .1
        assert S.opts.opacity == .1
        S.opts = {"opacity": 0.5}
        assert S.opts.opacity == .5
        S.opts = {"color": '#FFF'}
        assert S.opts.opacity == 1

        assert S.mesh.opts.wireframe
        self.assertRaises(ValueError,
                          lambda: setattr(S.mesh.opts, 'wireframe', 'Wires'))
        self.assertRaises(ValueError,
                          lambda: setattr(S.mesh.opts, 'wireframe', 1))
        S.mesh.opts = {"wireframe": False}
        assert not S.mesh.opts.wireframe
        S.mesh.opts.wireframe = True
        assert S.mesh.opts.wireframe

        # Test triangles
        S.triangles = [[0, 0, 0], [1, 1, 1]]
        assert isinstance(S.mesh.triangles, np.ndarray)
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'triangles', -1))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'triangles', [[0, 0]]))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'triangles', [[0, 0, .5], [1, 1, 1]]))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'triangles', [[0], [0], [0]]))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'triangles', 'Three isosceles, please!'))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'triangles', [[0, 0, 1, 1], [0, 0, 0, 0]]))

        S.mesh.triangles = [[0, 0, -100], [1, 1, 1]]
        self.assertRaises(ValueError, lambda: S.validate())

        S.mesh._p_triangles = -1   # try to fake things out.
        # ensure we also call the validator
        self.assertRaises(ValueError, lambda: S.validate())

        myNewTriangles = np.array([
            [0, 1, 2], [1, 2, 3],
            [0, 1, 4], [0, 2, 4],
            [1, 3, 4], [2, 3, 4]
        ])
        S.mesh.triangles = myNewTriangles
        self.assertRaises(ValueError, lambda: S.validate())
        assert np.array_equal(S.mesh.triangles, myNewTriangles)

        # Test vertices
        myNewVerts = np.array([
            [0, 0, 0],
            [0, 0, -1],
            [0, 1, 0],
            [0, 1, 1],
            [1, .5, .5]
        ])
        S.mesh.vertices = myNewVerts
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'vertices', -1))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'vertices', [[0, 0]]))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'vertices', [[0], [0], [0]]))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'vertices', 'Just a few random points.'))
        self.assertRaises(
            ValueError,
            lambda: setattr(S.mesh, 'vertices', [[0, 0, 1, 1], [0, 0, 0, 0]]))

        # Other Constructor tests
        S = steno3d.Surface(P)
        self.assertRaises(properties.exceptions.RequiredPropertyError,
                          lambda: S.validate())
        S.mesh = S.mesh
        self.assertRaises(properties.exceptions.RequiredPropertyError,
                          lambda: S.validate())
        S.mesh.vertices = myVerts
        S.mesh.triangles = myTriangles
        S.validate()
        MOpts = dict(wireframe=True)
        M = steno3d.Mesh2D(
            vertices=myNewVerts,
            triangles=myNewTriangles,
            opts=MOpts
        )
        SOpts = dict(opacity=.5, color=[100, 100, 100])
        S = steno3d.Surface(P, mesh=M, opts=SOpts)

        assert S.mesh.vertices is not myNewVerts
        assert S.mesh.triangles is not myNewTriangles
        assert np.array_equal(S.mesh.vertices, myNewVerts)
        assert np.array_equal(S.mesh.triangles, myNewTriangles)
        assert S.opts.opacity == .5
        assert S.opts.color == (100, 100, 100)
        assert S.mesh.opts.wireframe

        # Test Data
        # This needs to be updated once data is updated
        S.mesh.triangles = myTriangles
        S.mesh.vertices = myVerts
        S.data = [{'data': [0], 'location': 'face'}]
        assert type(S.data) is list
        d0 = S.data[0]
        # copying the list and appending to it (not the same list!)
        S.data.append({'data': [2], 'location': 'vertex'})
        assert len(S.data) == 1
        # iadd is resetting the list and doing validation
        S.data += [{'data': [2], 'location': 'vertex'}]
        assert S.data[0] is d0
        from steno3d.surface import _SurfaceBinder
        assert isinstance(S.data[1], _SurfaceBinder)
        # surface.data[1] is the incorrect length
        self.assertRaises(Exception, lambda: S.validate())
        S.data[1].data = [0, 1, 2]
        assert S.data[1].data.title == ''
        assert S.data[1].data.description == ''
        assert np.all(S.data[1].data.array == [0, 1, 2])
        S.validate()

    def test_surface_mesh2dgrid(self):
        myh1 = [5., 4., 3., 2., 1., 1., 1., 1., 2., 3., 4., 5.]
        myh2 = [1., 1., 1., 1., 2., 3., 4., 5.]

        # This should error
        def f():
            P = steno3d.Project()
            S = steno3d.Surface(
                P,
                mesh=dict(
                    h1=myh1,
                    h2=myh2,
                    opts={"wireframe": True}
                ),
                opts={"opacity": 0.3, "color": "red"},
            )

        self.assertRaises(KeyError, f)

        # This should be ok
        P = steno3d.Project()
        M = steno3d.Mesh2DGrid(h1=myh1, h2=myh2, opts={"wireframe": True})
        S = steno3d.Surface(P, mesh=M, opts={"opacity": 0.3, "color": "red"})

        S.validate()

        myZ = np.random.rand(10)
        S.mesh.Z = myZ
        self.assertRaises(ValueError, lambda: S.validate())

        myZ = np.random.rand((len(myh1)+1) * (len(myh2)+1))
        S.mesh.Z = myZ
        S.validate()

        S.mesh.x0 = [[0, 0, 0], [1, 1, 1]]
        self.assertRaises(ValueError, lambda: S.validate())

    def test_teapot(self):
        basedir = os.path.realpath(os.path.dirname(steno3d.__file__))
        teapot = os.path.realpath(basedir + '/../assets/basic/teapot.json')
        with open(teapot) as f:
            data = json.loads(f.read())
        P = steno3d.Project()
        S = steno3d.Surface(
            project=P,
            mesh=dict(
                vertices=data['vertices'],
                triangles=data['triangles'],
                opts={"wireframe": True}
            ),
            opts={"opacity": 0.3, "color": "red"},
        )
        S.validate()

    def test_proj_resource_link(self):
        p0 = steno3d.Project()
        p1 = steno3d.Project()
        p2 = steno3d.Project()
        s0 = steno3d.Surface(p0)
        assert len(s0.project) == 1
        assert len(p0.resources) == 1
        s0.project = [p0, p0, p2, p1, p2]
        assert len(s0.project) == 3
        assert s0.project[0] is p0
        assert s0.project[1] is p2
        assert s0.project[2] is p1
        assert len(p0.resources) == 1
        assert len(p1.resources) == 1
        assert len(p2.resources) == 1
        s1 = steno3d.Surface(p1)
        assert len(s1.project) == 1
        assert len(p1.resources) == 2
        s2 = steno3d.Surface(p1)
        assert len(p1.resources) == 3
        s2.project += [p1]
        assert len(p1.resources) == 3
        assert len(s2.project) == 1
        p2.resources += [s0, s1, s1, s1]
        assert len(p2.resources) == 2
        assert p2.resources[0] is s0
        assert p2.resources[1] is s1
        assert len(s0.project) == 3
        assert len(s1.project) == 2


if __name__ == '__main__':
    unittest.main()
