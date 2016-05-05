import spidev


def test_bus(bus=0, device=0):
    spi = spidev.SpiDev()
    spi.open(bus, device)


spi=spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=100000
channel_select=[0x01, 0x80, 0x00]
if __name__=='__main__':
    print('welcome to the slide pot reader')
    try:
        while True:
            adc_data=spi.xfer(channel_select)
            adc=((adc_data[1]<<8)&0x300)|(adc_data[2]&0xFF)
            print(adc)
    except KeyboardInterrupt:
        print('CTRL-C, Exiting')