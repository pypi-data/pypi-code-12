
#     #TODO: REMOOOOVE
#     @staticmethod
#     def _findParamForDistort(R,f, A1,A2, w,h):
#         from scipy.optimize import fsolve
#         ###find dx, dy as 
#         dx,dy=0,0
#         #find the right focal length to fit the whole scene:
#         def solveIterative(x):
#             dz = x[0]
# 
#             T = np.array([
#                 [1, 0, 0, dx],
#                 [0, 1, 0, dy],
#                 [0, 0, 1, dz],
#                 [0, 0, 0, 1]])
# 
#             #Final and overall transformation matrix
#             t = np.linalg.inv(A2.dot(T.dot(R.dot(A1))))
#             
#             #both should be zero:
#             x0 = t[0,2]/t[2,2]
#             y0 = t[1,2]/t[2,2]
#             #both should be image.shape:
#             x1 = (t[0,0]*w+t[0,1]*h+t[0,2])/(t[2,0]*w+t[2,1]*h+t[2,2])
#             y1 = (t[1,0]*w+t[1,1]*h+t[1,2])/(t[2,0]*w+t[2,1]*h+t[2,2])
# 
#             if x0>0:
#                 x0*=0.9
#             if y0>0:
#                 y0*=0.9
#             if x1<w:
#                 x1*=0.9
#             if y1<h:
#                 y1*=0.9
#             res = abs(x0) + abs(y0) + abs(x1-w) + abs(y1-h)
#             print '      ' , res
#             return res#, res, res
#         m= fsolve(solveIterative, 
#                     (w),factor=0.1 
#                    # bounds=( (1,None),(0,None), (0,None)  )
#                       )
#         return dx,dy,m[0]



# 
#     def distort2(self, fit=False, rotX=0, rotY=0, rotZ=0, 
#                 dx=0,dy=0,dz=10000):
#         #DOESNT WORK
#         '''
#         rotation angles in DEGREE
#         
#         translating c++ post http://stackoverflow.com/questions/6606891/opencv-virtually-camera-rotating-translating-for-birds-eye-view/6667784#6667784
#         '''
#         alpha = rotX/180.0*np.pi
#         beta = rotY/180.0*np.pi
#         gamma = rotZ/180.0*np.pi
#         
#         f = self.opts['cameraMatrix'][0,0]
# 
#         taille = self.img.shape
#         h,w = taille
#         #Projection 2D -> 3D matrix
#         A1 = np.array([
#             [1, 0, -w/2],
#             [0, 1, -h/2],
#             [0, 0,    0],
#             [0, 0,    1]])
#         #Rotation matrices around the X,Y,Z axis
#         RX = np.array([
#             [1, 0, 0, 0],
#             [0, np.cos(alpha), -np.sin(alpha), 0],
#             [0, np.sin(alpha),  np.cos(alpha), 0],
#             [0, 0, 0, 1]])
#         RY = np.array([
#             [np.cos(beta), 0, -np.sin(beta), 0],
#             [0, 1,         0, 0],
#             [np.sin(beta), 0,  np.cos(beta), 0],
#             [0, 0,          0, 1]])
#         RZ = np.array([
#             [np.cos(gamma), -np.sin(gamma), 0, 0],
#             [np.sin(gamma),  np.cos(gamma), 0, 0],
#             [0,          0,           1, 0],
#             [0,          0,           0, 1]])
#         #Composed rotation matrix with (RX,RY,RZ)
#         R = RX.dot(RY).dot(RZ)
# 
#         #Camera Intrisics matrix 3D -> 2D
#         A2 = np.array([
#             [f, 0, w/2, 0],
#             [0, f, h/2, 0],
#             [0, 0,   1, 0]])
#         
#         if fit:
#             dx,dy,dz = self._findParamForDistort(R,f, A1,A2, w,h)
#         #Translation matrix on the Z axis change dist will change the height
#         T = np.array([
#             [1, 0, 0, dx],
#             [0, 1, 0, dy],
#             [0, 0, 1, dz],
#             [0, 0, 0, 1]])
# 
#         #Final and overall transformation matrix
#         transfo = A2.dot(T.dot(R.dot(A1)))
#         #Apply matrix transformation
#         return cv2.warpPerspective(self.img, transfo, taille[::-1], flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)



      
#     #TODO:remove?
#     def _poseFromHomography2(self):
#         '''
#         GIVES DIFFERENT RESULTS FROM QUAD POSE - REMOVE?
#         
#         get H from ref image
#         get tvec, rvec from H matrix
#         code origin from http://stackoverflow.com/questions/8927771/computing-camera-pose-with-homography-matrix-based-on-4-coplanar-points
#         '''
# 
#         H = self.homography
#         H1 = H[:, 0]
#         H2 = H[:, 1]
#         H3 = np.cross(H1, H2)
#     
#         norm1 = np.linalg.norm(H1)
#         norm2 = np.linalg.norm(H1)
#         tnorm = (norm1 + norm2) / 2.0;
#     
#         self.tvec = H[:, 2] / tnorm
#         self.rvec = cv2.Rodrigues(np.mat([H1, H2, H3]))[0]



#     #TODO: remove?!
#     @staticmethod
#     def _stretchFactors(corners, imgShape):
#         '''
#         return the stretch factors=img.shape/quad_length
#         '''
#         c = corners
#         ll = PerspectiveCorrection._linelength
#         x = np.linspace( imgShape[1] / ll((c[0], c[1])) , 
#                          imgShape[1] / ll((c[2], c[3])) , imgShape[0] )
#         
#         y = np.linspace( imgShape[0] / ll((c[0], c[3])) ,
#                          imgShape[0] / ll((c[1], c[2])) , imgShape[1] )
#         x = x.reshape(imgShape[0],1) 
#         return x,y