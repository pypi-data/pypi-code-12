import box0
import time
import sys
from box0.driver import Ads1220

gain = Ads1220.GAIN_1

# get the gain
if len(sys.argv) > 1:
	gain = Ads1220.__dict__['GAIN_' + sys.argv[1]]
	print("chosen gain: %s" % sys.argv[1])

dev = box0.usb.open_supported()
spi0 = dev.spi(0)
ads1220 = box0.driver.Ads1220(spi0, 0)

ads1220.gain = gain

try:
	print("Values:")
	while True:
		ads1220.start()
		time.sleep(0.05)
		print(ads1220.read())
except KeyboardInterrupt:
	pass

ads1220.close()
spi0.close()
dev.close()
