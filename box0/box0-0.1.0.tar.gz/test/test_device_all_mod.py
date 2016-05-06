import box0

dev = box0.usb.open_supported()

mod_type_dict = {
	box0.module.Module.DIO: "DIO",
	box0.module.Module.AOUT: "AOUT",
	box0.module.Module.AIN: "AIN",
	box0.module.Module.SPI: "SPI",
	box0.module.Module.I2C: "I2C",
	box0.module.Module.PWM: "PWM",
	box0.module.Module.UNIO: "UNIO"
}

print("has modules: ")
for m in dev:
	str_type = mod_type_dict.get(m.type, hex(m.type))
	print("'%s' type: %s and index: %i"%(m.name, str_type, m.index))

dev.close()
print("bye bye...")
