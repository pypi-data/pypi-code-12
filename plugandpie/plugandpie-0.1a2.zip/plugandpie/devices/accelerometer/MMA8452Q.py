from plugandpie.common.utils import twos_complement
from plugandpie.devices.accelerometer.Accelerometer import Accelerometer
from plugandpie.interfaces.SMBus import SMBusInterface, SMBusRegister

DEFAULT_I2C_BUS = 1
DEFAULT_I2C_ADDRESS = 0x1d

# CTRL_REG1 Register (Read/Write)
# +------------+------------+-------+-------+------+--------+--------+--------+
# | bit 7      | bit 6      | bit 5 | bit 4 | bit 3| bit 2  | bit 1  | bit 0  |
# +------------+------------+-------+-------+------+--------+--------+--------+
# | ASLP_RATE1 | ASLP_RATE0 | DR2   | DR1   | DR0  | LNOISE | F_READ | ACTIVE |
# +------------+------------+-------+-------+------+--------+--------+--------+
CTRL_REG1_SET_ACTIVE = 0x01
# DR2 DR1 DR0
CTRL_REG1_ODR_800 = 1 << 3  # period = 1.25 ms
CTRL_REG1_ODR_400 = 2 << 3  # period = 2.5 ms
CTRL_REG1_ODR_200 = 3 << 3  # period = 5 ms
CTRL_REG1_ODR_100 = 4 << 3  # period = 10 ms
CTRL_REG1_ODR_50 = 5 << 3  # period = 20 ms
CTRL_REG1_ODR_12_5 = 6 << 3  # period = 80 ms
CTRL_REG1_ODR_6_25 = 7 << 3  # period = 160 ms
CTRL_REG1_ODR_1_56 = 8 << 3  # period = 640 ms

# XYZ_DATA_CFG (Read/Write)
# +-------+-------+-------+---------+-------+-------+-------+-------+
# | bit 7 | bit 6 | bit 5 | bit 4   | bit 3 | bit 2 | bit 1 | bit 0 |
# +-------+-------+-------+---------+-------+-------+-------+-------+
# | 0     | 0     | 0     | HPF_OUT | 0     | 0     | FS1   | FS0   |
# +-------+-------+-------+---------+-------+-------+-------+-------+
XYZ_DATA_CFG_FSR_2G = 0x00
XYZ_DATA_CFG_FSR_4G = 0x01
XYZ_DATA_CFG_FSR_8G = 0x02


class MMA8452Q(Accelerometer):
    def __init__(self, i2c_bus=DEFAULT_I2C_BUS, i2c_address=DEFAULT_I2C_ADDRESS, gravity=9.80665):
        super().__init__(SMBusInterface(i2c_bus))
        self.i2c_address = i2c_address
        self.gravity = gravity
        # registers
        self.STATUS = SMBusRegister(self.interface, i2c_address, 0x00)
        self.OUT_X_MSB = SMBusRegister(self.interface, i2c_address, 0x01)
        self.OUT_X_LSB = SMBusRegister(self.interface, i2c_address, 0x02)
        self.OUT_Y_MSB = SMBusRegister(self.interface, i2c_address, 0x03)
        self.OUT_Y_LSB = SMBusRegister(self.interface, i2c_address, 0x04)
        self.OUT_Z_MSB = SMBusRegister(self.interface, i2c_address, 0x05)
        self.OUT_Z_LSB = SMBusRegister(self.interface, i2c_address, 0x06)
        self.SYSMOD = SMBusRegister(self.interface, i2c_address, 0x0B)
        self.INT_SOURCE = SMBusRegister(self.interface, i2c_address, 0x0C)
        self.WHO_AM_I = SMBusRegister(self.interface, i2c_address, 0x0D)
        self.XYZ_DATA_CFG = SMBusRegister(self.interface, i2c_address, 0x0E)
        self.HP_FILTER_CUTOFF = SMBusRegister(self.interface, i2c_address, 0x0F)
        self.PL_STATUS = SMBusRegister(self.interface, i2c_address, 0x10)
        self.PL_CFG = SMBusRegister(self.interface, i2c_address, 0x11)
        self.PL_COUNT = SMBusRegister(self.interface, i2c_address, 0x12)
        self.PL_BF_ZCOMP = SMBusRegister(self.interface, i2c_address, 0x13)
        self.P_L_THS_REG = SMBusRegister(self.interface, i2c_address, 0x14)
        self.FF_MT_CFG = SMBusRegister(self.interface, i2c_address, 0x15)
        self.FF_MT_SRC1 = SMBusRegister(self.interface, i2c_address, 0x16)
        self.FF_MT_SRC2 = SMBusRegister(self.interface, i2c_address, 0x17)
        self.FF_MT_COUNT = SMBusRegister(self.interface, i2c_address, 0x18)
        self.TRANSIENT_CFG = SMBusRegister(self.interface, i2c_address, 0x1D)
        self.TRANSIENT_THS = SMBusRegister(self.interface, i2c_address, 0x1F)
        self.TRANSIENT_COUNT = SMBusRegister(self.interface, i2c_address, 0x20)
        self.PULSE_CFG = SMBusRegister(self.interface, i2c_address, 0x21)
        self.PULSE_SRC = SMBusRegister(self.interface, i2c_address, 0x22)
        self.PULSE_THSX = SMBusRegister(self.interface, i2c_address, 0x23)
        self.PULSE_THSY = SMBusRegister(self.interface, i2c_address, 0x24)
        self.PULSE_THSZ = SMBusRegister(self.interface, i2c_address, 0x25)
        self.PULSE_TMLT = SMBusRegister(self.interface, i2c_address, 0x26)
        self.PULSE_LTCY = SMBusRegister(self.interface, i2c_address, 0x27)
        self.PULSE_WIND = SMBusRegister(self.interface, i2c_address, 0x28)
        self.ASLP_COUNT = SMBusRegister(self.interface, i2c_address, 0x29)
        self.CTRL_REG1 = SMBusRegister(self.interface, i2c_address, 0x2A)
        self.CTRL_REG2 = SMBusRegister(self.interface, i2c_address, 0x2B)
        self.CTRL_REG3 = SMBusRegister(self.interface, i2c_address, 0x2C)
        self.CTRL_REG4 = SMBusRegister(self.interface, i2c_address, 0x2D)
        self.CTRL_REG5 = SMBusRegister(self.interface, i2c_address, 0x2E)
        self.OFF_X = SMBusRegister(self.interface, i2c_address, 0x2F)
        self.OFF_Y = SMBusRegister(self.interface, i2c_address, 0x30)
        self.OFF_Z = SMBusRegister(self.interface, i2c_address, 0x31)
        self.init()

    def init(self):
        self.standby()
        self.set_output_data_rate(800)  # Hz
        self.set_g_range(2)
        self.activate()

    def reset(self):
        self.CTRL_REG1.set(0)

    def activate(self):
        self.CTRL_REG1.set(self.CTRL_REG1.get(cached=True) | CTRL_REG1_SET_ACTIVE)

    def standby(self):
        self.CTRL_REG1.set(self.CTRL_REG1.get(cached=True) & ~CTRL_REG1_SET_ACTIVE)

    def set_g_range(self, g_range):
        g_ranges = {2: XYZ_DATA_CFG_FSR_2G,
                    4: XYZ_DATA_CFG_FSR_4G,
                    8: XYZ_DATA_CFG_FSR_8G}
        self.XYZ_DATA_CFG.set(self.XYZ_DATA_CFG.get(cached=True) & 0b11111100 | g_ranges[g_range])

    def set_output_data_rate(self, output_data_rate):
        output_data_rates = {800: CTRL_REG1_ODR_800,
                             400: CTRL_REG1_ODR_400,
                             200: CTRL_REG1_ODR_200,
                             100: CTRL_REG1_ODR_100,
                             50: CTRL_REG1_ODR_50,
                             12.5: CTRL_REG1_ODR_12_5,
                             6.25: CTRL_REG1_ODR_6_25,
                             1.56: CTRL_REG1_ODR_1_56}
        self.CTRL_REG1.set(self.CTRL_REG1.get(cached=True) & 0b11100111 | output_data_rates[output_data_rate])

    def get_g(self):
        x = (self.OUT_X_MSB.get() << 4) | (self.OUT_X_LSB.get() >> 4)
        y = (self.OUT_Y_MSB.get() << 4) | (self.OUT_Y_LSB.get() >> 4)
        z = (self.OUT_Z_MSB.get() << 4) | (self.OUT_Z_LSB.get() >> 4)
        fsr = self.XYZ_DATA_CFG.get(cached=True) & 0b00000011
        g_ranges = {XYZ_DATA_CFG_FSR_2G: 2,
                    XYZ_DATA_CFG_FSR_4G: 4,
                    XYZ_DATA_CFG_FSR_8G: 8}
        g_range = g_ranges[fsr]
        resolution = 12
        multiplier = g_range / (2 ** (resolution - 1))
        x = twos_complement(x, resolution) * multiplier
        y = twos_complement(y, resolution) * multiplier
        z = twos_complement(z, resolution) * multiplier

        return {'x': x, 'y': y, 'z': z}

    def get_ms2(self):
        xyz = self.get_g()
        # multiply each xyz value by the standard gravity value
        return {direction: magnitude * self.gravity
                for direction, magnitude in xyz.items()}
