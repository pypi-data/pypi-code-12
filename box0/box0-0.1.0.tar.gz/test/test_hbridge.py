import box0
import time

dev = box0.usb.open_supported()
dio = dev.dio()
hbridge = box0.driver.HBridge(dio)

print("disable")
hbridge.disable()
time.sleep(1)

print("forward")
hbridge.forward()
time.sleep(1)

print("backward")
hbridge.backward()
time.sleep(1)

hbridge.close()
dio.close()
dev.close()
