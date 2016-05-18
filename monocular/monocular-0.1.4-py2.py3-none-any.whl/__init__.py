"""
"""
from monocular import api as api
from monocular import images as images
from monocular import detectors as detectors
from monocular import config as config
from monocular import util as util


def initialize(options):
    """
    Set the config values to the options provided.
    """
    for key, value in options.items():
        config.set(key, value)


def _validate_image(image):
    if util.validate_image(image):
        return util.produce_request_image(image)
    else:
        raise ValueError('Image must be a PIL image or path')

# Endpoints
def face_detection(options):
    """
    Detect faces in an image through the Monocular API
    """
    path = '/face-detection'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def upscale(options):
    path = '/upscale'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def downscale(options):
    path = '/downscale'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def rotate(options):
    path = '/rotate'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def resize(options):
    path = '/resize'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def flip(options):
    path = '/flip'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def crop(options):
    path = '/crop'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def erode(options):
    path = '/erode'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def dilate(options):
    path = '/dilate'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def threshold(options):
    path = '/threshold'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)

def distance_transform(options):
    path = '/distance_transform'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return api.post(path, options)
