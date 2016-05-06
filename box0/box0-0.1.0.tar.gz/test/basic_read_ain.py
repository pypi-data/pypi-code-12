import box0
import sys
import numpy as np

dev = box0.usb.open_supported()
ain0 = dev.ain(0)

print("label")
i = 0
for l in ain0.label.values:
	print(str(i) + l)
	i += 1

print("reference")
print("  high: %.3f" % ain0.ref.high)
print("  low: %.3f" % ain0.ref.low)

print("bitsize")
for b in ain0.bitsize.values: print(str(b))

print("count %i"%ain0.count.value)

ain0.static_prepare()

ain0.speed.current = 100
ain0.bitsize.current = 12
data = np.empty(10, dtype=np.float64)
ain0.static_start(data)
print(data)

ain0.close()
dev.close()
