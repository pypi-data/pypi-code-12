# -*- coding: utf-8 -*-
"""
@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""
from __future__ import division


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
    noise_mode: str
            Option to select the type of point distribution to use in
            the noise point cloud.
    noise_ratio: scalar
            Noise to signal ratio to simulate.
    noise_range: scalar
            Maximum distance from the shape's surface to place the noise
            points in.

    Returns
    -------
    Cylinder: instance
            Cylinder's shape instance with the input and calculated
            parameter and the created point clouds.

    """

    # Setting the instance initial variables and functions
    # to run when the instance is created.
    def __init__(self, xr, yr, length, *args, **kwargs):

        # Appending all variables from kwargs to self.
        self.__dict__ = kwargs
        # Setting default variables' values.
        default = {'xc': 0, 'yc': 0, 'zb': 0, 'interval': 0.02,
                   'point_density': 300, 'threshold': 0.04,
                   'noise_mode': 'linear', 'noise_ratio': 0.1,
                   'noise_range': 4}
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
        self.noise_mode = default['noise_mode']
        self.noise_ratio = default['noise_ratio']
        self.noise_range = default['noise_range']
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

        if 'random' in args:
            self.xrand, self.yrand, self.zrand = self.random_coordinates()
        if 'noise' in args:
            mode = self.noise_mode
            npoints = len(self.xx) * self.noise_ratio
            nrange = self.noise_range
            self.xnoise, self.ynoise, self.znoise = self.noise(mode, npoints,
                                                               nrange)

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
                points can be placed in.

        Returns
        -------
        xrand: numpy.ndarray
                Set of x-axis coordinates from  the pseudorandomly placed
                point cloud.
        yrand: numpy.ndarray
                Set of y-axis coordinates from  the pseudorandomly placed
                point cloud.
        zrand: numpy.ndarray
                Set of z-axis coordinates from  the pseudorandomly placed
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

        """
        This function generates a point cloud around the instance's shape,
        from the shape's surface up to a certain range, given by the user,
        pseudorandomly placed, based on the 'mode' value. The modes allowed
        by this function are:
            * uniform: for a uniformly distributed noise point cloud.
            * linear: for a point cloud distribution that linearly increases\
             in density as the distance from the surface of the shape\
             increases.
            * beta1: for a point cloud that follows the beta probability\
            function with alpha equals 3 and beta equals 1.
            * beta2: for a point cloud that follows the beta probability\
            function with alpha equals 2 and beta equals 1.

        Also, this function takes into account the desired number of points
        to place and the maximum range from the shape to place them.

        Parameters
        ----------
        mode: str
                Point cloud probability distribution, as described above.
        npoints: scalar
                Number of noise points to place.
        nrange: scalar
                Maximum distance from the shape's surface that points can be
                placed in.

        Returns
        -------
        xnoise-: numpy.ndarray
                Set of x-axis coordinates from  the noise point cloud.
        ynoise: numpy.ndarray
                Set of y-axis coordinates from  the noise point cloud.
        znoise: numpy.ndarray
                Set of z-axis coordinates from  the noise point cloud.
        """

        import numpy as np

        # Defining the noise mode dictionary.
        val = {'uniform': (1, 1, npoints), 'linear': (2, 1, npoints),
               'beta1': (3, 1, npoints), 'beta2': (6, 1, npoints)}

        # Generating the function 'f' based on the input 'mode'. This function
        # Will be used latter to generae the pseudorandom values.
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
        xnoise = self.xc + x_vals * np.cos(r_vals)
        ynoise = self.yc + y_vals * np.sin(r_vals)
        znoise = self.zb + z_vals

        return xnoise, ynoise, znoise

    def hslice(self, target, hmin, hmax):

        """
        This function performs the horizontal slicing of the shape, based
        on the minimum ('hmin') and maximum ('hmax') value for the shape's
        z-axis coordinates.
        The mode variable aims to perform the selection of the point cloud
        to be sliced.

        Parameters
        ----------
        target: str
                Option to select the target point cloud.
                'regular' for regularly placed point cloud, 'random'
                for pseudorandomly placed point cloud and 'noise' for noise
                point cloud.
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
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

        # Generating the slice mask.
        slice_mask = ((z >= hmin) & (z <= hmax))

        # Selecting the points that are True within the mask.
        xs = x[slice_mask]
        ys = y[slice_mask]
        zs = z[slice_mask]

        return xs, ys, zs

    def occlusion(self, target, angle1, angle2):

        import numpy as np
        from point_inside_polygon import point_inside_polygon

        # Checking for the 'mode' value to define which point cloud should
        # be sliced.
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

        # Initializing output lists as empty.
        xocclusion = []
        yocclusion = []
        zocclusion = []

        # Calculating the maximum values of x and y to use it as a distance
        # variable later.
        xmax = abs(np.max(x))
        ymax = abs(np.max(y))

        # Creating a subset of angular values between angle1 and angle2.
        R = np.arange(angle1, angle2, 0.2)

        # Calculating a set of points for the angular array (R)
        p1x = self.xc + ((xmax * 20) * np.cos(R))
        p1y = self.yc + ((ymax * 20) * np.sin(R))

        # Appending the points calculated between the selected angles and the
        # center coordinates of the object.
        xp = np.append(self.xc, p1x)
        yp = np.append(self.yc, p1y)

        # Creating a polygon array to use as a region of interest threshold in
        # order to apply the occlusion.
        poly = np.asarray([xp, yp]).T

        for i in range(len(x)):

            # Checking if the point with current ith x and y values is inside
            # the occlusion polygon.
            if point_inside_polygon(x[i], y[i], poly) is False:

                # Appending the points that are outside the occlusion polygon
                # to the output variables.
                xocclusion.append(x[i])
                yocclusion.append(y[i])
                zocclusion.append(z[i])

        return xocclusion, yocclusion, zocclusion

    def rotate(self, target, z_angle, y_angle, x_angle):

        """
        This function performs the rotation of the point cloud based on
        the angular values inputed. This function was based on the code
        from NiBabel (http://nipy.org/nibabel/). Starts the rotation at
        the z axis, followed by the y-axis and the x-axis. This function
        uses the right-hand rule as convention for the rotation angles.

        Parameters
        ----------
        target: str
                Option to select the target point cloud.
                'regular' for regularly placed point cloud, 'random'
                for pseudorandomly placed point cloud and 'noise' for noise
                point cloud.
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
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

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
        xrot, yrot, zrot = np.dot(R, M)

        return xrot, yrot, zrot


# Defining the Cone's shape class.
class Cone:

    """
    The Cone class performs the creation of a cone defined by
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
    r: scalar
            Radius of the shape over the x and y axis.
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
    noise_mode: str
            Option to select the type of point distribution to use in
            the noise point cloud.
    noise_ratio: scalar
            Noise to signal ratio to simulate.
    noise_range: scalar
            Maximum distance from the shape's surface to place the noise
            points in.

    Returns
    -------
    Cone: instance
            Cone's shape instance with the input and calculated
            parameter and the created point clouds.

    """
    # Setting the instance initial variables and functions
    # to run when the instance is created.
    def __init__(self, r, length, *args, **kwargs):

        # Appending all variables from kwargs to self.
        self.__dict__ = kwargs
        # Setting default variables' values.
        default = {'xc': 0, 'yc': 0, 'zb': 0, 'interval': 0.02,
                   'point_density': 300, 'threshold': 0.04,
                   'noise_mode': 'linear', 'noise_ratio': 0.1,
                   'noise_range': 4}
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
        self.noise_mode = default['noise_mode']
        self.noise_ratio = default['noise_ratio']
        self.noise_range = default['noise_range']
        self.length = length
        self.r = r

        # Executing functions to calculate basic parameters
        # from the instance's geometric shape.
        self.area_base = self.area_base()
        self.perimeter = self.perimeter()
        self.area_surface = self.area_surface()
        self.volume = self.volume()

        self.xx, self.yy, self.zz = self.point_coordinates()

        if 'random' in args:
            self.xrand, self.yrand, self.zrand = self.random_coordinates()
        if 'noise' in args:
            mode = self.noise_mode
            npoints = len(self.xx) * self.noise_ratio
            nrange = self.noise_range
            self.xnoise, self.ynoise, self.znoise = self.noise(mode, npoints,
                                                               nrange)

    def area_base(self):

        """
        This function calculates the base area of the instance's
        shape.

        """

        pi = 3.14159265359
        area_ = pi * (self.r ** 2)

        return area_

    def perimeter(self):

        """
        This function calculates the perimeter of the instance's
        shape.

        """

        pi = 3.14159265359

        # Calcultating the circumference.
        perimeter_ = 2 * pi * self.r

        return perimeter_

    def area_surface(self):

        """
        This function calculates the surface area of the instance's
        shape.

        """

        pi = 3.14159265359
        h = (self.r ** 2 + self.length ** 2) ** (1/2)

        area_surface_ = h * self.r * pi

        return area_surface_

    def volume(self):

        """
        This function calculates the volume of the instance's
        shape.

        """

        pi = 3.14159265359
        volume_ = (1 / 3) * pi * (self.r ** 2) * self.length

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

        # Calculating the lateral angle of the cone.
        angle_z = np.arctan(self.length / self.r)

        # Generating a z axis coordinates array with the size of
        # ((length / interval) * len(x)).
        # Filling a base z axis matrix with the same size as xx and yy.
        z1 = np.matrix(np.full([len(R)], 1))
        # Generating the set of z coordinate values to be generated.
        z2 = np.matrix(np.arange(0, self.length,
                                 self.interval))
        # Multiplying base z matrix (z1) and the z set of values (z2)
        z3 = z1.T * z2

        # Generating the final z coordinate array by reshaping the z
        # coordinates matrix (z3)
        zz = np.squeeze(np.reshape(np.asarray(z3), [len(R) * np.size(z2)]))

        # Calculating the z_factor of the cone, which is then used to
        # correct the x and y coordinates based on the z-axis coordinate.
        z_factor = 1 - ((zz / np.tan(angle_z)) / self.r)

        # Calculating the x and y coordinates of a horizontal transect
        # of the shape.
        x = self.r * np.cos(R)
        y = self.r * np.sin(R)

        # Repeating the xx and yy ellipse coordinates along the z axis.
        # Also, applying the correction factor on the x and y set of
        # coordinates.
        xx = self.xc + (np.repeat(x, np.size(z2)) * z_factor)
        yy = self.yc + (np.repeat(y, np.size(z2)) * z_factor)
        zz = self.zb + zz

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
                Set of x-axis coordinates from  the pseudorandomly placed
                point cloud.
        yrand: numpy.ndarray
                Set of y-axis coordinates from  the pseudorandomly placed
                point cloud.
        zrand: numpy.ndarray
                Set of z-axis coordinates from  the pseudorandomly placed
                point cloud.

        """

        import numpy as np

        # Calculating the lateral angle of the cone.
        angle_z = np.arctan(self.length / self.r)

        # Calculating the total amount of points to place on the surface
        # of the shape.
        n_points = int(self.area_surface * self.point_density)

        # Calculating the minimum and maximum values for the x, y and z
        # axis and for the angle (r_vals).
        xmin = ymin = self.r - self.threshold
        xmax = ymax = self.r + self.threshold
        zmin = self.zb
        zmax = self.zb + self.length
        rmin = 0
        rmax = 2 * np.pi

        # Generating n_points pseudorandom distance values for the x, y
        # and z axis and the angle (r_vals).
        x_vals = xmin + (np.random.sample(n_points) * (xmax - xmin))
        y_vals = ymin + (np.random.sample(n_points) * (ymax - ymin))
        z_vals = zmin + (np.random.sample(n_points) * (zmax - zmin))
        r_vals = rmin + (np.random.sample(n_points) * (rmax - rmin))

        # Calculating the z_factor of the cone, which is then used to
        # correct the x and y coordinates based on the z-axis coordinate.
        z_factor = 1 - ((z_vals / np.tan(angle_z)) / self.r)

        # Multiplying the pseudorandom distances values for the
        # pseudorandom angle values to obtain the set of x and y output
        # point coordinates.
        # Also, applying the correction factor on the x and y set of
        # coordinates.
        xrand = self.xc + (x_vals * np.cos(r_vals) * z_factor)
        yrand = self.yc + (y_vals * np.sin(r_vals) * z_factor)
        zrand = self.zb + z_vals

        return xrand, yrand, zrand

    def noise(self, mode, npoints, nrange):

        """
        This function generates a point cloud around the instance's shape,
        from the shape's surface up to a certain range, given by the user,
        pseudorandomly placed, based on the 'mode' value. The modes allowed
        by this function are:
            * uniform: for a uniformly distributed noise point cloud.
            * linear: for a point cloud distribution that linearly increases\
             in density as the distance from the surface of the shape\
             increases.
            * beta1: for a point cloud that follows the beta probability\
            function with alpha equals 3 and beta equals 1.
            * beta2: for a point cloud that follows the beta probability\
            function with alpha equals 2 and beta equals 1.

        Also, this function takes into account the desired number of points
        to place and the maximum range from the shape to place them.

        Parameters
        ----------
        mode: str
                Point cloud probability distribution, as described above.
        npoints: scalar
                Number of noise points to place.
        nrange: scalar
                Maximum distance from the shape's surface that points can be
                placed in.

        Returns
        -------
        xnoise-: numpy.ndarray
                Set of x-axis coordinates from  the noise point cloud.
        ynoise: numpy.ndarray
                Set of y-axis coordinates from  the noise point cloud.
        znoise: numpy.ndarray
                Set of z-axis coordinates from  the noise point cloud.
        """

        import numpy as np

        # Defining the noise mode dictionary.
        val = {'uniform': (1, 1, npoints), 'linear': (2, 1, npoints),
               'beta1': (3, 1, npoints), 'beta2': (6, 1, npoints)}

        # Generating the function 'f' based on the input 'mode'. This function
        # Will be used latter to generae the pseudorandom values.
        f = getattr(np.random, 'beta')

        # Calculating the minimum and maximum values for the x, y and z
        # axis and for the angle (r_vals).
        xmin = ymin = self.r
        xmax = ymax = self.r + nrange
        zmin = self.zb
        zmax = self.zb + self.length
        rmin = 0
        rmax = 2 * np.pi

        # Generating n_points random distance values for the x, y and z
        # axis and the angle (r_vals).
        x_vals = xmin + (f(*val[mode]) * (xmax - xmin))
        y_vals = ymin + (f(*val[mode]) * (ymax - ymin))
        z_vals = zmin + (np.random.sample(npoints) * (zmax - zmin))
        r_vals = rmin + (np.random.sample(npoints) * (rmax - rmin))

        # Calculating the lateral angle of the cone.
        angle_z = np.arctan(self.length / self.r)
        # Calculating the z_factor of the cone, which is then used to
        # correct the x and y coordinates based on the z-axis coordinate.
        z_factor = 1 - ((z_vals / np.tan(angle_z)) / self.r)

        # Multiplying the pseudorandom distances values for the
        # pseudorandom angle values to obtain the set of x, y and z output
        # point coordinates.
        xn = self.xc + (x_vals * np.cos(r_vals) * z_factor)
        yn = self.yc + (y_vals * np.sin(r_vals) * z_factor)
        zn = self.zb + z_vals

        return xn, yn, zn

    def hslice(self, target, hmin, hmax):

        """
        This function performs the horizontal slicing of the shape, based
        on the minimum ('hmin') and maximum ('hmax') value for the shape's
        z-axis coordinates.
        The mode variable aims to perform the selection of the point cloud
        to be sliced.

        Parameters
        ----------
        target: str
                Option to select the target point cloud.
                'regular' for regularly placed point cloud, 'random'
                for pseudorandomly placed point cloud and 'noise' for noise
                point cloud.
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
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

        # Generating the slice mask.
        slice_mask = ((z >= hmin) & (z <= hmax))

        # Selecting the points that are True within the mask.
        xs = x[slice_mask]
        ys = y[slice_mask]
        zs = z[slice_mask]

        return xs, ys, zs

    def occlusion(self, target, angle1, angle2):

        import numpy as np
        from point_inside_polygon import point_inside_polygon

        # Checking for the 'mode' value to define which point cloud should
        # be sliced.
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

        # Initializing output lists as empty.
        xocclusion = []
        yocclusion = []
        zocclusion = []

        # Calculating the maximum values of x and y to use it as a distance
        # variable later.
        xmax = abs(np.max(x))
        ymax = abs(np.max(y))

        # Creating a subset of angular values between angle1 and angle2.
        R = np.arange(angle1, angle2, 0.2)

        # Calculating a set of points for the angular array (R)
        p1x = self.xc + ((xmax * 20) * np.cos(R))
        p1y = self.yc + ((ymax * 20) * np.sin(R))

        # Appending the points calculated between the selected angles and the
        # center coordinates of the object.
        xp = np.append(self.xc, p1x)
        yp = np.append(self.yc, p1y)

        # Creating a polygon array to use as a region of interest threshold in
        # order to apply the occlusion.
        poly = np.asarray([xp, yp]).T

        for i in range(len(x)):

            # Checking if the point with current ith x and y values is inside
            # the occlusion polygon.
            if point_inside_polygon(x[i], y[i], poly) is False:

                # Appending the points that are outside the occlusion polygon
                # to the output variables.
                xocclusion.append(x[i])
                yocclusion.append(y[i])
                zocclusion.append(z[i])

        return xocclusion, yocclusion, zocclusion

    def rotate(self, target, z_angle, y_angle, x_angle):

        """
        This function performs the rotation of the point cloud based on
        the angular values inputed. This function was based on the code
        from NiBabel (http://nipy.org/nibabel/). Starts the rotation at
        the z axis, followed by the y-axis and the x-axis. This function
        uses the right-hand rule as convention for the rotation angles.

        Parameters
        ----------
        target: str
                Option to select the target point cloud.
                'regular' for regularly placed point cloud, 'random'
                for pseudorandomly placed point cloud and 'noise' for noise
                point cloud.
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
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

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
        xrot, yrot, zrot = np.dot(R, M)

        return xrot, yrot, zrot


# Defining the Spheroid's shape class.
class Spheroid:

    """
    The Spheroid class performs the creation of a spheroid defined by
    the input variables. It contains as embedded functions the calculation
    of the shape's basic parameters, such as axis perimeter, eccentricity,
    surface area and volume; functions to create a point cloud around
    the shape's surface, both by regularly and pseudorandomly placing
    points; and functions that can be called to obtain just a slice in any
    horizontal transcept of the shape and to rotate the shape. Both this
    later functions can be applied to the regularly and pseudorandomly
    placed point cloud.
    This function creates a spheroid based on the formulas presented
    at http://planetcalc.com/149/.

    Parameters
    ----------
    r: scalar
            Radius of the shape over the x and y axis.
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
    noise_mode: str
            Option to select the type of point distribution to use in
            the noise point cloud.
    noise_ratio: scalar
            Noise to signal ratio to simulate.
    noise_range: scalar
            Maximum distance from the shape's surface to place the noise
            points in.

    Returns
    -------
    Spheroid: instance
            Cone's shape instance with the input and calculated
            parameter and the created point clouds.

    References
    ----------
    .. [1] PLANETCALC - Spheroids, available at http://planetcalc.com/149/.
    """

    # Setting the instance initial variables and functions
    # to run when the instance is created.
    def __init__(self, r, zr, *args, **kwargs):

        # Appending all variables from kwargs to self.
        self.__dict__ = kwargs
        # Setting default variables' values.
        default = {'xc': 0, 'yc': 0, 'zc': 0, 'interval': 0.02,
                   'point_density': 300, 'threshold': 0.04,
                   'noise_mode': 'linear', 'noise_ratio': 0.1,
                   'noise_range': 4}
        # Updating the default variables dictionary.
        default.update(kwargs)

        # Setting basic variables, either from default values
        # or from required input arguments.
        self.xc = default['xc']
        self.yc = default['yc']
        self.zc = default['zc']
        self.interval = default['interval']
        self.point_density = default['point_density']
        self.threshold = default['threshold']
        self.noise_mode = default['noise_mode']
        self.noise_ratio = default['noise_ratio']
        self.noise_range = default['noise_range']
        self.r = r
        self.zr = zr

        # Executing functions to calculate basic parameters
        # from the instance's geometric shape.
        self.axis_perimeter = self.axis_perimeter()
        self.eccentricity = self.eccentricity()
        self.area_surface = self.area_surface()
        self.volume = self.volume()

        self.xx, self.yy, self.zz = self.point_coordinates()

        if 'random' in args:
            self.xrand, self.yrand, self.zrand = self.random_coordinates()
        if 'noise' in args:
            mode = self.noise_mode
            npoints = self.xx.size * self.noise_ratio
            nrange = self.noise_range
            self.xnoise, self.ynoise, self.znoise = self.noise(mode, npoints,
                                                               nrange)

    def axis_perimeter(self):

        """
        This function calculates the axis perimeter the instance's
        shape. This means that both x/y and z axis are calculated
        separatedly and might present different values.

        """

        pi = 3.14159265359

        perimeter_xy = 2 * pi * self.r

        # Calculating h.
        h = ((self.zr - self.r) ** 2)/((self.zr + self.r) ** 2)

        # Calcultating the circumference based of the approximation of
        # Ramanujan.
        perimeter_z = pi * (self.zr + self.r) * (1 + ((3 * h) /
                                                 (10 + ((4 - 3 * h) **
                                                        (1/2)))))

        return perimeter_xy, perimeter_z

    def eccentricity(self):

        """
        This function calculates eccentricity of the spheroid,
        considering if it is a prolate spheroid, oblate spheroid
        or a sphere.

        """

        import math

        if self.zr < self.r:

            e = math.acos(self.zr / self.r)

        elif self.zr > self.r:

            e = math.acos(self.r / self.zr)

        elif self.zr == self.r:

            e = 0

        return e

    def area_surface(self):

        """
        This function calculates the surface area of the instance's
        shape.

        """

        import math

        pi = 3.14159265359

        e = self.eccentricity

        if self.zr < self.r:

            area_surface_ = (2 * pi * (self.r ** 2 + ((self.zr ** 2) /
                             math.sin(e)) * math.log((1 + math.sin(e)) /
                                                     math.cos(e))))

        elif self.zr > self.r:

            area_surface_ = (2 * pi * ((self.r ** 2) +
                             (((self.r * self.zr * e) / math.sin(e)))))

        elif self.zr == self.r:
            area_surface_ = 4 * pi * (self.r ** 2)

        return area_surface_

    def volume(self):

        """
        This function calculates the volume of the instance's
        shape.

        """

        pi = 3.14159265359
        volume_ = (3 / 4) * pi * (self.r ** 2) * self.zr

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

        # Calculating the axes perimeters for the x/y and z axis.
        perimeter_xy, perimeter_z = self.axis_perimeter

        # Calculating the angle interval between the points both on
        # x/y and z axis.
        angle_xy = (2 * np.pi * self.interval) / perimeter_xy
        angle_z = (2 * np.pi * self.interval) / perimeter_z

        # Generating the phi and theta angular values to place points
        # at.
        phi, theta = np.mgrid[0:np.pi:angle_z, 0:2 * np.pi:angle_xy]

        # Calculating the x, y and z axis coordinate values for the
        # shape.
        xx = self.xc + (self.r * np.sin(phi) * np.cos(theta))
        yy = self.yc + (self.r * np.sin(phi) * np.sin(theta))
        zz = self.zc + (self.zr * np.cos(phi))

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
                Set of x-axis coordinates from  the pseudorandomly placed
                point cloud.
        yrand: numpy.ndarray
                Set of y-axis coordinates from  the pseudorandomly placed
                point cloud.
        zrand: numpy.ndarray
                Set of z-axis coordinates from  the pseudorandomly placed
                point cloud.

        """

        import numpy as np

        # Calculating the total amount of points to place on the surface
        # of the shape.
        n_points = int(self.area_surface * self.point_density)

        # Calculating the minimum and maximum values for the phi, theta and
        # r and zr radii.
        phi_min = 0
        phi_max = np.pi
        theta_min = 0
        theta_max = 2 * np.pi
        rmin = self.r - self.threshold
        rmax = self.r + self.threshold
        zrmin = self.zr - self.threshold
        zrmax = self.zr + self.threshold

        # Generating n_points pseudorandom values for the phi, theta and
        # r and zr radii.
        phi_vals = phi_min + (np.random.sample(n_points) * (phi_min -
                              phi_max))
        theta_vals = theta_min + (np.random.sample(n_points) * (theta_min -
                                  theta_max))
        r_vals = rmin + (np.random.sample(n_points) * (rmin - rmax))
        zr_vals = zrmin + (np.random.sample(n_points) * (zrmin - zrmax))

        # Calculating the x, y and z axis coordinate values for the
        # shape.
        xr = self.xc + (r_vals * np.sin(phi_vals) * np.cos(theta_vals))
        yr = self.yc + (r_vals * np.sin(phi_vals) * np.sin(theta_vals))
        zr = self.zc + (zr_vals * np.cos(phi_vals))

        return xr, yr, zr

    def noise(self, mode, npoints, nrange):

        """
        This function generates a point cloud around the instance's shape,
        from the shape's surface up to a certain range, given by the user,
        pseudorandomly placed, based on the 'mode' value. The modes allowed
        by this function are:
            * uniform: for a uniformly distributed noise point cloud.
            * linear: for a point cloud distribution that linearly increases\
             in density as the distance from the surface of the shape\
             increases.
            * beta1: for a point cloud that follows the beta probability\
            function with alpha equals 3 and beta equals 1.
            * beta2: for a point cloud that follows the beta probability\
            function with alpha equals 2 and beta equals 1.

        Also, this function takes into account the desired number of points
        to place and the maximum range from the shape to place them.

        Parameters
        ----------
        mode: str
                Point cloud probability distribution, as described above.
        npoints: scalar
                Number of noise points to place.
        nrange: scalar
                Maximum distance from the shape's surface that points can be
                placed in.

        Returns
        -------
        xnoise-: numpy.ndarray
                Set of x-axis coordinates from  the noise point cloud.
        ynoise: numpy.ndarray
                Set of y-axis coordinates from  the noise point cloud.
        znoise: numpy.ndarray
                Set of z-axis coordinates from  the noise point cloud.
        """

        import numpy as np

        # Defining the noise mode dictionary.
        val = {'uniform': (1, 1, npoints), 'linear': (2, 1, npoints),
               'beta1': (3, 1, npoints), 'beta2': (6, 1, npoints)}

        # Generating the function 'f' based on the input 'mode'. This function
        # Will be used latter to generae the pseudorandom values.
        f = getattr(np.random, 'beta')

        # Calculating the minimum and maximum values for the phi, theta and
        # r and zr radii.
        phi_min = 0
        phi_max = np.pi
        theta_min = 0
        theta_max = 2 * np.pi
        rmin = self.r
        rmax = self.r + nrange
        zrmin = self.zr
        zrmax = self.zr + nrange

        # Generating n_points pseudorandom values for the phi, theta and
        # r and zr radii.
        phi_vals = phi_min + (np.random.sample(npoints) * (phi_max -
                              phi_min))
        theta_vals = theta_min + (np.random.sample(npoints) * (theta_max -
                                  theta_min))
        r_vals = rmin + (f(*val[mode]) * (rmax - rmin))
        zr_vals = zrmin + (f(*val[mode]) * (zrmax - zrmin))

        # Calculating the x, y and z axis coordinate values for the
        # shape.
        xnoise = self.xc + (r_vals * np.sin(phi_vals) * np.cos(theta_vals))
        ynoise = self.yc + (r_vals * np.sin(phi_vals) * np.sin(theta_vals))
        znoise = self.zc + (zr_vals * np.cos(phi_vals))

        return xnoise, ynoise, znoise

    def hslice(self, target, hmin, hmax):

        """
        This function performs the horizontal slicing of the shape, based
        on the minimum ('hmin') and maximum ('hmax') value for the shape's
        z-axis coordinates.
        The mode variable aims to perform the selection of the point cloud
        to be sliced.

        Parameters
        ----------
        target: str
                Option to select the target point cloud.
                'regular' for regularly placed point cloud, 'random'
                for pseudorandomly placed point cloud and 'noise' for noise
                point cloud.
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
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

        # Generating the slice mask.
        slice_mask = ((z >= hmin) & (z <= hmax))

        # Selecting the points that are True within the mask.
        xs = x[slice_mask]
        ys = y[slice_mask]
        zs = z[slice_mask]

        return xs, ys, zs

    def occlusion(self, target, angle1, angle2):

        import numpy as np
        from point_inside_polygon import point_inside_polygon

        # Checking for the 'mode' value to define which point cloud should
        # be sliced.
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

        # Reshaping the x, y and z matrices into 1D vectors, aiming to avoid
        # problems with the logical conditioners from the
        # point_inside_polygon in a latter stage.
        x = np.reshape(x, x.size)
        y = np.reshape(y, y.size)
        z = np.reshape(z, z.size)

        # Initializing output lists as empty.
        xocclusion = []
        yocclusion = []
        zocclusion = []

        # Calculating the maximum values of x and y to use it as a distance
        # variable later.
        xmax = abs(np.max(x))
        ymax = abs(np.max(y))

        # Creating a subset of angular values between angle1 and angle2.
        R = np.arange(angle1, angle2, 0.2)

        # Calculating a set of points for the angular array (R)
        p1x = self.xc + ((xmax * 20) * np.cos(R))
        p1y = self.yc + ((ymax * 20) * np.sin(R))

        # Appending the points calculated between the selected angles and the
        # center coordinates of the object.
        xp = np.append(self.xc, p1x)
        yp = np.append(self.yc, p1y)

        # Creating a polygon array to use as a region of interest threshold in
        # order to apply the occlusion.
        poly = np.asarray([xp, yp]).T

        for i in range(len(x)):

            # Checking if the point with current ith x and y values is inside
            # the occlusion polygon.
            if point_inside_polygon(x[i], y[i], poly) is False:

                # Appending the points that are outside the occlusion polygon
                # to the output variables.
                xocclusion.append(x[i])
                yocclusion.append(y[i])
                zocclusion.append(z[i])

        return xocclusion, yocclusion, zocclusion

    def rotate(self, target, z_angle, y_angle, x_angle):

        """
        This function performs the rotation of the point cloud based on
        the angular values inputed. This function was based on the code
        from NiBabel (http://nipy.org/nibabel/). Starts the rotation at
        the z axis, followed by the y-axis and the x-axis. This function
        uses the right-hand rule as convention for the rotation angles.

        Parameters
        ----------
        target: str
                Option to select the target point cloud.
                'regular' for regularly placed point cloud, 'random'
                for pseudorandomly placed point cloud and 'noise' for noise
                point cloud.
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
        if (target == 'regular'):  # If 'regular' slices the regularly placed
                                    # point cloud.
            x = self.xx
            y = self.yy
            z = self.zz

        elif (target == 'random'):  # If 'random' slices the pseudorandomly
                                    # placed point cloud.
            try:
                x = self.xrand
                y = self.yrand
                z = self.zrand
            except:
                raise Exception('Pseudorandom point cloud not found! To use\
 the pseudorandom point cloud you must first create it by calling the\
 argument "random".')

        elif (target == 'noise'):  # If 'noise' slices the noise
                                    #  point cloud.
            try:
                x = self.xnoise
                y = self.ynoise
                z = self.znoise
            except:
                raise Exception('Noise point cloud not found! To use the\
 noise point cloud you must first create it by calling the argument "noise".')

        else:
            raise ValueError('Point cloud target option not recognized')

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
        xrot, yrot, zrot = np.dot(R, M)

        return xrot, yrot, zrot
