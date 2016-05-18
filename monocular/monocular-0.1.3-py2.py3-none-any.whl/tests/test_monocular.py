import monocular

import unittest

class TestMonocularSDK(unittest.TestCase):
    def test_monocular(self):
        self.assertIsNotNone(monocular.face_detection);
        self.assertIsNotNone(monocular.upscale);
        self.assertIsNotNone(monocular.downscale);
        self.assertIsNotNone(monocular.resize);
        self.assertIsNotNone(monocular.rotate);
        self.assertIsNotNone(monocular.flip);
        self.assertIsNotNone(monocular.crop);
    def test_images(self):
        self.assertIsNotNone(monocular.images.create);
        self.assertIsNotNone(monocular.images.delete);
        self.assertIsNotNone(monocular.images.download);
        self.assertIsNotNone(monocular.images.find_all);
        self.assertIsNotNone(monocular.images.find_one);
        self.assertIsNotNone(monocular.images.update);
        self.assertIsNotNone(monocular.images.face_detection);
        self.assertIsNotNone(monocular.images.upscale);
        self.assertIsNotNone(monocular.images.downscale);
        self.assertIsNotNone(monocular.images.resize);
        self.assertIsNotNone(monocular.images.rotate);
        self.assertIsNotNone(monocular.images.flip);
        self.assertIsNotNone(monocular.images.crop);

    def test_detectors(self):
        self.assertIsNotNone(monocular.detectors.create);
        self.assertIsNotNone(monocular.detectors.add_images);
        self.assertIsNotNone(monocular.detectors.remove_images);
        self.assertIsNotNone(monocular.detectors.find_all);
        self.assertIsNotNone(monocular.detectors.find_one);
        self.assertIsNotNone(monocular.detectors.detect);
        self.assertIsNotNone(monocular.detectors.train);

if __name__ == '__main__':
    unittest.main()
