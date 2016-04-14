# -*- coding: utf-8 -*-
"""
Easy visualization of point clouds and geometric primitives
Created on Fri Apr 08 12:01:56 2011

.. Author: Øystein Skotheim, SINTEF ICT <oystein.skotheim@sintef.no>
   Date:   Thu Sep 12 15:50:40 2013

"""

import vtk
from renderwidget import RenderWidget
from pointobject import *
                
class VTKVisualizerControl:
    "Class for easy visualization of point clouds and geometric primitives"
    
    def __init__(self, parent=None):
        "Create a wiget with a VTK Visualizer Control in it"
        self.pointObjects = []
        self.renderer = vtk.vtkRenderer()
        self.renderWidget = RenderWidget(self.renderer, parent)
        self.renderWindow = self.renderWidget.renderWindow
        self.widget = self.renderWidget.widget
        
    def __del__(self):
        del self.renderWidget
                        
    def AddPointCloudActor(self, pc):
        """Add a point cloud from a given NumPy array
        
        The NumPy array should have dimension Nxd where d >= 3
        
        If d>3, the points will be colored according to the last column
        in the supplied array (values should be between 0 and 1, where 
        0 is black and 1 is white)
        """        
        obj = VTKObject()
        obj.CreateFromArray(pc)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddColoredPointCloudActor(self, pc):    
        """Add a point cloud with colors from a given NumPy array
        
        The NumPy array should have dimension Nx6 where the first three
        dimensions correspond to X, Y and Z and the last three dimensions
        correspond to R, G and B values (between 0 and 255)        
        """        
        
        obj = VTKObject()
        obj.CreateFromArray(pc[:,:3])
        obj.AddColors(pc[:,3:6].astype(np.uint8))
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddShadedPointsActor(self, pc):    
        """Add a point cloud with shaded points based on supplied normal vectors
        
        The NumPy array should have dimension Nx6 where the first three
        dimensions correspond to x, y and z and the last three dimensions
        correspond to surface normals (nx, ny, nz)
        """        
        
        obj = VTKObject()
        obj.CreateFromArray(pc[:,0:3])
        obj.AddNormals(pc[:,3:6])
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddPolyDataMeshActor(self,pd):
        "Add a supplied vtkPolyData object to the visualizer"
        obj = VTKObject()
        obj.CreateMeshFromPolyData(pd)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddSTLActor(self,filename):
        "Load a mesh from an STL file and add it to the visualizer" 
        obj = VTKObject()
        obj.CreateFromSTL(filename)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddPLYActor(self,filename):
        "Load a mesh from a PLY file and add it to the visualizer"         
        obj = VTKObject()
        obj.CreateFromPLY(filename)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())
        
    def AddNormalsActor(self,pc, scale):
        """Add a set of surface normals to the visualizer
        
        The input is a NumPy array with dimension Nx6 with (x,y,z) and
        (nx,ny,nz) values for the points and associated surface normals
        
        The normals will be scaled according to given scale factor"""
                
        obj = VTKObject()
        obj.CreateFromArray(pc[:,0:3])
        obj.AddNormals(pc[:,3:6])
        obj.SetupPipelineHedgeHog(scale)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddHedgeHogActor(self,pc, scale):        
        """Add shaded points with surface normals to the visualizer
        
        The input is a NumPy array with dimension Nx6 with (x,y,z) and
        (nx,ny,nz) values for the points and associated surface normals
        
        The normals will be scaled according to given scale factor"""
        # Add the points
        self.AddShadedPointsActor(pc)    
        actor = self.GetLastActor()
        actor.GetProperty().SetColor(1,1,1)
        actor.GetProperty().SetPointSize(5.0)
        actor.GetProperty().SetInterpolation(True)
        # Add the normals
        self.AddNormalsActor(pc, scale)        
        
    def AddHedgeHogActorWithScalars(self,pc,scale):   
        """Add shaded points with surface normals and scalars to the visualizer
        
        The input is a NumPy array with dimension Nx7 with (x,y,z),
        (nx,ny,nz) and scalar (the last dimension contains the scalars)
        
        The normals will be scaled according to given scale factor"""
        # Add the points
        self.AddPointCloudActor(pc[:,[0,1,2,-1]])    
        actor = self.GetLastActor()
        actor.GetProperty().SetColor(1,1,1)
        actor.GetProperty().SetPointSize(5.0)
        # Add the normals
        self.AddNormalsActor(pc,scale)  
        
    def AddAxesActor(self,length):
        "Add coordinate system axes with specified length"
        obj = VTKObject()
        obj.CreateAxes(length)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())
    
    def AddActor(self,actor):
        "Add a supplied vtkActor object to the visualizer"
        obj = VTKObject()
        obj.CreateFromActor(actor)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())
                        
    def ResetCamera(self):
        "Reset the camera to fit contents"
        self.renderer.ResetCamera()
        
    def Render(self):
        "Render all objects"
        self.renderWindow.Render()
        
    def GetNumberOfActors(self):
        "Get the number of actors added to visualizer"
        return len(self.pointObjects)
        
    def GetLastActorID(self):
        "Get the ID of the last actor added to the visualizer"        
        return len(self.pointObjects)-1
        
    def RemoveAllActors(self):
        "Remove all actors from the visualizer"
        self.pointObjects = []
        self.renderer.RemoveAllViewProps()
        
    def RemoveLastActor(self):
        "Remove the last added actor from the visualizer"
        if len(self.pointObjects) > 0:
            idx = self.GetLastActorID()
            obj = self.pointObjects[idx]
            self.renderer.RemoveActor(obj.GetActor())
            del self.pointObjects[idx]
    
    def GetLastActor(self):
        "Get the actor last added to the visualizer"
        return self.pointObjects[self.GetLastActorID()].GetActor()
        
    def GetActor(self, idx):
        "Get the actor add the specified location"
        return self.pointObjects[idx].GetActor()
        
    def SetActorColor(self, idx, rgb):        
        """Set the color of the specified actor index
        
        rgb is a tuple of (r,g,b) values in the range 0..1
        """
        self.GetActor(idx).GetProperty().SetColor(rgb[0],rgb[1],rgb[2])

    def SetActorOpacity(self, idx, opacity):        
        "Set the opacity (0..1) of the specified actor index"       
        self.GetActor(idx).GetProperty().SetOpacity(opacity)
        
    def SetActorTransform(self, idx, T):
        """Set the pose (location and orientation) of the specified actor index
        
        T is a 4x4 NumPy array containing rotation matrix and translation vector"""
        
        self.GetActor(idx).SetUserTransform(self._array2vtkTransform(T))
        
    def SetActorScale(self, idx, scale):
        "Set the scale of supplied actor index (tuple of 3 values)"
        self.GetActor(idx).SetScale(*scale)
        
    def SetActorVisibility(self, idx,visibility):
        "Toggle visibility of the specified actor index on or of"
        if visibility: 
            self.GetActor(idx).VisibilityOn()
        else:
            self.GetActor(idx).VisibilityOff()
            
    def SetWindowBackground(self,r,g,b):
        "Set the background color of the visualizer to given R, G and B color"
        self.renderer.SetBackground(r,g,b)
        
    def ScreenShot(self,filename):
        "Create a screenshot of the visualizer in BMP format"
        win2img = vtk.vtkWindowToImageFilter()
        win2img.SetInput(self.renderWindow)
        win2img.Update()
        bmpWriter = vtk.vtkBMPWriter()
        bmpWriter.SetInput(win2img.GetOutput())
        bmpWriter.SetFileName(filename)
        bmpWriter.Write()
        
    def Close(self):
        "Close the visualization widget"
        self.widget.close()
        
    # Primitives
    def AddSphere(self, origin, r):
        "Add a sphere with given origin (x,y,z) and radius r"        
        obj = VTKObject()
        obj.CreateSphere(origin, r)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddCylinder(self, origin, r, h):
        "Add a cylinder with given origin (x,y,z), radius r and height h"               
        obj = VTKObject()
        obj.CreateCylinder(origin, r, h)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())
                
    def AddPlane(self,normal=None, origin=None):
        """Add a plane (optionally with a given normal vector and origin)
        
        Note: SetActorScale can be used to scale the extent of the plane"""
        obj = VTKObject()
        obj.CreatePlane(normal, origin)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())

    def AddBox(self,bounds):
        "Add a box witih the given bounds=[xmin,xmax,ymin,ymax,zmin,zmax]"        
        obj = VTKObject()
        obj.CreateBox(bounds)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())
        
    def AddLine(self,p1,p2):
        "Add a 3D line from p1=[x1,y1,z1] to p2=[x2,y2,z2]"
        obj = VTKObject()
        obj.CreateLine(p1,p2)
        self.pointObjects.append(obj)
        self.renderer.AddActor(obj.GetActor())
        
    # Helper functions    
    def _array2vtkTransform(self,arr):
        T = vtk.vtkTransform()
        matrix = vtk.vtkMatrix4x4()
        for i in range(0,4):
            for j in range(0,4):
                matrix.SetElement(i, j, arr[i,j])
        T.SetMatrix(matrix)
        return T
                                                            
if __name__ == '__main__':

    import sys
    from python_qt_binding import QtGui
        
    vtkControl = VTKVisualizerControl()
    
    # Add a red sphere
    vtkControl.AddSphere((0,0,0), 5.0)
    nID = vtkControl.GetLastActorID()
    vtkControl.SetActorColor(nID, (1,0,0))   
    
    # Add a blue, partly transparent box
    vtkControl.AddBox([-10,10,-10,10,-10,10])
    nID = vtkControl.GetLastActorID()
    vtkControl.SetActorColor(nID, (0.8,0.8,1.0))   
    vtkControl.SetActorOpacity(nID, 0.5)
    
        
    app = QtGui.QApplication.instance()
    
    if app is None:
        app = QtGui.QApplication(sys.argv)

    app.exec_()            