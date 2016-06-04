#                             if found:
#                                 break

                        #didn't find connected neighbour:
                        #search in local kernel for biggest moment to neighbour
#                         if not found and search_kernel_size:# and pos>= minimum_cluster_size:
#                             mi = 0.0
#                             mj = 0.0
#                             for ii in xrange(max(0,i-hk),min(gx,i+hk+1)):
#                                 for jj in xrange(max(0,j-hk),min(gy,j+hk+1)):
#                                     if img[ii,jj]:
#                                         dist = ((ii-i)**2 + (jj-j)**2 )**0.5
#                                         mi += (ii-i) / dist
#                                         mj += (jj-j) / dist
#                             dist = (mi**2 + mj**2)**0.5
#                             if dist >  min_m:
#                                 #go into direction of biggest moment
#                                 #try to find first non-zero pixel in the way
#                                 di = mi/dist
#                                 dj = mj/dist
#                                 f_i = float(i)
#                                 f_j = float(j)
#                                 i_first = abs(di) > abs(dj)
#                                 
#                                 for _ in xrange(k*2):
#                                     f_i += di
#                                     i2 = int(round(f_i))
#                                     f_j += dj
#                                     j2 = int(round(f_j))
#                                     if i_first:
#                                         if img[i2,j]:
#                                             i = i2
#                                             found = True
#                                             img[i,j]=0
#                                             break
#                                         if img[i,j2]:
#                                             i = i2
#                                             found = True
#                                             img[i,j]=0
#                                             break
#                                     else:
#                                         if img[i,j2]:
#                                             i = i2
#                                             found = True
#                                             img[i,j]=0
#                                             break
#                                         if img[i2,j]:
#                                             i = i2
#                                             found = True
#                                             img[i,j]=0
#                                             break
#                                     if img[i2,j2]:
#                                         i = i2
#                                         j = j2
#                                         found = True
#                                         img[i,j]=0
#                                         break