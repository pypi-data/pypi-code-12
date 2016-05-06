import box0
import sys
import time
import numpy as np

dev = box0.usb.open_supported()
ain0 = dev.ain(0)

stream_value = ain0.stream.search(125, 12)
if stream_value is None:
	print("no stream_value found")
	sys.exit(0)

print("bitsize: %i" % stream_value.bitsize)
print("speed: %i" % stream_value.speed)

ain0.stream_prepare(stream_value)
ain0.stream_start()

try:
	arr = np.empty(stream_value.speed / 10) # 100ms data
	while True:
		ain0.stream_read(arr)
		print(str(arr))
except:
	print("exiting...")

ain0.stream_stop()
ain0.close()
dev.close()
