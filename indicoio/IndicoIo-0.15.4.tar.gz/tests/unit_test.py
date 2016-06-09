from indicoio.utils.image import image_preprocess
from PIL import Image
import os, unittest, base64
from six import BytesIO

DIR = os.path.dirname(os.path.realpath(__file__))

class ResizeTests(unittest.TestCase):
    """
    test image resizing
    """
    def test_min_axis_resize(self):
        test_image = os.path.normpath(os.path.join(DIR, "data/fear.png"))
        resized_image = image_preprocess(test_image, size=360, min_axis=True)
        image_string = BytesIO(base64.b64decode(resized_image))
        image = Image.open(image_string)
        self.assertEqual(image.size, (360.0, 360.0))
