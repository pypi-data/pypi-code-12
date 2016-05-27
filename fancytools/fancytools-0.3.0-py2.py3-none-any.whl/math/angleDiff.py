from math import atan2, sin, cos

def  angleDiff(angle1,angle2):
    '''
    smallest difference between 2 angles
    code from http://stackoverflow.com/questions/1878907/the-smallest-difference-between-2-angles
    '''
    return atan2(sin(angle1-angle2), cos(angle1-angle2))