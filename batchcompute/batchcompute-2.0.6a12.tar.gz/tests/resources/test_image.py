import unittest

from batchcompute.resources.image import *

class ImageDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.snapshot_id = "batchcompute_snapshot"
        self.image_name = "batchcompute_image"
        self.image_desc = "batchcompute_image created by batchcompute"
        self.image_id = "m-23rjvafd9"

    def get_device_mapping(self):
        disk = DeviceDescription()

        disk.ECSSnapshotId = self.snapshot_id

        self.assertEqual(disk.ECSSnapshotId, self.snapshot_id)

        return disk

    def get_image_description(self):
        img_desc = ImageDescription()

        disk1 = self.get_device_mapping()
        disk2 = self.get_device_mapping()
        disk3 = self.get_device_mapping()

        img_desc.Name = self.image_name
        img_desc.OS = "Windows" 
        img_desc.ECSImageId = self.image_id 

        img_desc.add_disk('disk1', disk1)
        img_desc.add_disk('disk2', disk2)
        img_desc.add_disk('disk3', disk3)

        self.assertEqual(img_desc.get_disk('disk1').dump(), disk1.dump())
        self.assertEqual(img_desc.get_disk('disk2').dump(), disk2.dump())
        self.assertEqual(img_desc.get_disk('disk3').dump(), disk3.dump())

        img_desc.delete_disk('disk1')
        img_desc.delete_disk('disk2')
        img_desc.delete_disk('disk3')

        self.assertRaises(KeyError, img_desc.get_disk, 'disk1')

        img_desc.add_disk('disk1', disk1)
        img_desc.add_disk('disk2', disk2)
        img_desc.add_disk('disk3', disk3)
        return img_desc

    def testDevice(self):
        self.get_device_mapping()

    def testImageDescription(self):
        self.get_image_description()

if __name__ == '__main__':
    unittest.main()
