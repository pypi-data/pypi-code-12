'''
Created on 21 Aug 2015

#taken from http://codentronix.com/2011/04/20/simulation-of-3d-point-rotation-with-python-and-pygame/
'''


from math import pi, cos, sin
 

class Point3D:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = float(x), float(y), float(z)
 
    def rotateX(self, angle):
        """ Rotates the point around the X axis by the given angle in degrees. """
        rad = angle * pi / 180
        cosa = cos(rad)
        sina = sin(rad)
        y = self.y * cosa - self.z * sina
        z = self.y * sina + self.z * cosa
        return Point3D(self.x, y, z)
 
    def rotateY(self, angle):
        """ Rotates the point around the Y axis by the given angle in degrees. """
        rad = angle * pi / 180
        cosa = cos(rad)
        sina = sin(rad)
        z = self.z * cosa - self.x * sina
        x = self.z * sina + self.x * cosa
        return Point3D(x, self.y, z)
 
    def rotateZ(self, angle):
        """ Rotates the point around the Z axis by the given angle in degrees. """
        rad = angle * pi / 180
        cosa = cos(rad)
        sina = sin(rad)
        x = self.x * cosa - self.y * sina
        y = self.x * sina + self.y * cosa
        return Point3D(x, y, self.z)
 
    def project(self, win_width, win_height, fov, viewer_distance):
        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (viewer_distance + self.z)
        x = self.x * factor + win_width / 2
        y = -self.y * factor + win_height / 2
        return Point3D(x, y, 1)



if __name__ == '__main__':
    p = Point3D(640,-480,0)
    angleX, angleY, angleZ = 0,0,0
    win_width = 640
    win_height = 480 
    fov = 1
    viewer_distance = 1
    
    p_rot = p.rotateX(angleX).rotateY(angleY).rotateZ(angleZ)
    # Transform the point from 3D to 2D
    p_proj = p_rot.project(win_width, win_height, fov, viewer_distance)
    print p_proj.x, p_proj.y
