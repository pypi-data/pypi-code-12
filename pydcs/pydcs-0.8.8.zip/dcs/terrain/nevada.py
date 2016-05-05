from .terrain import Terrain, Airport, Runway, ParkingSlot, MapView, Graph
from .. import mapping
import os


class Creech(Airport):
    id = 1
    name = "Creech"
    position = mapping.Point(-359732, -74970.9)
    tacan = None
    frequencies = [122000000, 38600000, 251000000]
    unit_zones = []
    civilian = False
    slot_version = 2

    def __init__(self):
        super(Creech, self).__init__()

        self.runways.append(Runway(80))
        self.runways.append(Runway(130))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-360682.53125, -75873.546875), large=False, heli=True,
                airplanes=False, slot_name='H13', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(-360683.375, -75850.3515625), large=False, heli=True,
                airplanes=False, slot_name='H12', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-360683.96875, -75827.6015625), large=False, heli=True,
                airplanes=False, slot_name='H11', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=7, position=mapping.Point(-360684.5625, -75804.7578125), large=False, heli=True,
                airplanes=False, slot_name='H10', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-360685.0625, -75782.15625), large=False, heli=True,
                airplanes=False, slot_name='H09', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-360685.8125, -75759.8671875), large=False, heli=True,
                airplanes=False, slot_name='H08', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-360686.53125, -75737.0078125), large=False, heli=True,
                airplanes=False, slot_name='H07', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-360687.3125, -75713.9453125), large=False, heli=True,
                airplanes=False, slot_name='H06', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-360687.84375, -75691.640625), large=False, heli=True,
                airplanes=False, slot_name='H05', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-360696.65625, -75605.953125), large=False, heli=True,
                airplanes=False, slot_name='H04', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-360698, -75569.671875), large=False, heli=True,
                airplanes=False, slot_name='H03', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-360698.84375, -75533.09375), large=False, heli=True,
                airplanes=False, slot_name='H02', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-360699.875, -75496.71875), large=False, heli=True,
                airplanes=False, slot_name='H01', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-360725.40625, -75329.1640625), large=False, heli=False,
                airplanes=True, slot_name='A01', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-360726.90625, -75298.5390625), large=False, heli=False,
                airplanes=True, slot_name='A02', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-360728.28125, -75268.6640625), large=False, heli=False,
                airplanes=True, slot_name='A03', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-360729.75, -75238.1015625), large=False, heli=False,
                airplanes=True, slot_name='A04', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-360731.0625, -75207.7734375), large=False, heli=False,
                airplanes=True, slot_name='A05', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-360732.09375, -75178.578125), large=False, heli=False,
                airplanes=True, slot_name='A06', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-360733.96875, -75145), large=False, heli=False,
                airplanes=True, slot_name='A07', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-360860.5, -74766.4296875), large=False, heli=False,
                airplanes=True, slot_name='A27', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-360862.09375, -74698.609375), large=False, heli=False,
                airplanes=True, slot_name='A28', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-360147.46875, -75552.78125), large=False, heli=False,
                airplanes=True, slot_name='B01', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-360132.21875, -75530.234375), large=False, heli=False,
                airplanes=True, slot_name='B02', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-360114.71875, -75503.8359375), large=False, heli=False,
                airplanes=True, slot_name='B03', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-360100.0625, -75479.9609375), large=False, heli=False,
                airplanes=True, slot_name='B04', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-360083.21875, -75455.2109375), large=False, heli=False,
                airplanes=True, slot_name='B05', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-360067.96875, -75430.78125), large=False, heli=False,
                airplanes=True, slot_name='B06', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-360052.09375, -75407.75), large=False, heli=False,
                airplanes=True, slot_name='B07', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-360036.5625, -75383.390625), large=False, heli=False,
                airplanes=True, slot_name='B08', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-359790, -75834.2265625), large=False, heli=False,
                airplanes=True, slot_name='C01', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-359785.46875, -75793.9296875), large=False, heli=False,
                airplanes=True, slot_name='C02', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=36, position=mapping.Point(-359757.0625, -75619.1640625), large=False, heli=False,
                airplanes=True, slot_name='C03', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-359747.59375, -75578.0390625), large=False, heli=False,
                airplanes=True, slot_name='C04', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-359619.27265034, -74679.236312177), large=False, heli=False,
                airplanes=True, slot_name='D05', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-359638.93551172, -74666.214833227), large=False, heli=False,
                airplanes=True, slot_name='D04', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-359660.59176172, -74653.324208227), large=False, heli=False,
                airplanes=True, slot_name='D03', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-359681.55132758, -74639.525047155), large=False, heli=False,
                airplanes=True, slot_name='D02', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-359703.02221723, -74625.020206057), large=False, heli=False,
                airplanes=True, slot_name='D01', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-359648, -74540.8046875), large=False, heli=False,
                airplanes=True, slot_name='D16', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-359569.28125, -74596.9765625), large=False, heli=False,
                airplanes=True, slot_name='D14', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-359538.78125, -74613.2890625), large=False, heli=False,
                airplanes=True, slot_name='D12', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-359458.8125, -74668.9765625), large=False, heli=False,
                airplanes=True, slot_name='D10', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-359506.21875, -74757.28125), large=False, heli=False,
                airplanes=True, slot_name='D06', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-359479.5, -74773.4375), large=False, heli=False,
                airplanes=True, slot_name='D07', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-359453.625, -74792.4609375), large=False, heli=False,
                airplanes=True, slot_name='D08', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-359427.28125, -74809.390625), large=False, heli=False,
                airplanes=True, slot_name='D09', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-359619.40625, -74497.296875), large=False, heli=False,
                airplanes=True, slot_name='D17', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-359538.46875, -74550.1640625), large=False, heli=False,
                airplanes=True, slot_name='D15', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-359510.3125, -74570.03125), large=False, heli=False,
                airplanes=True, slot_name='D13', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-359427.90625, -74621.9375), large=False, heli=False,
                airplanes=True, slot_name='D11', length=26.0, width=24.0, height=20.0, shelter=False))


class Groom(Airport):
    id = 2
    name = "Groom"
    position = mapping.Point(-288694, -87414.2)
    tacan = None
    frequencies = [123000000, 38800000, 252000000]
    unit_zones = []
    civilian = False
    slot_version = 2

    def __init__(self):
        super(Groom, self).__init__()

        self.runways.append(Runway(320))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-287031.03125, -87680.9453125), large=False, heli=False,
                airplanes=True, slot_name='03', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(-287021.96875, -87660.40625), large=False, heli=False,
                airplanes=True, slot_name='02', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-287013.15625, -87639.8671875), large=False, heli=False,
                airplanes=True, slot_name='01', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(-287085.46875, -87657.1640625), large=False, heli=False,
                airplanes=True, slot_name='06', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-287076.09375, -87636.03125), large=False, heli=False,
                airplanes=True, slot_name='05', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=7, position=mapping.Point(-287067, -87615.140625), large=False, heli=False,
                airplanes=True, slot_name='04', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-286989.03125, -88658.1484375), large=False, heli=True,
                airplanes=False, slot_name='H01', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-287088.65625, -88662.3125), large=False, heli=True,
                airplanes=False, slot_name='H03', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-287036.0625, -88665.71875), large=False, heli=True,
                airplanes=False, slot_name='H02', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-287139.1875, -88658.765625), large=False, heli=True,
                airplanes=False, slot_name='H04', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-287210.5, -88758.765625), large=False, heli=False,
                airplanes=True, slot_name='C06', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-287209.34375, -88740.7734375), large=False, heli=False,
                airplanes=True, slot_name='C05', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-287208, -88722.0234375), large=False, heli=False,
                airplanes=True, slot_name='C04', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-287206.65625, -88704.0078125), large=False, heli=False,
                airplanes=True, slot_name='C03', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-287205.3125, -88685.9921875), large=False, heli=False,
                airplanes=True, slot_name='C02', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-287204.0625, -88668.171875), large=False, heli=False,
                airplanes=True, slot_name='C01', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-287298.3125, -88754.28125), large=False, heli=False,
                airplanes=True, slot_name='C17', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-287316.75, -88753.265625), large=False, heli=False,
                airplanes=True, slot_name='C16', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-287335.25, -88752.3203125), large=False, heli=False,
                airplanes=True, slot_name='C15', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-287353.125, -88750.96875), large=False, heli=False,
                airplanes=True, slot_name='C14', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-287371.65625, -88750.6875), large=False, heli=False,
                airplanes=True, slot_name='C13', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-287295, -89033.7578125), large=False, heli=False,
                airplanes=True, slot_name='C07', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-287314.21875, -89031.703125), large=False, heli=False,
                airplanes=True, slot_name='C08', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-287332.9375, -89029.3125), large=False, heli=False,
                airplanes=True, slot_name='C09', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-287352.25, -89028), large=False, heli=False,
                airplanes=True, slot_name='C10', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-287371.15625, -89026), large=False, heli=False,
                airplanes=True, slot_name='C11', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-287391.46875, -89026.078125), large=False, heli=False,
                airplanes=True, slot_name='C12', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-287821.53125, -88662.4296875), large=False, heli=False,
                airplanes=True, slot_name='B12', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-287819.9375, -88643.015625), large=False, heli=False,
                airplanes=True, slot_name='B11', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-287818.65625, -88623.421875), large=False, heli=False,
                airplanes=True, slot_name='B10', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-287857.0625, -88659.953125), large=False, heli=False,
                airplanes=True, slot_name='B09', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-287856.03125, -88644.328125), large=False, heli=False,
                airplanes=True, slot_name='B08', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-287854.6875, -88624.9765625), large=False, heli=False,
                airplanes=True, slot_name='B07', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-287976.9375, -88623.140625), large=False, heli=False,
                airplanes=True, slot_name='B06', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=36, position=mapping.Point(-288018.34867322, -88620.494576174), large=False, heli=False,
                airplanes=True, slot_name='B05', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-288059.78125, -88617.4140625), large=False, heli=False,
                airplanes=True, slot_name='B04', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-288101.89536924, -88615.021138197), large=False, heli=False,
                airplanes=True, slot_name='B03', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-288143.78125, -88612.2734375), large=False, heli=False,
                airplanes=True, slot_name='B02', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-288192.51793122, -88609.054927123), large=False, heli=False,
                airplanes=True, slot_name='B01', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-288541.3125, -88724.5859375), large=False, heli=False,
                airplanes=True, slot_name='A02', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-288588.34375, -88721.5859375), large=False, heli=False,
                airplanes=True, slot_name='A01', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-288582.4375, -88641.296875), large=False, heli=False,
                airplanes=True, slot_name='A03', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-288538.65625, -88644.4375), large=False, heli=False,
                airplanes=True, slot_name='A04', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-289152.71875, -88598.15625), large=False, heli=False,
                airplanes=True, slot_name='A05', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-290246.0625, -86277.09375), large=False, heli=False,
                airplanes=True, slot_name='09', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-290237.03125, -86255.8828125), large=False, heli=False,
                airplanes=True, slot_name='08', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-290227.96875, -86234.8515625), large=False, heli=False,
                airplanes=True, slot_name='07', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-290300.3125, -86253.421875), large=False, heli=False,
                airplanes=True, slot_name='12', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-290291, -86232.6640625), large=False, heli=False,
                airplanes=True, slot_name='11', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-290282.15625, -86211.484375), large=False, heli=False,
                airplanes=True, slot_name='10', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-288406.46875, -88722.09375), large=False, heli=False,
                airplanes=True, slot_name='A06', length=78.7228, width=67.0965, height=18.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-288412.73465185, -88791.59932747), large=False, heli=False,
                airplanes=True, slot_name='A07', length=78.7228, width=67.0965, height=18.0, shelter=False))


class McCarran(Airport):
    id = 3
    name = "McCarran"
    position = mapping.Point(-416083, -27121.1)
    tacan = None
    frequencies = [124000000, 39000000, 253000000]
    unit_zones = []
    civilian = False
    slot_version = 2

    def __init__(self):
        super(McCarran, self).__init__()

        self.runways.append(Runway(70))
        self.runways.append(Runway(70))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=0, position=mapping.Point(-415257.57624166, -25235.620152082), large=False, heli=False,
                airplanes=True, slot_name='01', length=78.7228, width=67.0965, height=18.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=1, position=mapping.Point(-415299.8125, -25565.33984375), large=False, heli=False,
                airplanes=True, slot_name='02', length=78.7228, width=67.0965, height=18.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-415416.5625, -25562.279296875), large=False, heli=False,
                airplanes=True, slot_name='03', length=78.7228, width=67.0965, height=18.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(-415462.96677517, -25559.448116796), large=False, heli=False,
                airplanes=True, slot_name='04', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-415516.5625, -25553.318359375), large=False, heli=False,
                airplanes=True, slot_name='05', length=78.7228, width=67.0965, height=18.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-415320.94681994, -27463.112736896), large=False, heli=False,
                airplanes=True, slot_name='07', length=22.7274, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-415374.69906801, -27152.648387252), large=False, heli=False,
                airplanes=True, slot_name='06', length=78.7228, width=67.0965, height=18.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-414696.90625, -29025.103515625), large=False, heli=True,
                airplanes=False, slot_name='H09', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-414696.5, -28984.884765625), large=False, heli=True,
                airplanes=False, slot_name='H07', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-414696.125, -28945.2109375), large=False, heli=True,
                airplanes=False, slot_name='H05', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-414695.71875, -28905.353515625), large=False, heli=True,
                airplanes=False, slot_name='H03', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-414695.40625, -28865.255859375), large=False, heli=True,
                airplanes=False, slot_name='H01', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-414725.375, -29044.947265625), large=False, heli=True,
                airplanes=False, slot_name='H11', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-414724.84375, -29004.904296875), large=False, heli=True,
                airplanes=False, slot_name='H13', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-414724.4375, -28964.96484375), large=False, heli=True,
                airplanes=False, slot_name='H15', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-414723.61629733, -28932.518344013), large=False, heli=True,
                airplanes=False, slot_name='H16', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-414727.25, -28895.244140625), large=False, heli=True,
                airplanes=False, slot_name='H17', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-414761.53125, -28890.283203125), large=False, heli=True,
                airplanes=False, slot_name='H23', length=28.5104, width=21.5, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-414781.1875, -28918.62109375), large=False, heli=True,
                airplanes=False, slot_name='H20', length=28.5104, width=21.5, height=None, shelter=False))


class Nellis(Airport):
    id = 4
    name = "Nellis"
    position = mapping.Point(-397971, -17639.5)
    tacan = None
    frequencies = [125000000, 39200000, 254000000]
    unit_zones = []
    civilian = False
    slot_version = 2

    def __init__(self):
        super(Nellis, self).__init__()

        self.runways.append(Runway(30))
        self.runways.append(Runway(30))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-399468.03125, -18132.794921875), large=False, heli=False,
                airplanes=True, slot_name='A05', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(-399481.84375, -18115.802734375), large=False, heli=False,
                airplanes=True, slot_name='A06', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-399494.8125, -18099.30078125), large=False, heli=False,
                airplanes=True, slot_name='A07', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=7, position=mapping.Point(-399508.40625, -18082.740234375), large=False, heli=False,
                airplanes=True, slot_name='A08', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-399522.65625, -18067.08984375), large=False, heli=False,
                airplanes=True, slot_name='A09', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-399536.78125, -18050.83203125), large=False, heli=False,
                airplanes=True, slot_name='A10', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-399550.4375, -18034.271484375), large=False, heli=False,
                airplanes=True, slot_name='A11', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-399563.65625, -18018.255859375), large=False, heli=False,
                airplanes=True, slot_name='A12', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-399577.5, -18001.57421875), large=False, heli=False,
                airplanes=True, slot_name='A13', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-399285.75, -18329.0859375), large=False, heli=False,
                airplanes=True, slot_name='A04', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-399268.21875, -18350.09765625), large=False, heli=False,
                airplanes=True, slot_name='A03', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-399252.03125, -18371.326171875), large=False, heli=False,
                airplanes=True, slot_name='A02', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-399235.6875, -18392.296875), large=False, heli=False,
                airplanes=True, slot_name='A01', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-399632.8125, -17804.15234375), large=False, heli=False,
                airplanes=True, slot_name='G01', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-399609.21875, -17784.78125), large=False, heli=False,
                airplanes=True, slot_name='G02', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-399585.9375, -17765.4296875), large=False, heli=False,
                airplanes=True, slot_name='G03', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-399562.9375, -17745.71484375), large=False, heli=False,
                airplanes=True, slot_name='G04', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-399539.46875, -17726.12109375), large=False, heli=False,
                airplanes=True, slot_name='G05', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-399516.0625, -17706.34375), large=False, heli=False,
                airplanes=True, slot_name='G06', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-399493, -17686.326171875), large=False, heli=False,
                airplanes=True, slot_name='G07', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-399469.21875, -17666.791015625), large=False, heli=False,
                airplanes=True, slot_name='G08', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-399446.15625, -17647.318359375), large=False, heli=False,
                airplanes=True, slot_name='G09', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-399422.9375, -17627.724609375), large=False, heli=False,
                airplanes=True, slot_name='G10', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-399399.875, -17608.3125), large=False, heli=False,
                airplanes=True, slot_name='G11', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-399376.03125, -17588.537109375), large=False, heli=False,
                airplanes=True, slot_name='G12', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-399352.375, -17568.517578125), large=False, heli=False,
                airplanes=True, slot_name='G13', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-399327.34375, -17547.1640625), large=False, heli=False,
                airplanes=True, slot_name='G14', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-399302.46875, -17526.41796875), large=False, heli=False,
                airplanes=True, slot_name='G15', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-399277.875, -17505.669921875), large=False, heli=False,
                airplanes=True, slot_name='G16', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-399253.0625, -17484.8984375), large=False, heli=False,
                airplanes=True, slot_name='G17', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-399228.40625, -17463.767578125), large=False, heli=False,
                airplanes=True, slot_name='G18', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-399203.84375, -17443.546875), large=False, heli=False,
                airplanes=True, slot_name='G19', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=36, position=mapping.Point(-399179.375, -17422.21484375), large=False, heli=False,
                airplanes=True, slot_name='G20', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-399154.34375, -17401.943359375), large=False, heli=False,
                airplanes=True, slot_name='G21', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-399129.53125, -17380.66015625), large=False, heli=False,
                airplanes=True, slot_name='G22', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-399104.9375, -17359.9921875), large=False, heli=False,
                airplanes=True, slot_name='G23', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-399079.9375, -17339.408203125), large=False, heli=False,
                airplanes=True, slot_name='G24', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-399055.21875, -17318.33984375), large=False, heli=False,
                airplanes=True, slot_name='G25', length=26.0, width=24.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-398957.375, -17236.330078125), large=False, heli=False,
                airplanes=True, slot_name='G26', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-398908.75, -17193.064453125), large=False, heli=False,
                airplanes=True, slot_name='G27', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-398860.28832851, -17149.502505997), large=False, heli=False,
                airplanes=True, slot_name='G28', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-398775.03125, -16494.689453125), large=False, heli=False,
                airplanes=True, slot_name='C01', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-398799.5, -16453.03515625), large=False, heli=False,
                airplanes=True, slot_name='C02', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-398824.6875, -16411.25), large=False, heli=False,
                airplanes=True, slot_name='C03', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-398850.03125, -16369.627929688), large=False, heli=False,
                airplanes=True, slot_name='C04', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-398874.84375, -16328.064453125), large=False, heli=False,
                airplanes=True, slot_name='C05', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-398900.3125, -16288.135742188), large=False, heli=False,
                airplanes=True, slot_name='C06', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-398614.78125, -16496.521484375), large=False, heli=False,
                airplanes=True, slot_name='C07', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-398591.1875, -16453.716796875), large=False, heli=False,
                airplanes=True, slot_name='C08', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-398567.03125, -16410.140625), large=False, heli=False,
                airplanes=True, slot_name='C09', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-398542.78125, -16366.208984375), large=False, heli=False,
                airplanes=True, slot_name='C10', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-398518.8125, -16322.481445313), large=False, heli=False,
                airplanes=True, slot_name='C11', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-398493.9375, -16287.296875), large=False, heli=False,
                airplanes=True, slot_name='C12', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-397871.1875, -16515.53125), large=False, heli=False,
                airplanes=True, slot_name='G29', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(-397833.71875, -16483.927734375), large=False, heli=False,
                airplanes=True, slot_name='G30', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-397796.25, -16451.1796875), large=False, heli=False,
                airplanes=True, slot_name='G31', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-397758.625, -16418.984375), large=False, heli=False,
                airplanes=True, slot_name='G32', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(-397639.59375, -16350.368164063), large=False, heli=False,
                airplanes=True, slot_name='G33', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-397601.59375, -16317.193359375), large=False, heli=False,
                airplanes=True, slot_name='G34', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-397707.54722631, -16375.160214965), large=False, heli=False,
                airplanes=True, slot_name='G35', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=64, position=mapping.Point(-397501.5625, -16237.845703125), large=False, heli=False,
                airplanes=True, slot_name='G37', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-397539.8125, -16196.006835938), large=False, heli=False,
                airplanes=True, slot_name='G36', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=66, position=mapping.Point(-397392.71875, -16146.012695313), large=False, heli=False,
                airplanes=True, slot_name='G39', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=67, position=mapping.Point(-397428.40625, -16102.09765625), large=False, heli=False,
                airplanes=True, slot_name='G38', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=68, position=mapping.Point(-396939.14711578, -15793.794429073), large=False, heli=False,
                airplanes=True, slot_name='E13', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-397176.46875, -16131.192382813), large=False, heli=False,
                airplanes=True, slot_name='E11', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=70, position=mapping.Point(-397162.65625, -16147.19921875), large=False, heli=False,
                airplanes=True, slot_name='E10', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-397148.96875, -16163.375976563), large=False, heli=False,
                airplanes=True, slot_name='E09', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=72, position=mapping.Point(-397135.21875, -16179.889648438), large=False, heli=False,
                airplanes=True, slot_name='E08', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=73, position=mapping.Point(-397121.625, -16196.024414063), large=False, heli=False,
                airplanes=True, slot_name='E07', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=74, position=mapping.Point(-396813.53125, -16946.072265625), large=False, heli=False,
                airplanes=True, slot_name='E01', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=75, position=mapping.Point(-396815.21875, -16921.412109375), large=False, heli=False,
                airplanes=True, slot_name='E02', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-396816.4375, -16895.833984375), large=False, heli=False,
                airplanes=True, slot_name='E03', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=77, position=mapping.Point(-396818.1875, -16870.94921875), large=False, heli=False,
                airplanes=True, slot_name='E04', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-396819.71875, -16844.984375), large=False, heli=False,
                airplanes=True, slot_name='E05', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-396825.4375, -16823.09765625), large=False, heli=False,
                airplanes=True, slot_name='E06', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-397017.09375, -16873.912109375), large=False, heli=False,
                airplanes=True, slot_name='D01', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=81, position=mapping.Point(-397018.75, -16849.865234375), large=False, heli=False,
                airplanes=True, slot_name='D02', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-397017.78125, -16823.912109375), large=False, heli=False,
                airplanes=True, slot_name='D03', length=22.9711, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-396495.21875, -17137.720703125), large=False, heli=True,
                airplanes=False, slot_name='04', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=84, position=mapping.Point(-396541.40625, -17138.611328125), large=False, heli=True,
                airplanes=False, slot_name='05', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-396587.6875, -17139.62109375), large=False, heli=True,
                airplanes=False, slot_name='06', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-396488.15625, -17052.21875), large=False, heli=True,
                airplanes=False, slot_name='01', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=87, position=mapping.Point(-396515.4375, -17052.734375), large=False, heli=True,
                airplanes=False, slot_name='02', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-396542.78125, -17053.294921875), large=False, heli=True,
                airplanes=False, slot_name='03', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=89, position=mapping.Point(-396407.0625, -17269.4609375), large=False, heli=True,
                airplanes=False, slot_name='H07', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-396356.9375, -17191.818359375), large=False, heli=True,
                airplanes=False, slot_name='H03', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=91, position=mapping.Point(-396357.09375, -17159.314453125), large=False, heli=True,
                airplanes=False, slot_name='H02', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=92, position=mapping.Point(-396357.53125, -17127.65234375), large=False, heli=True,
                airplanes=False, slot_name='H01', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=93, position=mapping.Point(-396427.96875, -17192.732421875), large=False, heli=True,
                airplanes=False, slot_name='H06', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=94, position=mapping.Point(-396428.6875, -17159.482421875), large=False, heli=True,
                airplanes=False, slot_name='H05', length=30.0964, width=23.0, height=10.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=95, position=mapping.Point(-396429.1875, -17126.84375), large=False, heli=True,
                airplanes=False, slot_name='H04', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=96, position=mapping.Point(-396626.6875, -17261.57421875), large=False, heli=True,
                airplanes=False, slot_name='H08', length=42.0, width=34.0, height=14.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=97, position=mapping.Point(-396894.99429792, -17427.297869104), large=False, heli=False,
                airplanes=True, slot_name='09', length=78.7228, width=67.0965, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=98, position=mapping.Point(-396894.34375, -17373.21484375), large=False, heli=False,
                airplanes=True, slot_name='08', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=99, position=mapping.Point(-396894.46875, -17320.515625), large=False, heli=False,
                airplanes=True, slot_name='07', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=100, position=mapping.Point(-396989.75, -17373.185546875), large=False, heli=False,
                airplanes=True, slot_name='10', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(-396983.5625, -17428.751953125), large=False, heli=False,
                airplanes=True, slot_name='11', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=102, position=mapping.Point(-397228.02803954, -17305.196424077), large=False, heli=False,
                airplanes=True, slot_name='F12', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=103, position=mapping.Point(-397228.20970166, -17286.458984375), large=False, heli=False,
                airplanes=True, slot_name='F11', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=104, position=mapping.Point(-397228.55055264, -17269.019188339), large=False, heli=False,
                airplanes=True, slot_name='F10', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=105, position=mapping.Point(-397229.01836829, -17224.390741296), large=False, heli=False,
                airplanes=True, slot_name='F07', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=106, position=mapping.Point(-397229.67278146, -17198.669572986), large=False, heli=False,
                airplanes=True, slot_name='F05', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=107, position=mapping.Point(-397229.66176049, -17172.58351919), large=False, heli=False,
                airplanes=True, slot_name='F03', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(-397230.05145512, -17146.210704907), large=False, heli=False,
                airplanes=True, slot_name='F01', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=109, position=mapping.Point(-397276.54041023, -17287.2265625), large=False, heli=False,
                airplanes=True, slot_name='F14', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=110, position=mapping.Point(-397276.19666023, -17305.667852454), large=False, heli=False,
                airplanes=True, slot_name='F13', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=111, position=mapping.Point(-397276.90989974, -17269.402692639), large=False, heli=False,
                airplanes=True, slot_name='F15', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=112, position=mapping.Point(-397277.57828238, -17225.128673657), large=False, heli=False,
                airplanes=True, slot_name='F18', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=113, position=mapping.Point(-397278.08637877, -17199.529296875), large=False, heli=False,
                airplanes=True, slot_name='F20', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=114, position=mapping.Point(-397278.3198234, -17173.458868079), large=False, heli=False,
                airplanes=True, slot_name='F22', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(-397278.66908389, -17146.9375), large=False, heli=False,
                airplanes=True, slot_name='F24', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=116, position=mapping.Point(-397353.78125, -17213.474609375), large=False, heli=False,
                airplanes=True, slot_name='F27', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=117, position=mapping.Point(-397334.1875, -17196.017578125), large=False, heli=False,
                airplanes=True, slot_name='F25', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=118, position=mapping.Point(-397337.67530081, -17335.577824813), large=False, heli=False,
                airplanes=True, slot_name='F36', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=119, position=mapping.Point(-397349.01467072, -17322.475961091), large=False, heli=False,
                airplanes=True, slot_name='F35', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=120, position=mapping.Point(-397362.0358341, -17306.853732276), large=False, heli=False,
                airplanes=True, slot_name='F34', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=121, position=mapping.Point(-397382.34121192, -17283.010603613), large=False, heli=False,
                airplanes=True, slot_name='F32', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=122, position=mapping.Point(-397399.17031512, -17262.972714295), large=False, heli=False,
                airplanes=True, slot_name='F30', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=123, position=mapping.Point(-397415.90856898, -17243.08242449), large=False, heli=False,
                airplanes=True, slot_name='F28', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=124, position=mapping.Point(-397389.83671744, -17379.520256416), large=False, heli=False,
                airplanes=True, slot_name='F45', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=125, position=mapping.Point(-397401.11506678, -17366.330078125), large=False, heli=False,
                airplanes=True, slot_name='F44', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=126, position=mapping.Point(-397413.30186552, -17351.608950897), large=False, heli=False,
                airplanes=True, slot_name='F43', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=127, position=mapping.Point(-397434.0674447, -17326.470324109), large=False, heli=False,
                airplanes=True, slot_name='F41', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=128, position=mapping.Point(-397450.95523477, -17306.323493584), large=False, heli=False,
                airplanes=True, slot_name='F39', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=129, position=mapping.Point(-397467.59724437, -17286.72917506), large=False, heli=False,
                airplanes=True, slot_name='F37', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=130, position=mapping.Point(-397440.38892961, -17422.544076427), large=False, heli=False,
                airplanes=True, slot_name='F54', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=131, position=mapping.Point(-397452.03584207, -17409.086623322), large=False, heli=False,
                airplanes=True, slot_name='F53', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=132, position=mapping.Point(-397464.70770512, -17393.537899536), large=False, heli=False,
                airplanes=True, slot_name='F52', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=133, position=mapping.Point(-397485.13884516, -17369.429836032), large=False, heli=False,
                airplanes=True, slot_name='F50', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=134, position=mapping.Point(-397501.9090192, -17349.356260072), large=False, heli=False,
                airplanes=True, slot_name='F48', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=135, position=mapping.Point(-397518.30221536, -17329.430454066), large=False, heli=False,
                airplanes=True, slot_name='F46', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=136, position=mapping.Point(-397615.28125, -17489.353515625), large=False, heli=False,
                airplanes=True, slot_name='F56', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=137, position=mapping.Point(-397559.28125, -17439.673828125), large=False, heli=False,
                airplanes=True, slot_name='F55', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=138, position=mapping.Point(-397667.25, -17531.330078125), large=False, heli=False,
                airplanes=True, slot_name='F57', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=139, position=mapping.Point(-397716.34375, -17577.064453125), large=False, heli=False,
                airplanes=True, slot_name='F58', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=140, position=mapping.Point(-397747.54685507, -17674.741938965), large=False, heli=False,
                airplanes=True, slot_name='F64', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=141, position=mapping.Point(-397759.71875, -17660.845703125), large=False, heli=False,
                airplanes=True, slot_name='F63', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=142, position=mapping.Point(-397772.39153943, -17645.521274044), large=False, heli=False,
                airplanes=True, slot_name='F62', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=143, position=mapping.Point(-397789.66732596, -17625.57357596), large=False, heli=False,
                airplanes=True, slot_name='F61', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=144, position=mapping.Point(-397800.41409537, -17612.940260668), large=False, heli=False,
                airplanes=True, slot_name='F60', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=145, position=mapping.Point(-397811.52089921, -17599.023602253), large=False, heli=False,
                airplanes=True, slot_name='F59', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=146, position=mapping.Point(-397865.2941078, -17644.538248426), large=False, heli=False,
                airplanes=True, slot_name='F65', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=147, position=mapping.Point(-397854.125, -17658.101446204), large=False, heli=False,
                airplanes=True, slot_name='F66', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=148, position=mapping.Point(-397843.66545806, -17670.865932153), large=False, heli=False,
                airplanes=True, slot_name='F67', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=149, position=mapping.Point(-397827.33185047, -17690.383969485), large=False, heli=False,
                airplanes=True, slot_name='F68', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=150, position=mapping.Point(-397815.20221166, -17704.84097482), large=False, heli=False,
                airplanes=True, slot_name='F70', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=151, position=mapping.Point(-397801.98163171, -17720.610537964), large=False, heli=False,
                airplanes=True, slot_name='F71', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=152, position=mapping.Point(-397855.2821445, -17765.427132966), large=False, heli=False,
                airplanes=True, slot_name='F77', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=153, position=mapping.Point(-397867.12130243, -17751.056849305), large=False, heli=False,
                airplanes=True, slot_name='F76', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=154, position=mapping.Point(-397880.2287327, -17735.870947988), large=False, heli=False,
                airplanes=True, slot_name='F75', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=155, position=mapping.Point(-397896.86768457, -17715.784614623), large=False, heli=False,
                airplanes=True, slot_name='F74', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=156, position=mapping.Point(-397907.58277685, -17703.095867247), large=False, heli=False,
                airplanes=True, slot_name='F73', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=157, position=mapping.Point(-397918.8410665, -17689.597258818), large=False, heli=False,
                airplanes=True, slot_name='F72', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=158, position=mapping.Point(-397982.19383125, -17780.111721156), large=False, heli=False,
                airplanes=True, slot_name='F78', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=159, position=mapping.Point(-398032.83425154, -17823.250283303), large=False, heli=False,
                airplanes=True, slot_name='F79', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=160, position=mapping.Point(-398083.72547581, -17865.672145612), large=False, heli=False,
                airplanes=True, slot_name='F80', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=161, position=mapping.Point(-398128.09357472, -17903.543003824), large=False, heli=False,
                airplanes=True, slot_name='F81', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=162, position=mapping.Point(-398162.7162851, -17932.6043404), large=False, heli=False,
                airplanes=True, slot_name='F82', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=163, position=mapping.Point(-398200.20515857, -17963.775893418), large=False, heli=False,
                airplanes=True, slot_name='F83', length=22.7274, width=18.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=164, position=mapping.Point(-398226.78441444, -17986.375148532), large=False, heli=False,
                airplanes=True, slot_name='F84', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=165, position=mapping.Point(-398274.91732596, -18027.318359375), large=False, heli=False,
                airplanes=True, slot_name='F85', length=39.8575, width=40.0, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=166, position=mapping.Point(-398303.78673657, -18143.260090601), large=False, heli=False,
                airplanes=True, slot_name='F91', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=167, position=mapping.Point(-398319.34005243, -18124.604073194), large=False, heli=False,
                airplanes=True, slot_name='F90', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=168, position=mapping.Point(-398347.41177643, -18091.277468017), large=False, heli=False,
                airplanes=True, slot_name='F88', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=169, position=mapping.Point(-398357.92465814, -18078.913625213), large=False, heli=False,
                airplanes=True, slot_name='F87', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=170, position=mapping.Point(-398368.45038171, -18066.050905517), large=False, heli=False,
                airplanes=True, slot_name='F86', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=171, position=mapping.Point(-398350.99603083, -18182.929084523), large=False, heli=False,
                airplanes=True, slot_name='F97', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=172, position=mapping.Point(-398366.28953964, -18164.28620491), large=False, heli=False,
                airplanes=True, slot_name='F96', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=173, position=mapping.Point(-398394.46754405, -18130.773374583), large=False, heli=False,
                airplanes=True, slot_name='F94', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=174, position=mapping.Point(-398404.85716409, -18118.414106199), large=False, heli=False,
                airplanes=True, slot_name='F93', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=175, position=mapping.Point(-398415.33732907, -18105.626391571), large=False, heli=False,
                airplanes=True, slot_name='F92', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=176, position=mapping.Point(-398409.38667989, -18201.745188147), large=False, heli=False,
                airplanes=True, slot_name='F102', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=177, position=mapping.Point(-398394.44256196, -18219.51041885), large=False, heli=False,
                airplanes=True, slot_name='F103', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=178, position=mapping.Point(-398437.84651321, -18167.396255768), large=False, heli=False,
                airplanes=True, slot_name='F100', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=179, position=mapping.Point(-398448.26747379, -18154.851915375), large=False, heli=False,
                airplanes=True, slot_name='F99', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=180, position=mapping.Point(-398458.64622315, -18142.091770979), large=False, heli=False,
                airplanes=True, slot_name='F98', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=181, position=mapping.Point(-398440.41546603, -18262.10870512), large=False, heli=False,
                airplanes=True, slot_name='F111', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=182, position=mapping.Point(-398450.8676208, -18249.418983533), large=False, heli=False,
                airplanes=True, slot_name='F110', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=183, position=mapping.Point(-398460.92644714, -18237.300532715), large=False, heli=False,
                airplanes=True, slot_name='F109', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=184, position=mapping.Point(-398471.48252621, -18224.819502411), large=False, heli=False,
                airplanes=True, slot_name='F108', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=185, position=mapping.Point(-398481.28125, -18213.091796875), large=False, heli=False,
                airplanes=True, slot_name='F107', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=186, position=mapping.Point(-398491.96875, -18200.25), large=False, heli=False,
                airplanes=True, slot_name='F106', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=187, position=mapping.Point(-398502.42925021, -18187.66235791), large=False, heli=False,
                airplanes=True, slot_name='F105', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=188, position=mapping.Point(-398512.97614514, -18175.298061877), large=False, heli=False,
                airplanes=True, slot_name='F104', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=189, position=mapping.Point(-398492.70352428, -18306.161012743), large=False, heli=False,
                airplanes=True, slot_name='F118', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=190, position=mapping.Point(-398505.91701404, -18290.651539781), large=False, heli=False,
                airplanes=True, slot_name='F117', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=191, position=mapping.Point(-398518.68843436, -18275.21714975), large=False, heli=False,
                airplanes=True, slot_name='F116', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=192, position=mapping.Point(-398534.82355286, -18255.912014999), large=False, heli=False,
                airplanes=True, slot_name='F115', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=193, position=mapping.Point(-398545.78900772, -18243.113058876), large=False, heli=False,
                airplanes=True, slot_name='F114', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=194, position=mapping.Point(-398555.7119904, -18230.966556822), large=False, heli=False,
                airplanes=True, slot_name='F113', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=195, position=mapping.Point(-398566.19489514, -18218.446266784), large=False, heli=False,
                airplanes=True, slot_name='F112', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=196, position=mapping.Point(-398545.36857907, -18350.523104553), large=False, heli=False,
                airplanes=True, slot_name='F125', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=197, position=mapping.Point(-398558.45956586, -18334.941987732), large=False, heli=False,
                airplanes=True, slot_name='F124', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=198, position=mapping.Point(-398571.22220402, -18319.51928001), large=False, heli=False,
                airplanes=True, slot_name='F123', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=199, position=mapping.Point(-398587.48715814, -18300.082508392), large=False, heli=False,
                airplanes=True, slot_name='F122', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=200, position=mapping.Point(-398598.0992844, -18287.253232385), large=False, heli=False,
                airplanes=True, slot_name='F121', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=201, position=mapping.Point(-398608.29596854, -18275.251046667), large=False, heli=False,
                airplanes=True, slot_name='F120', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=202, position=mapping.Point(-398618.66989042, -18262.632511012), large=False, heli=False,
                airplanes=True, slot_name='F119', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=203, position=mapping.Point(-398609.70356413, -18404.774379115), large=False, heli=False,
                airplanes=True, slot_name='F132', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=204, position=mapping.Point(-398622.7785665, -18389.082901122), large=False, heli=False,
                airplanes=True, slot_name='F131', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=205, position=mapping.Point(-398635.45042157, -18373.737178069), large=False, heli=False,
                airplanes=True, slot_name='F130', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=206, position=mapping.Point(-398651.79140835, -18354.126307158), large=False, heli=False,
                airplanes=True, slot_name='F129', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=207, position=mapping.Point(-398662.23719003, -18342.004070372), large=False, heli=False,
                airplanes=True, slot_name='F128', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=208, position=mapping.Point(-398672.64341611, -18329.49474602), large=False, heli=False,
                airplanes=True, slot_name='F127', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=209, position=mapping.Point(-398683.40918887, -18316.535331904), large=False, heli=False,
                airplanes=True, slot_name='F126', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=210, position=mapping.Point(-398667.75793833, -18453.579902471), large=False, heli=False,
                airplanes=True, slot_name='F139', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=211, position=mapping.Point(-398680.89426279, -18437.934135377), large=False, heli=False,
                airplanes=True, slot_name='F138', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=212, position=mapping.Point(-398693.70586829, -18422.754467804), large=False, heli=False,
                airplanes=True, slot_name='F137', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=213, position=mapping.Point(-398709.90262417, -18403.278995812), large=False, heli=False,
                airplanes=True, slot_name='F136', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=214, position=mapping.Point(-398720.74086368, -18390.509697155), large=False, heli=False,
                airplanes=True, slot_name='F135', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=215, position=mapping.Point(-398730.99453734, -18378.433060094), large=False, heli=False,
                airplanes=True, slot_name='F134', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=216, position=mapping.Point(-398741.51476637, -18366.117467919), large=False, heli=False,
                airplanes=True, slot_name='F133', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=217, position=mapping.Point(-398728.50835829, -18504.749641321), large=False, heli=False,
                airplanes=True, slot_name='F146', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=218, position=mapping.Point(-398741.58872691, -18489.109275362), large=False, heli=False,
                airplanes=True, slot_name='F145', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=219, position=mapping.Point(-398754.32681941, -18474.020687385), large=False, heli=False,
                airplanes=True, slot_name='F144', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=220, position=mapping.Point(-398770.62122272, -18454.729578951), large=False, heli=False,
                airplanes=True, slot_name='F143', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=221, position=mapping.Point(-398781.0163067, -18442.254351653), large=False, heli=False,
                airplanes=True, slot_name='F142', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=222, position=mapping.Point(-398791.56714816, -18429.487547177), large=False, heli=False,
                airplanes=True, slot_name='F141', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=223, position=mapping.Point(-398801.92159971, -18417.143050005), large=False, heli=False,
                airplanes=True, slot_name='F140', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=224, position=mapping.Point(-398780.13418414, -18548.301924286), large=False, heli=False,
                airplanes=True, slot_name='F153', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=225, position=mapping.Point(-398793.24817114, -18532.617540375), large=False, heli=False,
                airplanes=True, slot_name='F152', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=226, position=mapping.Point(-398805.78307886, -18517.806059143), large=False, heli=False,
                airplanes=True, slot_name='F151', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=227, position=mapping.Point(-398822.54502621, -18497.887633179), large=False, heli=False,
                airplanes=True, slot_name='F150', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=228, position=mapping.Point(-398832.88877621, -18485.705182465), large=False, heli=False,
                airplanes=True, slot_name='F149', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=229, position=mapping.Point(-398843, -18473.53125), large=False, heli=False,
                airplanes=True, slot_name='F148', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=230, position=mapping.Point(-398853.43380243, -18461.227124054), large=False, heli=False,
                airplanes=True, slot_name='F147', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=231, position=mapping.Point(-398900, -18561.5078125), large=False, heli=False,
                airplanes=True, slot_name='F154', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=232, position=mapping.Point(-398958.28125, -18614.92578125), large=False, heli=False,
                airplanes=True, slot_name='F155', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=233, position=mapping.Point(-399016.21875, -18668.3359375), large=False, heli=False,
                airplanes=True, slot_name='F156', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=234, position=mapping.Point(-399073.75, -18716.099609375), large=False, heli=False,
                airplanes=True, slot_name='F157', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=235, position=mapping.Point(-399130.1875, -18755.638671875), large=False, heli=False,
                airplanes=True, slot_name='F158', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=236, position=mapping.Point(-399181.75, -18801.109375), large=False, heli=False,
                airplanes=True, slot_name='F159', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=237, position=mapping.Point(-399231.28125, -18848.513671875), large=False, heli=False,
                airplanes=True, slot_name='F160', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=238, position=mapping.Point(-399282.90625, -18894.162109375), large=False, heli=False,
                airplanes=True, slot_name='F161', length=39.8278, width=40.0, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=239, position=mapping.Point(-399245.60017093, -18688.000934356), large=False, heli=False,
                airplanes=True, slot_name='F165', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=240, position=mapping.Point(-399228.31802643, -18673.378429108), large=False, heli=False,
                airplanes=True, slot_name='F166', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=241, position=mapping.Point(-399211.08826343, -18658.880943787), large=False, heli=False,
                airplanes=True, slot_name='F167', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=242, position=mapping.Point(-399194.27942114, -18644.426114197), large=False, heli=False,
                airplanes=True, slot_name='F168', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=243, position=mapping.Point(-399177.00828964, -18629.994577912), large=False, heli=False,
                airplanes=True, slot_name='F170', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=244, position=mapping.Point(-399159.47703964, -18615.267786805), large=False, heli=False,
                airplanes=True, slot_name='F171', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=245, position=mapping.Point(-399142.51930264, -18600.957717072), large=False, heli=False,
                airplanes=True, slot_name='F172', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=246, position=mapping.Point(-399125.28125, -18585.966796875), large=False, heli=False,
                airplanes=True, slot_name='F173', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=247, position=mapping.Point(-399107.71598679, -18571.223466339), large=False, heli=False,
                airplanes=True, slot_name='F174', length=22.9224, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=248, position=mapping.Point(-399499.78125, -19155.43359375), large=False, heli=False,
                airplanes=True, slot_name='F162', length=23.0763, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=249, position=mapping.Point(-399571.90625, -19235.638671875), large=False, heli=False,
                airplanes=True, slot_name='F163', length=23.0763, width=14.5, height=20.0, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=250, position=mapping.Point(-399382, -19269.267578125), large=False, heli=False,
                airplanes=True, slot_name='F164', length=23.0763, width=14.5, height=20.0, shelter=False))


class Nevada(Terrain):
    center = {"lat": 39.81806, "long": -114.73333}
    bounds = mapping.Rectangle(-497177.656250, -329334.875000, -166934.953125, 209836.890625)
    map_view_default = MapView(mapping.Point(-340928.57142857, -55928.571428568), 1000000)
    city_graph = Graph.from_pickle(os.path.join(os.path.dirname(__file__), 'nevada.p'))

    def __init__(self):
        super(Nevada, self).__init__("Nevada")
        # nttr center MGRS
        # 11SPE9400410022
        self.bullseye_blue = {"x": -409931.344, "y": -14024.097}
        self.bullseye_red = {"x": -288293.969, "y": -88022.641}

        self.airports['Creech'] = Creech()
        self.airports['Groom'] = Groom()
        self.airports['McCarran'] = McCarran()
        self.airports['Nellis'] = Nellis()

    def creech(self) -> Airport:
        return self.airports["Creech"]

    def groom(self) -> Airport:
        return self.airports["Groom"]

    def mccarran(self) -> Airport:
        return self.airports["McCarran"]

    def nellis(self) -> Airport:
        return self.airports["Nellis"]
