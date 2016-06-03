# -*- coding: utf-8 -*-
import cv2
import numpy as np


from fancytools.math.line import intersection
from fancytools.math.pointInsidePolygon import pointInsidePolygon

#own
from imgProcessor.imgIO import imread
from imgProcessor.genericCameraMatrix import genericCameraMatrix
from imgProcessor.sortCorners import sortCorners



class ObjectNotFound(Exception):
    pass



class QuadDetection(object):
    ''' 
    Automatic perspective correction for quadrilateral objects. See the tutorial at
    http://opencv-code.com/tutorials/automatic-perspective-correction-for-quadrilateral-objects/
  
    '''
    def __init__(self, img, cameraMatrix=None, distCoeffs=None):
        self.transformationMatrix = None 
        
        self.img  = imread(img, 'gray', dtype=np.uint8)
        self.edges = cv2.blur(self.img, (5, 5) )
        self.edges = cv2.Canny(self.edges, 100, 100, 3)

        #CAMERAMATRIX
        if cameraMatrix is None:
            s = img.shape
            if len(s) == 3:
                s = s[:-1]
            (height, width) = s
            cameraMatrix = genericCameraMatrix((height, width))  
        self.cameraMatrix = cameraMatrix
        
        #DISTORITON COEFFS
        if distCoeffs is None:
            distCoeffs = np.zeros(shape=5)
        self.distCoeffs = distCoeffs


    @staticmethod    
    def _computeIntersect(a,b):
        x1 = a[0]
        y1 = a[1]
        x2 = a[2]
        y2 = a[3]
        x3 = b[0]
        y3 = b[1]
        x4 = b[2]
        y4 = b[3]
        d = float(((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        if  d :
            return [(((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d),
                    (((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d) ]
        return [-1.0, -1.0]  


    def findLines(self,threshold=50, minLineLength=None, maxLineGap=None):
        s = self.img.shape
        if minLineLength is None:
            minLineLength = int(s[0]*0.15)
        if maxLineGap is None:
            maxLineGap=int(s[0]*0.015)
        #get lines from bw-image
        out = cv2.HoughLinesP(self.edges, 1, np.pi/180, threshold=threshold, 
                              minLineLength=minLineLength, maxLineGap=maxLineGap)
        if out is not None:
            self.lines = out[0]
        else:
            self.lines = []
        return self.lines


    @staticmethod    
    def _cuttingAngle(l1, l2):
        #http://de.wikipedia.org/wiki/Schnittwinkel_(Geometrie)
        if l1[3] == l1[1]:
            m1 = 1e5
        else:
            m1 = (l1[2] - l1[0]) / (l1[3] - float(l1[1]))
        if l2[3] == l2[1]:
            m2 = 1e5
        else:
            m2 = (l2[2] - l2[0]) / (l2[3] - float(l2[1]))
        a = np.arctan(abs( (m1-m2) / (1 + m1*m2)))
        #if a > np.pi/2:
        #    a = np.pi - a
        return a


    def _lineDistance(self, l1, l2):
        #line middle
        m1x = (l1[0] + l1[2]) / 2
        m1y = (l1[1] + l1[3]) / 2
        m2x = (l2[0] + l2[2]) / 2
        m2y = (l2[1] + l2[3]) / 2
        dx = m2x - m1x
        dy = m2y - m1y
        return (dx**2 + dy**2)**0.5


    def findQuads(self, relDistObjOutsideImg=0.2, maxScewAngleDeg=35, minLength=20, 
                  criterion='closest', quadOnFoundLine=True):
        '''
        criterion = ['furthest', 'closest', 'all']
        quadOnFoundLine = True/False ... whether a build line must lie on a found line
                            set to false is an extension of a line is ok
        minLength = minimum side length of all sides of a quad
        maxScewAngleDeg = max error angle for parallel and normal lines
                          set to 0 to only detect rectangles
        relDistObjOutsideImg = relative amount of a detected quad to be outside the image
                               set to 0 to only detect quads inside the image
        '''
        halfpi = np.pi*0.5
        l = len(self.lines)
        s = self.img.shape
        #max angle between parallel lines:
        if maxScewAngleDeg >45:
            maxScewAngleDeg = 45
        maxScewAngle = maxScewAngleDeg * np.pi / 180
        #OBJECT BORDER
        xmax = int(s[0]*(1+relDistObjOutsideImg))
        xmin = int(-s[0]*relDistObjOutsideImg)
        ymax = int(s[1]*(1+relDistObjOutsideImg))
        ymin = int(-s[1]*relDistObjOutsideImg)
        #ARRAYS
        intersections = np.zeros(shape=(l,l,2), dtype=int)
        parallels = np.zeros(shape=(l,l), dtype=bool)
        normals = np.zeros(shape=(l,l), dtype=bool)
        distances  = np.zeros(shape=(l,l), dtype=int)

        def parallelsSortedInDistanceTo(line):
            #all lines that are parallel to line
            pList = np.where(parallels[line])[0]
            #sort all found parallels by its distance to line
            distToLine = [distances[n1,p] for p in pList]
            pList = self._sortBy(pList, distToLine)
            return pList 

        def parallelsSortedInDistanceToReverse(line):
            pList = parallelsSortedInDistanceTo(line)
            pList.reverse()
            return pList
        
        #as soon as 2 parallels are found for 2 normals 
        # and the build quad is valid: continue with next 2 normals 
        breakAfterFirstQuad = True
        
        if criterion == 'all':
            breakAfterFirstQuad = False
            # return all lines parallel to a given line
            getParallels = lambda line: np.where(parallels[line])[0]
        elif criterion == 'closest':
            getParallels = parallelsSortedInDistanceTo
        else: #'furthest'
            getParallels = parallelsSortedInDistanceToReverse
            
        #FILL ARRAYS
        ll = 1 
        for n in xrange(l):
            # fill arrays like a triangular matrix
            # save time because cutting angle and intersections
            # are the same for array[line1,line2] and array[line2,line1]
            for m in xrange(ll):
                if n == m: #same line
                    break
                l1,l2 = self.lines[n],self.lines[m]

                d = self._lineDistance(l1,l2)
                if d < minLength:
                    break
                distances[n,m] = d
                distances[m,n] = d

                #could lines be parallel or normal to each other?
                cutAngle = self._cuttingAngle(l1,l2)
                #print cutAngle * 180 / np.pi
                #PARALLEL
                if -maxScewAngle < cutAngle < maxScewAngle:
                    parallels[n,m] = True
                    parallels[m,n] = True
                    #print n,m,111
                #NORMAL
                elif  halfpi-maxScewAngle < cutAngle < maxScewAngle+halfpi:

                    i = self._computeIntersect(l1, l2)
                    #AND INSIDE BORDER
                    if (xmin < i[0] < xmax) and (ymin < i[1] < ymax):
                        #fill both possible positions:
                        intersections[n,m] = i
                        intersections[m,n] = i
                        normals[n,m] = True
            ll += 1
        #CREATE QUADS
        self.quads = []#[point1(x,y),...,point4(x,y)]
        self.quadLines = {}#id(quad):[lineindex1,,,lineindex4]
        # get lines that are normal to each other:
        for (n1,n2) in np.transpose(np.where(normals)):
            foundQuad = False
            #find to those 2 line 2 other that are parallel
            #stop as soon as a quad built by those parallels 
            # fulfils the criteria
            
            #scan all other lines that are parallel to n1 and n2
            allPallallelsToN2 = getParallels(n2)
            for p1 in getParallels(n1):
                for p2 in allPallallelsToN2:
                    if p1 == p2:
                        #same line
                        break
                    
                    corners=[intersections[n1,n2]]
                    for i,j in ((n1,p2), (p2,p1), (p1,n2)):
                        #CHECK: intersection valid?
                        pn = intersections[i,j]
                        if sum(pn)==0:
                            #intersections are outside the valid area
                            corners = None
                            break
                        corners.append(pn) 
                        
                    if corners is None:
                        break

                    for i, j in zip(range(-1,3), (n2,n1,p2,p1)):
                        #CHECK: is orig line on the newly built line?
                        if quadOnFoundLine:
                            (lx1,ly1,lx2,ly2) = self.lines[j]
                            mx = (lx1 + lx2) / 2
                            my = (ly1 + ly2) / 2
                            (cx1,cy1) = corners[i]
                            (cx2,cy2) = corners[i+1]
                            #middle point of given line must be in range of the created one
                            if not ( min(cx1,cx2)<= mx <= max(cx1,cx2) and
                                min(cy1,cy2)<= my <= max(cy1,cy2)):
                                corners = None
                                break
                        #CHECK: MIN EDGE LENGTH
                        if minLength > 0:
                            v = corners[i]-corners[i+1]
                            length = np.sqrt(v.dot(v))
                            if length < minLength:
                                corners = None
                                break
                            
                    if corners is not None:
                        quad = sortCorners(corners)
                        self.quads.append(quad)
                        self.quadLines[id(quad)] = (n1,n2,p1,p2)
                        foundQuad = True
                    if foundQuad and breakAfterFirstQuad:
                        break
                if foundQuad and breakAfterFirstQuad:
                    break


    def _quadArea(self, quad):
        #http://de.wikipedia.org/wiki/Viereck
        e = quad[0]-quad[2]
        length_e = np.sqrt(e.dot(e))
        f = quad[1]-quad[3]
        length_f = np.sqrt(f.dot(f))
        m1 = e[1]/e[0]
        m2 = f[1]/f[0]
        theta = np.arctan(abs( (m1-m2) / (1 + m1*m2)))
        return 0.5*length_e*length_f*np.sin(theta)


    @staticmethod
    def _sortBy(l, criteria):
        '''
        sort a list with the help of a given sortable list, like distances
        '''
        sort_index = np.argsort(criteria)
        out = []
        for i in sort_index:
            out.append(l[i])
        return out
        

    def filterQuads(self, criterion='biggest', maxQuads=5):
        '''
        criterion = 'biggest' OR 'smallest' <- sort quad list beginning with the biggest ones
        criterion = 'noQuadsInside' <- remove quads that have other quads inside
        criterion = 'noLinesInside' <- remove quads that have other lines inside
        criterion = 'centerOfGravity' <- sorting quads starting with those who
                                         have the closest center of gravity compared
                                         to one built by the 4 orig. quad lines
        criterion = 'lineLength' <- compare length of real and created lines
                                 
        '''
        #TODO: update quadLines when removing from self.quads
        #todo: throw fitting crit in findQuads out - because it can be now applied
        if criterion == 'lineLength':
            relDiff = []
            for q in self.quads:
                quadLength = 0
                for i in range(-1,3):
                    qi = q[i] - q[i+1]
                    quadLength += (qi[0]**2+qi[1]**2)**0.5
                #get to orig lines use dto build the quad
                lines = map(self.lines.__getitem__, self.quadLines[id(q)])
                lineLength  = 0
                for l in lines:
                    dx = l[2]-l[0]
                    dy = l[3]-l[1]
                    lineLength += (dx**2+dy**2)**0.5
                relDiff.append(abs(quadLength-lineLength) / lineLength)#((quadLength+lineLength)/2))    
            self.quads = self._sortBy(self.quads, relDiff)

        elif criterion == 'centerOfGravity':
            removeable = []
            distances = []
            for q in self.quads:
                c1 = sum(q)/4
                #get all lines used to build the quad:
                l = map(self.lines.__getitem__, self.quadLines[id(q)])
                #average to one line
                l = np.sum(l,axis=0)/4
                #middle point of this line is the center of gravity:            
                c2 = [ (l[0]+l[1])/2, (l[2]+l[3])/2 ]
                #distance vector of the 2 centers of gravity:
                d = c1-c2
                distances.append(( d[0]**2 + d[1]**2 )**0.5)
            self.quads = self._sortBy(self.quads, distances)
 
        elif criterion == 'noLinesInside':
            removeable = []    
            for n,q in enumerate(self.quads):
                remove = False
                for m,l in enumerate(self.lines):
                    if m in self.quadLines[id(q)]:
                        #this line belongs to the quad itself
                        continue
                    #TEST whether quad lines intersect with line
                    for i in range(-1,3):
                        if intersection( (q[i,0],q[i,1],q[i+1,0],q[i+1,0]), 
                                          l ) :
                            remove = True 
                            break 
                    if not remove:
                        #TEST: it is still possible that the line is inside the quad
                        remove = pointInsidePolygon(l[0],l[1], q)
                    if remove:
                        break
                if remove:
                    removeable.append(n)
            removeable.reverse()
            for n in removeable:
                self.quads.pop(n)
  
        elif criterion == 'noQuadsInside': 
            removeable = []    
            for n,q1 in enumerate(self.quads):
                kickIt = False
                for m,q2 in enumerate(self.quads):
                    if n == m:
                        break
                    for corner in q2:       
                        #as soon as a corner of another quad is inside the tested quad:
                        #remove it      
                        if self._pointInsidePolygon(corner[0],corner[1], q1):
                            kickIt=True
                            removeable.append(n)
                            break
                    if kickIt:
                        break
            removeable.reverse()
            for n in removeable:
                self.quads.pop(n)
            
        elif criterion in ('biggest', 'smallest'):
            areas = [self._quadArea(q) for q in self.quads]
            self.quads = self._sortBy(self.quads, areas)
            if criterion == 'biggest':
                self.quads.reverse()
        else:
            raise Exception('criterion %s not known' %criterion)
        
        self.quads = self.quads[:maxQuads]           


    def drawLines(self, img=None, thickness=4, color=None):
        if img is None:
            img = self.img 
        if color is None:
            if img.ndim == 3:
                color = cv2.cv.CV_RGB(0,255,0)
            else:
                color = 255
        for line in self.lines:
            cv2.line(img, tuple(line[:2]), tuple(line[2:]), color, thickness=thickness)  


    def drawQuads(self, img=None, thickness=4):
        if img is None:
            img = self.img 
        for quad in self.quads:
            #Draw quad lines
            for i in range(-1,3):
                cv2.line(img, tuple(quad[i]), tuple(quad[i+1]), cv2.cv.CV_RGB(255,00,0), thickness=thickness)  
            # Draw corner points
            cv2.circle(img, tuple(quad[0]), 3, cv2.cv.CV_RGB(255,0,0), thickness=thickness)
            cv2.circle(img, tuple(quad[1]), 3, cv2.cv.CV_RGB(0,255,0), thickness=thickness)
            cv2.circle(img, tuple(quad[2]), 3, cv2.cv.CV_RGB(0,0,255), thickness=thickness)
            cv2.circle(img, tuple(quad[3]), 3, cv2.cv.CV_RGB(255,255,255), thickness=thickness)


    def _calcQuadCenter(self, quad):
        return (0.25*sum(quad)).astype(int)


    def findQuadDefault(self, findops={'criterion':'closest', 'maxScewAngleDeg':25}, 
                        filteropts={'criterion':'lineLength', 'maxQuads':1}):
        #self.prepareImg()
        self.findLines()
        self.findQuads(**findops)
        self.filterQuads(**filteropts)#'noLinesInside')#'noQuadsInside', maxQuads=5)
        try:
            return self.quads[0]
        except IndexError:
            raise ObjectNotFound()


   
if __name__ == '__main__':

    def demo(frame):
        q=QuadDetection(frame)
        q.findLines()
        q.findQuads(criterion='closest', maxScewAngleDeg=25)
        q.filterQuads(criterion='lineLength', maxQuads=1)
    
        if q.quads:
            try:
                warped = q.warpPerspective()
                cv2.imshow("warped", warped)
                cv2.waitKey(20) 
            except:
                pass
        q.drawLines(frame)
        q.drawQuads(frame)

        cv2.imshow("result", frame)
        cv2.waitKey(20)


    cv2.namedWindow("result")
    vc = cv2.VideoCapture(-1)
    rval= vc.isOpened()# try to get the first frame
    while rval:
        rval, frame = vc.read()
        demo(frame)
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break

