from Gecko import GeckoIO


class LightSensor(GeckoIO.Boards.ControlAnything.Pins.Analog):

    # This is optional and typically used during devlopment.
    # if this doesn't exist, 
    cik = '98acd7f4dc8dd67cee40462ea623f99c8bc4adf1'


    # Pin identifier on the board
    pin_id = 0

    # Report rate in seconds
    # Must be a multiple of read_rate, else will be rounded up to read rate.
    # default is 10 seconds
    report_rate = 5

    # description of sensor
    description = "Monitors the light levels in the office"
