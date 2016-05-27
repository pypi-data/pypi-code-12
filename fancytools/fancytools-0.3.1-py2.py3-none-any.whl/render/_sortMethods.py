# -*- coding: utf-8 *-*
from copy import deepcopy

from fancytools.math.nearestPosition2 import NearestPosition2



class _UniformNearestPosition():
    def __init__(self, grid):
        self.start = grid[0]
        self.step = grid[1]-grid[0]

    def __call__(self, value):
        return round((value - self.start) / self.step)



class _SortBase:

    def __init__(self, grid, resolution, isuniform):
        self.resolution = resolution
        self.isuniform = isuniform
        self.grid = grid#self.render.opts['grid']

        self.reset()

    def reset(self):
        if self.isuniform:
            self.nearest = [_UniformNearestPosition(g) for g in self.grid]
        else:
            self.nearest = [NearestPosition2(g) for g in self.grid]



class Aliased(_SortBase):
    '''
    Takes one or more source-instances as list or tuple. Create like this::

        myMatrix = nIOp.target.CoarseMatrix( (mySource1,...mySourceN) )

    Coarse matrices store values of the mergeDimension at the nearest point in the
    mergeMatrix given by the difference of the values of the basisDimension and
    and the values of the basisMatrix. The following images illustrated this procedure.

    .. image:: _static/coarseMatrix_1D.png
       #:scale: 60 %
    .. image:: _static/coarseMatrix_2D.png
       #:scale: 60 %
    '''

    def reset(self):
        self.positionsIntensities = [[[ ],1]]
        for _ in range(len(self.grid)):
            self.positionsIntensities[0][0].append(0)
        self._majorPositions = self.positionsIntensities[0][0]
        _SortBase.reset(self)



    def getPositionsIntensities(self, point):
        for i, (p,n) in enumerate(zip(point, self.nearest)):
            self._majorPositions[i] = n(p)
        return self.positionsIntensities



class AntiAliased(_SortBase):
    '''
    Takes one or more source-instances as list.
    Create like this::

        myMatrix = nIOp.target.fineMatrix( (mySource1,...mySourceN) )

    This class isn't as fast as :class:`.coarseMatrix` but can assign values
    in a more accurate way if the following condition is fullfilled:
    
    .. note:: number of datapoints in matrix>> matrix-resolution
    
    In a fineMatrix the values of the mergeDimensions were stored in the mergeMatrix
    at the nearest point (analoque to the procedure of the :class:`.coarseMatrix`)
    AND all points near this point. Depending on the number of basisDimensions the following
    number of positions were filled:
    
    =======  ==========
    nBasis   nPositions
    =======  ==========
    1        2
    2        4
    3        8
    =======  ==========


    This splitted values are wheighted through
    its values in the densityMatrix - ther pointsdensity.
    The sum of this pointsdensity is allways one. The following images should illustrate this procedure:
    
    .. image:: _static/fineMatrix_1D.png
       :scale: 60 %

    .. image:: _static/fineMatrix_2D.png
       :scale: 60 %
    '''

    def reset(self):
        ndim = len(self.grid)
        self.positionsIntensities = [[[ ],1]]
        self.anzAffectedCells = 2**ndim
        self.affectedCellCounter =  []
        for i in range(1,ndim+1,1):
            self.affectedCellCounter.append((2**i/2) -1)
        
        for i in range(ndim):
            self.positionsIntensities[0][0].append(0)

        for _ in range(self.anzAffectedCells-1):
            #1D: 2 cells
            #2D: 4 cells
            #3D: 8 cells
            self.positionsIntensities.append(deepcopy(self.positionsIntensities[0]))

        _SortBase.reset(self)


    def getPositionsIntensities(self, point):
        for i in range(self.anzAffectedCells):
            # reset intensities (later there is a *=)
            self.positionsIntensities[i][1] = 1
        for i, (p, g, n) in enumerate(zip(point, self.grid, self.nearest)):

            nearest_point = n(p)
            nearest_diff = abs(g[nearest_point] -p)
            if nearest_point == 0:  # is first point of array - neared point is second point
                sec_nearest_point = 1
            elif nearest_point == self.resolution[i]-1:  # is last point of array
                sec_nearest_point = nearest_point-1  # basis.getResolution()-2
            else:  # whose of the neigbours is closer
                lastVal = g[nearest_point-1]
                nextVal = g[nearest_point+1]
                lastDiff = abs(lastVal-p)
                nextDiff = abs(nextVal-p)
                if lastDiff < nextDiff:
                    sec_nearest_point = nearest_point-1
                    #sec_nearest_diff = lastDiff
                else:
                    sec_nearest_point = nearest_point+1
                    #sec_nearest_diff = nextDiff 
            sec_nearest_diff = abs(g[sec_nearest_point] -p)
            #sec_nearest_point get some of the intensity of the nearest point
            transfered_intensity = (sec_nearest_diff-
                nearest_diff) / sec_nearest_diff
            n = 0
            write_point = nearest_point
            nearest_intensity = 1 - transfered_intensity
            sec_nearest_intensity = transfered_intensity
            intensity = nearest_intensity
            for j in range(self.anzAffectedCells):
                self.positionsIntensities[j][0][i] = write_point
                self.positionsIntensities[j][1] *= intensity
                if n == self.affectedCellCounter[i]:
                    if write_point == nearest_point:
                        write_point = sec_nearest_point
                        intensity = sec_nearest_intensity
                    else:
                        write_point = nearest_point
                        intensity = nearest_intensity
                    n = -1
                n += 1
        return self.positionsIntensities