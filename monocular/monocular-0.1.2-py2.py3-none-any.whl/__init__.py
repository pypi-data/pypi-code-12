"""
"""
import monocular.api as Api
import monocular.images as Images
import monocular.detectors as Detectors
import monocular.config as Config
import monocular.util as Util


def initialize(options):
    """
    Set the config values to the options provided.
    """
    for key, value in options.iteritems():
        Config.set(key, value)


def _validate_image(image):
    if Util.validate_image(image):
        return Util.produce_request_image(image)
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

    return Api.post(path, options)

def upscale(options):
    path = '/upscale'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def downscale(options):
    path = '/downscale'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def rotate(options):
    path = '/rotate'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def resize(options):
    path = '/resize'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def flip(options):
    path = '/flip'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def crop(options):
    path = '/crop'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def erode(options):
    path = '/erode'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def dilate(options):
    path = '/dilate'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def threshold(options):
    path = '/threshold'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)

def distance_transform(options):
    path = '/distance_transform'

    if 'image' in options:
        options['image'] = _validate_image(options['image'])

    return Api.post(path, options)
