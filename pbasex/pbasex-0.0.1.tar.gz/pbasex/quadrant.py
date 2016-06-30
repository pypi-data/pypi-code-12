import numpy as np

def foldQuadrant(M, x0=None, y0=None, quadrant_filter=[1,1,1,1]):

	big_int = 99999999
	qsigns = np.array([[-1,1],[-1,-1],[1,-1],[1,1]])
	try:
		sy,sx,sz = M.shape
	except ValueError:
		sy,sx = M.shape
		sz = 1
	if x0 is None:
		x0 = int(sx/2)
	if y0 is None:
		y0 = int(sy/2)
	quadrant_filter = np.array(quadrant_filter)

	lx,ly = big_int, big_int
	if quadrant_filter[1] or quadrant_filter[2]:
		lx = min(lx, x0+1)
	if quadrant_filter[0] or quadrant_filter[3]:
		lx = min(lx, sx-x0)
	if quadrant_filter[0] or quadrant_filter[1]:
		ly = min(ly, y0+1)
	if quadrant_filter[2] or quadrant_filter[3]:
		ly = min(ly, sy-y0)
	if sz>1:
		Mout = np.zeros((ly,lx,sz))
	else:
		Mout = np.zeros((ly,lx))

	for i in range(4):
		if quadrant_filter[i]:
			xf, yf = x0 + qsigns[i,1]*lx, y0 + qsigns[i,0]*ly
			if xf == -1:
				xf = None
			if yf == -1:
				yf = None
			Mout += M[y0:yf:qsigns[i,0], x0:xf:qsigns[i,1]]

	return Mout

def unfoldQuadrant(M):

	return np.vstack((np.hstack((np.rot90(M[1:,1:],2),np.flipud(M[1:,:]))),np.hstack((np.fliplr(M[:,1:]),M))))

def resizeFolded(M, r_max):

	try:
		sy,sx,sz = M.shape
		sz = (sz,)
	except ValueError:
		sy,sx = M.shape
		sz = ()

	if sx>r_max:
		x1, x2 = r_max, 0
	else:
		x1, x2 = sx, r_max-sx
	if sy>r_max:
		y1, y2 = r_max, 0
	else:
		y1, y2 = sy, r_max-sy

	return np.vstack((np.hstack((M[:y1,:x1],np.zeros((y1,x2)+sz))),np.zeros((y2,r_max)+sz)))