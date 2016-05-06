import time
import box0
import numpy as np

dev = box0.usb.open_supported()
ain = dev.ain(0)
aout = dev.aout(0)

ain_stream = ain.stream.search(96000, 12)
aout_stream = aout.stream.search(96000, 12)

ain.stream_prepare(ain_stream)
aout.stream_prepare(aout_stream)

ain.stream_start()
time.sleep(.2) # some delay in between
aout.stream_start()

try:
	count = ain_stream.speed / 10
	data = np.empty(count)
	while(True):
		ain.stream_read(data)
		aout.stream_write(data)
except:
	# no problem
	pass

ain.stream_stop()
aout.stream_stop()

ain.close()
aout.close()
dev.close()
