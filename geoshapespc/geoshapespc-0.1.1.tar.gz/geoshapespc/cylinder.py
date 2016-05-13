# -*- coding: utf-8 -*-
"""
Created on Wed May 11 09:43:19 2016

@author: mathe
"""

# Defining the Cylinder's shape class.
class Cylinder:

    """
    The Cylinder class performs the creation of a cylinder defined by
    the input variables. It contains as embedded functions the calculation
    of the shape's basic parameters, such as base area, perimeter,
    surface area and volume; functions to create a point cloud around
    the shape's lateral surface, both by regularly and pseudorandomly
    placing points; and functions that can be called to obtain just a
    slice in any horizontal transcept of the shape and to rotate the
    shape. Both this later functions can be applied to the regularly and
    pseudorandomly placed point cloud.

    Parameters
    ----------
    xr: scalar
            Radius of the shape over the x-axis.
    yr: scalar
            Radius of the shape over the y-axis.
    length: scalar
            Length of the shape over the z-axis, which can also represent
            the shape's heigth.

    Optional arguments
    ------------------
    xc: scalar
            Shape's center coordinate on the x-axis. Default is 0.
    yc: scalar
            Shape's center coordinate on the y-axis. Default is 0.
    zb: scalar
            Shape's initial (base) coordinate on the z-axis. Default is 0.
    interval: scalar
            Linear distance between the regularly placed points. Default
            is 0.02.
    point_density: scalar
            Amount of points per unit of area in the pseudorandomly
            placed points. Default is 300.
    threshold: scalar
            Linear distance limit from the shape's radii where points
            can be pseudorandomly placed.

    Returns
    -------
    Cylinder: instance
            Cylinder's shape instance with the input and calculated
            parameter and the created point clouds.

    """

    # Setting the instance initial variables and functions
    # to run when the instance is created.
    def __init__(self, xr, yr, length, **kwargs):

        # Appending all variables from kwargs to self.
        self.__dict__ = kwargs
        # Setting default variables' values.
        default = {'xc': 0, 'yc': 0, 'zb': 0, 'interval': 0.02,
                   'point_density': 300, 'threshold': 0.04}
        # Updating the default variables dictionary.
        default.update(kwargs)

        # Setting basic variables, either from default values
        # or from required input arguments.
        self.xc = default['xc']
        self.yc = default['yc']
        self.zb = default['zb']
        self.interval = default['interval']
        self.point_density = default['point_density']
        self.threshold = default['threshold']
        self.length = length
        self.xr = xr
        self.yr = yr

        # Executing functions to calculate basic parameters
        # from the instance's geometric shape.
        self.area_base = self.area_base()
        self.perimeter = self.perimeter()
        self.area_surface = self.area_surface()
        self.volume = self.volume()
        self.xx, self.yy, self.zz = self.point_coordinates()
        self.xrand, self.yrand, self.zrand = self.random_coordinates()

    def area_base(self):

        """
        This function calculates the base area of the instance's
        shape.

        """

        pi = 3.14159265359
        area_ = pi * self.xr * self.yr

        return area_

    def perimeter(self):

        """
        This function calculates the perimeter of the instance's
        shape.

        """

        pi = 3.14159265359

        # Calculating h.
        h = ((self.xr - self.yr) ** 2)/((self.xr + self.yr) ** 2)

        # Calcultating the circumference based of the approximation of
        # Ramanujan.
        perimeter_ = pi * (self.xr + self.yr) * (1 + ((3 * h) /
                                                 (10 + ((4 - 3 * h) **
                                                        (1/2)))))

        return perimeter_

    def area_surface(self):

        """
        This function calculates the surface area of the instance's
        shape.

        """

        area_surface_ = self.perimeter * self.length

        return area_surface_

    def volume(self):

        """
        This function calculates the volume of the instance's
        shape.

        """

        volume_ = self.area_base * self.length

        return volume_

    def point_coordinates(self):

        """
        This function generates a point cloud around the instance's shape,
        regularly spaced, based on the 'interval' value. If the 'interval'
        is not defined, assumes the default value of 0.02.
        This 'interval' is the linear distance between each point on the
        largest transect of the shape.

        Parameters
        ----------
        interval: scalar
                Linear distance between the points in the point
                cloud.

        Returns
        -------
        xx: numpy.ndarray
                Set of x-axis coordinates from  the point cloud.
        yy: numpy.ndarray
                Set of y-axis coordinates from  the point cloud.
        zz: numpy.ndarray
                Set of z-axis coordinates from  the point cloud.

        """

        import numpy as np

        # Calculating the angle interval between the points.
        angle = (2 * np.pi * self.interval) / self.perimeter
        # Creating an array of angular values to place points at.
        R = np.arange(0, 2 * np.pi, angle)

        # Calculating the x and y coordinates of a horizontal transect
        # of the shape.
        x = self.xc + (self.xr * np.cos(R))
        y = self.yc + (self.yr * np.sin(R))

        # Generating a z axis coordinates array with the size of
        # ((length / interval) * len(x)).
        # Filling a base z axis matrix with the same size as xx and yy.
        z1 = np.matrix(np.full([len(x)], 1))
        # Generating the set of z coordinate values to be generated.
        z2 = np.matrix(np.arange(self.zb, self.zb + self.length,
                                 self.interval))
        # Multiplying base z matrix (z1) and the z set of values (z2)
        z3 = z1.T * z2

        # Generating the final z coordinate array by reshaping the z
        # coordinates matrix (z3)
        zz = np.squeeze(np.reshape(np.asarray(z3), [len(x) * np.size(z2)]))
        # Repeating the xx and yy ellipse coordinates along the z axis.
        xx = np.repeat(x, np.size(z2))
        yy = np.repeat(y, np.size(z2))

        return xx, yy, zz

    def random_coordinates(self):

        """
        This function generates a point cloud around the instance's shape,
        pseudorandomly placed, based on the 'point_density' value. If the
        'point_density' is not defined, assumes the default value of 300.
        This 'point_density' is the amount of points per unit of area
        placed around the shape.
        Also, this function uses the parameter 'threshold' which is the
        maximum distance from the defined radius of the shape that the
        points can be placed. This aims to represent some of the signal
        variability found in a real measurement.

        Parameters
        ----------
        point_density: scalar
                Amount of points per unit of area to be placed around the
                shape.
        threshold: scalar
                Maximum distance from the shape's radius (or radii) that
                points can be placed.

        Returns
        -------
        xrand: numpy.ndarray
                Set of x-axis coordinates from  the pseudorandomly place
                point cloud.
        yrand: numpy.ndarray
                Set of y-axis coordinates from  the pseudorandomly place
                point cloud.
        zrand: numpy.ndarray
                Set of z-axis coordinates from  the pseudorandomly place
                point cloud.

        """

        import numpy as np

        # Calculating the total amount of points to place on the surface
        # of the shape.
        n_points = int(self.area_surface * self.point_density)

        # Calculating the minimum and maximum values for the x, y and z
        # axis and for the angle (r_vals).
        xmin = self.xr - self.threshold
        xmax = self.xr + self.threshold
        ymin = self.yr - self.threshold
        ymax = self.yr + self.threshold
        zmin = self.zb - self.threshold
        zmax = self.zb + self.length + self.threshold
        rmin = 0
        rmax = 2 * np.pi

        # Generating n_points random distance values for the x, y and z
        # axis and the angle (r_vals).
        x_vals = xmin + (np.random.sample(n_points) * (xmax - xmin))
        y_vals = ymin + (np.random.sample(n_points) * (ymax - ymin))
        z_vals = zmin + (np.random.sample(n_points) * (zmax - zmin))
        r_vals = rmin + (np.random.sample(n_points) * (rmax - rmin))

        # Multiplying the pseudorandom distances values for the
        # pseudorandom angle values to obtain the set of x, y and z output
        # point coordinates.
        xrand = self.xc + x_vals * np.cos(r_vals)
        yrand = self.yc + y_vals * np.sin(r_vals)
        zrand = self.zb + z_vals

        return xrand, yrand, zrand

    def noise(self, mode, npoints, nrange):

        import numpy as np

        val = {'uniform': (1, 1, npoints), 'linear': (2, 1, npoints),
               'beta1': (3, 1, npoints), 'beta2': (6, 1, npoints)}

        f = getattr(np.random, 'beta')

        # Calculating the minimum and maximum values for the x, y and z
        # axis and for the angle (r_vals).
        xmin = self.xr
        xmax = self.xr + nrange
        ymin = self.yr
        ymax = self.yr + nrange
        zmin = self.zb - nrange
        zmax = self.zb + self.length + nrange
        rmin = 0
        rmax = 2 * np.pi

        # Generating n_points random distance values for the x, y and z
        # axis and the angle (r_vals).
        x_vals = xmin + (f(*val[mode]) * (xmax - xmin))
        y_vals = ymin + (f(*val[mode]) * (ymax - ymin))
        z_vals = zmin + (np.random.sample(npoints) * (zmax - zmin))
        r_vals = rmin + (np.random.sample(npoints) * (rmax - rmin))

        # Multiplying the pseudorandom distances values for the
        # pseudorandom angle values to obtain the set of x, y and z output
        # point coordinates.
        xn = self.xc + x_vals * np.cos(r_vals)
        yn = self.yc + y_vals * np.sin(r_vals)
        zn = self.zb + z_vals

        return xn, yn, zn

    def hslice(self, mode, hmin, hmax):

        """
        This function performs the horizontal slicing of the shape, based
        on the minimum ('hmin') and maximum ('hmax') value for the shape's
        z-axis coordinates.
        The mode variable aims to perform the selection of the point cloud
        to be sliced.

        Parameters
        ----------
        mode: str
                Name of the mode to select the target point cloud.
                'regular' for regularly placed point cloud and 'random'
                for pseudorandomly placed point cloud.
        hmin: scalar
                Minimum z-axis coordinate value of the slice.
        hmax: scalar
                Maximum z-axis coordinate value of the slice.

        Returns
        -------
        xs: numpy.ndarray
                Set of x-axis coordinates for the sliced point cloud.
        ys: numpy.ndarray
                Set of y-axis coordinates for the sliced point cloud.
        zs: numpy.ndarray
                Set of z-axis coordinates for the sliced point cloud.

        """

        # Checking for the 'mode' value to define which point cloud should
        # be sliced.
        if (mode == 'regular'):  # If 'regular' slices the regularly
                                # placed point cloud.
            x = self.xx
            y = self.yy
            z = self.zz
        elif (mode == 'random'):  # If 'random' slices the pseudorandomly
                                # placed point cloud.
            x = self.xr
            y = self.yr
            z = self.zr

        # Generating the slice mask.
        slice_mask = ((z >= hmin) & (z <= hmax))

        # Selecting the points that are True within the mask.
        xs = x[slice_mask]
        ys = y[slice_mask]
        zs = z[slice_mask]

        return xs, ys, zs

    def rotate(self, mode, z_angle, y_angle, x_angle):

        """
        This function performs the rotation of the point cloud based on
        the angular values inputed. This function was based on the code
        from NiBabel (http://nipy.org/nibabel/). Starts the rotation at
        the z axis, followed by the y-axis and the x-axis. This function
        uses the right-hand rule as convention for the rotation angles.

        Parameters
        ----------
        mode: str
                Name of the mode to select the target point cloud.
                'regular' for regularly placed point cloud and 'random'
                for pseudorandomly placed point cloud.
        z_angle: scalar
                Rotation angle, in radians, for the z axis.
        y_angle: scalar
                Rotation angle, in radians, for the y axis.
        x_angle: scalar
                Rotation angle, in radians, for the x axis.

        Returns
        -------
        xr: numpy.ndarray
                Set of x-axis coordinates for the rotated point cloud.
        yr: numpy.ndarray
                Set of y-axis coordinates for the rotated point cloud.
        zr: numpy.ndarray
                Set of z-axis coordinates for the rotated point cloud.

        """

        import numpy as np
        import math

        # Checking for the 'mode' value to define which point cloud should
        # be sliced.
        if (mode == 'regular'):  # If 'regular' slices the regularly placed
            x = self.xx		 # point cloud.
            y = self.yy
            z = self.zz
        elif (mode == 'random'):  # If 'random' slices the pseudorandomly
            x = self.xr		  # placed point cloud.
            y = self.yr
            z = self.zr

        R = []

        # Calculating the sin and cos trigonometric values for each of the
        # input rotation angles.
        cosz = math.cos(z_angle)
        sinz = math.sin(z_angle)
        cosy = math.cos(y_angle)
        siny = math.sin(y_angle)
        cosx = math.cos(x_angle)
        sinx = math.sin(x_angle)

        # Generating the rotation array.
        R.append(np.array(
                [[cosz, -sinz, 0],
                 [sinz, cosz, 0],
                 [0, 0, 1]]))

        R.append(np.array(
                [[cosy, 0, siny],
                 [0, 1, 0],
                 [-siny, 0, cosy]]))

        R.append(np.array(
                [[1, 0, 0],
                 [0, cosx, -sinx],
                 [0, sinx, cosx]]))

        # Reducing the dot product of the rotation matrix.
        R = reduce(np.dot, R[::-1])

        # Concatenating the input point cloud sets of arrays
        # coordinates into a single array.
        M = np.asarray([x, y, z])

        # Calculating the dot product between the point cloud ('M')
        # and the rotation matrix ('R')
        xr, yr, zr = np.dot(R, M)

        return xrot, yrot, zrot
