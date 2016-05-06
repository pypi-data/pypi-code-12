import box0
import time
import numpy as np

CURRENT_THRESHOLD = 5.0

# sensor constants (HK050) - 500A
# Input/Output: 30A/15mA
# Design: Resistance of 1K and offset of 1.5V

# open the resources
dev = box0.usb.open_supported()
ain = dev.ain(0)

# prepare+start stream
stream = ain.stream.search(96000, 12)
samples_count = stream.speed / 2 # accumlate for 500ms
ain.stream_prepare(stream)
ain.stream_start()

# block till user do not kill
try:
	values = np.empty(samples_count)
	while True:
		ain.stream_read(values)

		# formula: (value * 20) - 30
		values = (values * 20.0) - 30.0

		#seen a serge?
		surge = max(abs(values.max()), abs(values.min()))
		if surge > CURRENT_THRESHOLD:
			print("got a surge! (peak: %f A)" % surge)

except:
	pass
finally:
	print("exited loop")

# stop stream
ain.stream_stop()

# close the resources
ain.close()
dev.close()
