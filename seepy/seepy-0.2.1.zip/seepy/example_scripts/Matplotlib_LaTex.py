#! ##Working with Matplotlib and LaTex
import matplotlib.pyplot as plt
import numpy as np

t = np.arange(-1.0, 2.0, 0.01)

#! ##Fig. 1
s1 = np.cos(9*np.pi*t) + 3 * t ** 2 #%tex
plt.figure(1)
plt.plot(t, s1) #%plt
plt.clf()

#! ##Fig. 2
s2 = np.sin(18*np.pi*t**2) #%tex
plt.figure(2)
plt.plot(t, s2)
plt #%plt
plt.clf()

#! ##Fig. 3
s3 = t**3 #%tex
plt.figure(3)
plt.plot(t, s3)
plt #%plt
plt.clf()

#! ##Fig. 4 - All in one
plt.figure(4)
plt.plot(t, s1)
plt.plot(t, s2)
plt.plot(t, s3)
plt #%plt
plt.clf()

#! You can use LaTex syntax

#%tex A_s = f_d/A_s
#%tex s(t) = \mathcal{A}\mathrm{sin}(2 \omega t)

a = 23
#%tex f(x) = %(a)s * y + 4^3

#%tex 26*i*2 + 4/2^6 kjkjk


