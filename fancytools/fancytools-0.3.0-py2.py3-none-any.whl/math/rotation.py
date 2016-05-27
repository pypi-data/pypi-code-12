import numpy as np
import utils


#THESE FUNCTIONS ARE BETTER IMPLEMENTED IN THE PACKAGE:  'transforms3d' within pypi


def rotMatrix2AxisAndAngle(R):
    '''
    http://stackoverflow.com/questions/12463487/obtain-rotation-axis-from-rotation-matrix-and-translation-vector-in-opencv
    
    R : 3x3 rotation matrix
    returns axis, angle
    
    '''
    angle = np.arccos(( R[0,0] + R[1,1] + R[2,2] - 1)/2)
    axis = np.array([
        #x
        (R[2,1] - R[1,2])/utils.sqrt((R[2,1] - R[1,2])**2 +(R[0,2] - R[2,0])**2 + (R[1,0] - R[0,1])**2),
        #y
        (R[0,2] - R[2,0])/utils.sqrt((R[2,1] - R[1,2])**2 +(R[0,2] - R[2,0])**2 + (R[1,0] - R[0,1])**2),
        #z
        (R[1,0] - R[0,1])/utils.sqrt((R[2,1] - R[1,2])**2 +(R[0,2] - R[2,0])**2 + (R[1,0] - R[0,1])**2) ])
    return axis, angle



def axisAndAngle2RotMatrix(axis, angle):
    """
    http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector
    
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by angle radians.
    """
    axis = np.asarray(axis)
    angle = np.asarray(angle)
    axis = axis/utils.sqrt(np.dot(axis, axis))
    a = utils.cos(angle/2)
    b, c, d = -axis*utils.sin(angle/2)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])



def rotVector2Matrix(vec):
    '''
    better use cv2.Rodrigues(rvec)[0] for that job...
    
    the angle is given as the magnitude of the rot vector,
    see https://www.safaribooksonline.com/library/view/learning-opencv/9780596516130/ch11s05.html

    '''
    return axisAndAngle2RotMatrix(vec, np.linalg.norm(vec))


if __name__ == '__main__':
    v = [3, 5, 0]
    axis = np.array([4, 4, 1])
    angle = 1.2 
    
    #transform angle, axis to rotation matrix and back:
    R = axisAndAngle2RotMatrix(axis, angle)
    axis2,angle2 = rotMatrix2AxisAndAngle(R)
    
    #the returned axis it (in opposite to the origin axis normalised, so
    normAxis = axis / np.linalg.norm(axis)

    #the differences after the transformation should be neglectable:
    assert (normAxis - axis2 < 1e-10).all()
    assert (angle - angle2 < 1e-10).all()

    rotVector = normAxis*1.2
    assert (rotVector2Matrix(rotVector) - R < 1e-10).all()

    #rotate a vector:
    #print(np.dot(R, v)) 
