import box0
import time
import numpy as np
from pylab import *

SAMPLE_SPEED = 96000.
SAMPLE_COUNT = 500.

dev = box0.usb.open_supported()
ain0 = dev.ain(0)
ain0.static_prepare()

xlabel('time (s)')
ylabel('voltage (V)')
title('About as simple as it gets, folks')
grid(True)

ain0.bitsize.current = 12
ain0.speed.current = int(SAMPLE_SPEED)
s = np.empty(int(SAMPLE_COUNT), dtype=np.float64)
ain0.static_start(s)

t = arange(0.0, SAMPLE_COUNT / SAMPLE_SPEED, 1/SAMPLE_SPEED)
clf()
grid(True)

print("s is" + str(s))
print("t is" + str(t))

#~ fill(t, s, 'r.-')
plot(t, s, 'r.-')

savefig("test.png")

ain0.close()
dev.close()

show()
