
import pyspatiotemporalgeom.region as region
from pyspatiotemporalgeom.utilities import segLibrary
import math
import bisect




def overlay(r1, r2, gridScalar = .00001 ):
    
    # get the min/max x, y vals
    #convert halfsegments to segments with an index
    r1 = [ s[0] for s in r1 if s[0][0] < s[0][1]]
    r2 = [ s[0] for s in r2 if s[0][0] < s[0][1]]
    indexedR1 = []
    indexedR2 = []
    for i in xrange( len( r1 ) ):
        indexedR1.append( (r1[i][0],r1[i][1],i) )
    r1 = indexedR1
    for i in xrange( len( r2 ) ):
        indexedR2.append( (r2[i][0],r2[i][1],i) )
    r2 = indexedR2
    xvals = [s[0][0] for s in r1] + [s[1][0] for s in r2]
    xmin = min( xvals )
    xmax = max( xvals )
    yvals = [s[0][1] for s in r1] + [s[1][1] for s in r2]
    ymin = min( yvals )
    ymax = max( yvals )

    xdif = xmax - xmin
    ydif = ymax - ymin

    cellSize = max( xdif,ydif ) * gridScalar
    # assign the cells

    cellDict1 = dict()
    cellDict2 = dict()
    usedCells1 = set()
    usedCells2 = set()

    assignCells( r1, cellSize, cellDict1, usedCells1 )

    assignCells( r2, cellSize, cellDict2, usedCells2 )

    usedCells = usedCells1 & usedCells2
    print 'num used cells:', len( usedCells)
    
    #for keys in usedCells:
    #    print keys, '1 ' , cellDict1[keys], '2 ', cellDict2[keys]

    pois1 = []
    pois2 = []
    # look for the intersection points
    for key in usedCells:
        for s1 in cellDict1[key]:
            for s2 in cellDict2[key]:
                # compute intersection point.
                x1 = s1[0][0]
                y1 = s1[0][1]
                x2 = s1[1][0]
                y2 = s1[1][1]
                x3 = s2[0][0]
                y3 = s2[0][1]
                x4 = s2[1][0]
                y4 = s2[1][1]

                # check for colinear overlapping case
                if segLibrary.isCollinearAndOverlapping( s1, s2 ):
                        ll = x1
                        lu = x2
                        rl = x3
                        ru = x4
                        # if theya are near vertical, use the y vals
                        if abs( x1-x2) < 0.0000001:
                                ll = y1
                                lu = y2 
                                rl = y3 
                                ru = y4 
                        if rl < ll and ll < ru:
                                intersectPoi = (s2[2],(x1, y1))
                                pois2.append( intersectPoi )
                        if rl < lu and lu < ru:
                                intersectPoi = (s2[2],(x2, y2))
                                pois2.append( intersectPoi )
                        if ll < rl and rl < lu:
                                intersectPoi = (s1[2],(x3, y3))
                                pois1.append( intersectPoi )
                        if ll < ru and ru < lu:
                                intersectPoi = (s1[2],(x4, y4))
                                pois1.append( intersectPoi )
                        continue

                # if an end point is shared, no intersection
                if s1[0] == s2[0] or s1[0] == s2[1] or s1[1] == s2[0] or s1[1] == s2[1]:
                    continue

                denom = ((y4-y3)*(x2-x1)) - ((x4-x3)*(y2-y1))
                if denom == 0.0:   #lines are parallel, no intersection
                    continue

                ua = ((x4-x3)*(y1-y3))-((y4-y3)*(x1-x3))
                ua = ua / denom
                ub = ((x2-x1)*(y1-y3))-((y2-y1)*(x1-x3))
                ub = ub / denom
                # if we get here, the lines are not parallel.  they must intersect somewhere
                # check for intersections in a seg interior
                # record the segs so that we can construct the resulting segs
                if 0.0 < ua and ua < 1.0 and 0.0 <= ub and ub <= 1.0:
                        x = x1 + (ua * (x2-x1) )
                        y = y1 + (ua * (y2-y1) )
                        intersectPoi = (s1[2],(x, y))
                        if intersectPoi[1] != s1[0] and intersectPoi[1] != s1[1]:
                            pois1.append( intersectPoi )
                                
                if  0.0 < ub and ub < 1.0 and 0.0 <= ua and ua <= 1.0:
                        x = x1 + (ua * (x2-x1) )
                        y = y1 + (ua * (y2-y1) )
                        intersectPoi = (s2[2],(x, y))
                        if intersectPoi[1] != s2[0] and intersectPoi[1] != s2[1]:
                            pois2.append( intersectPoi )

    pois1 = list(set( pois1 ))
    pois2 = list(set( pois2 ))
    pois1.sort()
    pois2.sort()
    
    print 'done intersect, noiw build'
    # build the resulting segs
    r1 = segLibrary.constructSegs( pois1, r1 )
    r2 = segLibrary.constructSegs( pois2, r2 )
    print 'done build'
    print 'result r1'
    r1.sort()
    for s in r1:
        print s

    print 'result r2'
    r2.sort()
    for s in r2:
        print s
    
    r1Final = computeTopology( r1, usedCells2, cellDict2, cellSize )
    r2Final = computeTopology( r2, usedCells1, cellDict1, cellSize )
    print '---------------'
    print 'result 1'
    for s in r1Final:
        print s

    print 'result 2'
    for s in r2Final:
        print s

def computeTopology( r1, usedCells2, cellDict2, cellSize ):
    # figure out the topology
    # make a sorted list out of used cells
    cells2 = list( usedCells2 )
    cells2.sort()
    
    finalR1Segs = []
    # grab a seg, do the point in poly with it
    for s in r1:
        boundsOtherReg = False
        count = 0
        colinSeg = False
        # find the cell of its left end point:
        x0 = s[0][0]
        y0 = s[0][1]
        y1 = s[1][1]
        cellX = int (x0 // cellSize)  
        cellY = int (y0 // cellSize)  
        # if a left Y end point is on a cell boundary and 
        # the segs extends down, record the upper cell, and adust start
        if math.fmod(y0, cellSize) == 0.0 and y0 > y1:
            cellY -= 1
        # now we got the cell:
        #print '==========='
        #print 'seg, cell:', s , cellX, cellY
        # find the first occurrence of the cell in the list
        index = bisect.bisect_left( cells2, (cellX, cellY) )
        cells2Len = len( cells2)
        if index > 0 and index < cells2Len and cells2[index][0] > cellX:
            index -=1
        # now do a ray shoot down the column
        while index < cells2Len and index >=0 and cells2[index][0] == cellX:
            #print 'looking cell: ' , cells2[index]
            for s2 in cellDict2[cells2[index]]:
                #print 's2: ', s2
                if index > 0 and cells2[index-1][0] == cellX and s2 in cellDict2[cells2[index-1]]:
                    continue
                s2IsVert =  s2[0][0] == s2[1][0]
                # if s2 is vertical
                if s2IsVert:
                    #print 'vert'
                    #skip it unless s1 is also vertical
                    if segLibrary.collinear( s, s2 ):
                        # if s[0] is on s2, then s bounds r2.  mark it accordingly
                        #print 'colin'
                        if s2[0][1] <= s[0][1] and s[0][1] < s2[1][1]:
                            #print 'spans!'
                            boundsOtherReg = True
                            continue
                    else:
                        continue
                # here, s2 is not vertical
                # check the span
                if not( s2[0][0] <= s[0][0] and s[0][0]< s2[1][0] ):
                    #print 'no span'
                    continue
                # now we know the span is good
                # check colin
                if segLibrary.collinear( s, s2 ):
                    #print 'span colin'
                    boundsOtherReg = True
                    continue
                # here they are not colinear.  check if s[0] is on s2
                checkPoint = s[0]
                turnVal =  segLibrary.collinearValue( s2[0], s2[1], checkPoint)
                if checkPoint == s2[0] or (-0.0000001 < turnVal and turnVal < 0.000001):
                    checkPoint  = s[1]
                    turnVal =  segLibrary.collinearValue( s2[0], s2[1], checkPoint)
                    #print 'same endpoint'
                if turnVal > 0:
                    # make sure we only count the seg once.  only count it
                    # if the intersection of a vertical and this one occurs in
                    # the cell.
                    #print 'LHT!'
                    count += 1
            index -= 1
        #print 'count', count
        finalR1Segs.append( (s, count % 2, boundsOtherReg ) )
    return finalR1Segs


def assignCells( r1, cellSize, r1Dict, usedCellSet):
    ''' 
    r1
        list of segments defining regions

    cellSize
        size of a cell
    
    r1Dict
        a dictionay of cell->list of segs. cell is just an x,y.  Segs are ((x1,y1),(x2,y2))

    usedCellsSet
        A set of cell addresses used

    Notes:
        If a segment is placed in 2 adjacent cells in the Y direction, it will
        be placed in the uppermost cell once, and twice in the lower cells.
        This is so the ray shooting test will still work.
    '''

    # first get the bbox of the scene


    # now we know how big each grid cell should be
    # time to put segs in thier place
    # dict is cell to list of seg indexes mapping

    for s in r1:
        # get the cells

        # if the line is steep, switch the x's and y's
        isSteep = abs(s[1][1]-s[0][1] ) > abs( s[1][0]-s[0][0] )
        if not isSteep:
            x0 = s[0][0]
            y0 = s[0][1]
            x1 = s[1][0]
            y1 = s[1][1]
        else:
            x0 = s[0][1]
            y0 = s[0][0]
            x1 = s[1][1]
            y1 = s[1][0]


        # get the starting and ending grids
        startGridX = int (x0 // cellSize)  
        startGridY = int (y0 // cellSize)  
        endGridX = int (x1 // cellSize)  
        endGridY = int (y1 // cellSize)  
        
        #print '----- Assign seg: ', s, 'steep: ', isSteep 
        #print 'start xy end xy: ', startGridX, startGridY, endGridX, endGridY

        # we assume that portions of aline (end points for example) that 
        # are on a cell boundary are pushd *up* a cell.  This cuases 
        # a slight problem in calculations below, so go ahead and 
        # record the *up* cell, and then adjust the cell down

        # if a left Y end point is on a cell boundary and 
        # the segs extends down, record the upper cell, and adust start
        if math.fmod(y0, cellSize) == 0.0 and y0 > y1:
            if isSteep:
                if (startGridY, startGridX) not in r1Dict:
                    r1Dict[ (startGridY, startGridX) ] = list()
                r1Dict[ (startGridY, startGridX) ].append( s )
                usedCellSet |= set( [(startGridY, startGridX)] )
                #print 'added 1', startGridY, startGridX
            else:
                if (startGridX, startGridY) not in r1Dict:
                    r1Dict[ (startGridX, startGridY) ] = list()
                r1Dict[ (startGridX, startGridY) ].append( s )
                usedCellSet |= set( [(startGridX, startGridY)] )
                #print 'added 1', startGridX, startGridY
            startGridY -= 1


        # if the X value of the right end point is on a boundary, record
        # the *up* (in this case *right* ) cell, then adjust end
        if math.fmod(x1, cellSize) == 0:
            if isSteep:
                if (endGridY, endGridX) not in r1Dict:
                    r1Dict[ (endGridY, endGridX) ] = list()
                r1Dict[ (endGridY, endGridX) ].append( s )
                usedCellSet |= set( [(endGridY, endGridX)] )
                #print 'added 2', endGridY, endGridX
            else:
                if (endGridX, endGridY) not in r1Dict:
                    r1Dict[ (endGridX, endGridY) ] = list()
                r1Dict[ (endGridX, endGridY) ].append( s )
                usedCellSet |= set( [(endGridX, endGridY)] )
                #print 'added 2', endGridX, endGridY 
            endGridX -= 1

        # now the main loop. 
       
       
        # !!!! This was an error in the c++ version   !!!!
        # !!!! that resulted in missing intersections !!!!
        # becuase we switch the Xs and Ys for steeps,
        # startGridX might be greater than endGridX
        # The loop below this wants to loop *up*
        # (range(3,1) returns a an empty list!)
        if endGridX < startGridX:
            startGridX, endGridX = endGridX, startGridX
            startGridY, endGridY = endGridY, startGridY 

        # get some numbers to check if extra cells need to be added 
        # so we don't have to worry about rounding so much.
        if y0 == y1:
            error = 0
        else:
            error = (y0 - ((startGridY * cellSize) + (cellSize / 2))) / cellSize
        if x0 == x1:
            slope = 0
        else: 
            slope = (y1 - y0) / (x1 - x0)
        currentY = startGridY
        
        #print 'startx, endx', startGridX, endGridX
        #print 'starty, endy', startGridY, endGridY
        for currentX in xrange( startGridX, endGridX ):
            #print 'currx curry', currentX, currentY
            if isSteep:
                # insert the segment
                if (currentY, currentX) not in r1Dict:
                    r1Dict[ (currentY, currentX) ] = list()
                r1Dict[ (currentY, currentX) ].append( s )
                usedCellSet |= set( [(currentY, currentX)] )
                #print 'added 3', currentY, currentX
                # check if additional cell should be added
                if slope < 0 and error < 0:
                    currentY -= 1
                    if (currentY, currentX) not in r1Dict:
                        r1Dict[ (currentY, currentX) ] = list()
                    r1Dict[ (currentY, currentX) ].append( s )
                    usedCellSet |= set( [(currentY, currentX)] )
                    #print 'added 4', currentY, currentX
                    currentY += 1
                if slope > 0 and error > 0:
                    currentY += 1
                    if (currentY, currentX) not in r1Dict:
                        r1Dict[ (currentY, currentX) ] = list()
                    r1Dict[ (currentY, currentX) ].append( s )
                    usedCellSet |= set( [(currentY, currentX)] )
                    #print 'added 5', currentY, currentX
                    currentY -= 1
            else:
                # same thig but for NOT steeps
                # insert the segment
                if (currentX, currentY) not in r1Dict:
                    r1Dict[ (currentX, currentY) ] = list()
                r1Dict[ (currentX, currentY) ].append( s )
                usedCellSet |= set( [(currentX, currentY)] )
                #print 'added 6', currentX, currentY
                # check if additional cell should be added
                if slope > 0 and error > 0:
                    currentY += 1
                    if (currentX, currentY) not in r1Dict:
                        r1Dict[ (currentX, currentY) ] = list()
                    r1Dict[ (currentX, currentY) ].append( s )
                    usedCellSet |= set( [(currentX, currentY)] )
                    #print 'added 7', currentX, currentY
                    currentY -= 1
                if slope < 0 and error < 0:
                    currentY -= 1
                    if (currentX, currentY) not in r1Dict:
                        r1Dict[ (currentX, currentY) ] = list()
                    r1Dict[ (currentX, currentY) ].append( s )
                    usedCellSet |= set( [(currentX, currentY)] )
                    #print 'added 8', currentX, currentY
                    currentY += 1
            error += slope
            if slope > 0 and error > 0.5:
                # adjust Y up
                error -= 1
                currentY += 1
            elif slope < 0 and error < -0.5:
                error += 1
                currentY -= 1

        # handle the last cell
        if isSteep:
            if (currentY, endGridX) not in r1Dict:
                r1Dict[ (currentY, endGridX) ] = list()
            r1Dict[ (currentY, endGridX) ].append( s )
            usedCellSet |= set( [(currentY, endGridX)] )
            #print 'added 9', currentY, endGridX
        else:
            if (endGridX, currentY) not in r1Dict:
                r1Dict[ (endGridX, currentY) ] = list()
            r1Dict[ (endGridX, currentY) ].append( s )
            usedCellSet |= set( [(endGridX, currentY)] )
            #print 'added 10', endGridX, currentY


        
if __name__ == "__main__":

    
    
    r1 = [((1,2),(5,2)),((1,2),(4,4)),((4,4),(5,2))] 
    r2 = [((1,1),(6,1)),((1,1),(3,5)),((3,5),(6,1))] 
    r1 = [((2,2),(8,3)),((8,3),(8,8)),((8,8),(2,8)),((2,8),(4,4)),((4,4),(2,2))] 
    r2 = [((3,7),(4,5)),((4,5),(8,5)),((8,5),(8,4)),((8,4),(9,4)),((9,4),(8,6)),((8,6),(8,7)),((8,7),(7,8)),((7,8),(5,8)),((5,8),(3,7))] 
    
    r1 = [((1,1),(2,7)),((2,7),(10,1)),((10,1),(1,1))] 
    r2 = [((1,1),(6,1)),((1,1),(3,5)),((3,5),(6,1))] 
    r1 = region.createRegionFromSegs( r1 )
    r2 = region.createRegionFromSegs( r2 )
    #print 'genr1'
    #r1 = region.getRandomRegion( 300 )
    #print 'genr2'
    #r2 = region.getRandomRegion( 300 )
    print 'length of input regions (number of halfsegments)'
    print len( r1 ), ' ', len(r2 )

    print 'inter'
    region.intersection( r1, r2 )
    print 'over'
    overlay( r1, r2, .0001 )

