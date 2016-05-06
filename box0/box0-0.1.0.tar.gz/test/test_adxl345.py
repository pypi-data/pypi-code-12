import box0

dev = box0.usb.open_supported()
i2c = dev.i2c()
adxl345 = box0.driver.Adxl345(i2c)

print("READ", adxl345.read())

adxl345.close()
i2c.close()
dev.close()
