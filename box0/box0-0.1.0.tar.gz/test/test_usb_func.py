import box0

dev = box0.usb.open_supported()
ain = dev.ain()
aout = dev.aout()

box0.usb.aout_iso_pending(aout, 16)
print("aout_iso_pending: OK")

box0.usb.aout_iso_test(aout, True)
print("aout_iso_test: OK")

box0.usb.ain_iso_delay(ain, 30)
print("ain_iso_delay: OK")

box0.usb.ain_iso_test(ain, True)
print("ain_iso_test: OK")

box0.usb.device_ctrlreq_timeout(dev, 100)
print("device_ctrlreq_timeout: OK")

box0.usb.device_bulk_timeout(dev, 100)
print("device_bulk_timeout: OK")

print("libusb_device_handle: ", box0.usb.libusb_device_handle(dev))
print("libusb_device: ", box0.usb.libusb_device(dev))
print("libusb_context: ", box0.usb.libusb_context(dev))

ain.close()
aout.close()
dev.close()
