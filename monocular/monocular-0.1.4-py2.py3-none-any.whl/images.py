from monocular import api as api
from monocular import util as util

IMAGE_ENDPOINT = '/images'


def create(image, options):
    """
    Validate an image and upload it.

    Usage::
        >>> monocular.image.create(image, options)
    """
    path = '{0}'.format(IMAGE_ENDPOINT)
    if util.validate_image(image):
        options['image'] = util.produce_request_image(image)

        response = api.post(path, options)

        return response
    else:
        raise ValueError('Image must be a PIL Image')


def delete(image_id):
    """
    Delete an image.

    Usage::
        >>> monocular.image.delete(image_id)
    """
    path = '{0}/{1}'.format(IMAGE_ENDPOINT, image_id)
    return api.delete(path, {})


def download(image_id):
    """
    Download an image.

    Usage::
        >>> image = monocular.image.download(image_id)
    """
    path = '{0}/{1}/download'.format(IMAGE_ENDPOINT, image_id)
    return api.get(IMAGE_ENDPOINT + '/' + image_id + '/download', {})


def find_all():
    """
    Find all owned images.

    Usage::
        >>> image_dict = monocular.image.find_all()
    """
    path = '{0}'.format(IMAGE_ENDPOINT)
    return api.get(IMAGE_ENDPOINT, {})


def find_one(image_id):
    """
    Find a particular image.

    Usage::
        >>> image_data = monocular.image.find_one(image_id)
    """

    return api.get(IMAGE_ENDPOINT + '/' + image_id, {})


def update(image_id, options):
    """
    Update a particular image.

    Usage::
        >>> monocular.image.update(image_id, box_data)
    """
    path = '{0}/{1}'.format(IMAGE_ENDPOINT, image_id)
    return api.put(IMAGE_ENDPOINT + '/' + image_id, options)

# Endpoints
def face_detection(image_id, landmarks=False):
    """
    Perform face detection on image.

    Usage::
        >>> faces = monocular.image.face_detection(image_id, landmarks)
    """
    path = '{0}/{1}/face-detection'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'landmarks': landmarks
    }

    return api.post(path, params)

def upscale(image_id, encode_type=None, save=False):
    """
    Upscale an image to twice its original size.

    Usage::
        >>> image = monocular.image.upscale(image_id, encode_type, save)
    """

    path = '{0}/{1}/upscale'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'encodeType': encode_type,
        'save': save
    }

    return api.post(path, params)

def downscale(image_id, encode_type=None, save=False):
    """
    Downscale an image to half of its original size.

    Usage::
        >>> image = monocular.image.downscale(image_id, encode_type, save)
    """
    path = '{0}/{1}/downscale'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def resize(image_id, width, height, encode_type=None, save=False):
    """
    Resize an image to a given size.

    'encode_type' and 'save' are optional

    Usage::
        >>> image = monocular.image.resize(image_id, width, height, encode_type, save)
    """
    path = '{0}/{1}/resize'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'width': width,
        'height': height
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def rotate(image_id, angle, encode_type=None, save=False):
    """
    Rotate an image by a given number of degrees.
    """

    path = '{0}/{1}/rotate'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'angle': angle
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def crop(image_id, top, left, bottom, right, encode_type=None,  save=False):
    path = '{0}/{1}/crop'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'top': top,
        'left': left,
        'bottom': bottom,
        'right': right
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def flip(image_id, vertical=False, horizontal=False, encode_type=None, save=False):
    path = '{0}/{1}/flip'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'vertical': vertical,
        'horizontal': horizontal
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def distance_transform(image_id, distance_type, encode_type=None, save=False):
    path = '{0}/{1}/distance_transform'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'distanceType': distance_type,
        'maskSize': mask_size
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def erode(image_id, kernel_shape, kernel_size, kernel_anchor, anchor, iterations, border_type, encode_type=None, save=False):
    path = '{0}/{1}/erode'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'kernelShape': kernel_shape,
        'kernelSize': kernel_size,
        'kernelAnchor': kernel_anchor,
        'anchor': anchor,
        'iterations': iterations,
        'borderType': border_type
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)

def dilate(image_id, kernel_shape, kernel_size, kernel_anchor, anchor, iterations, border_type, encode_type=None, save=False):
    path = '{0}/{1}/erode'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'kernelShape': kernel_shape,
        'kernelSize': kernel_size,
        'kernelAnchor': kernel_anchor,
        'anchor': anchor,
        'iterations': iterations,
        'borderType': border_type
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)


def threshold(image_id, threshold_type, threshold, max_size, encode_type=None, save=False):
    path = '{0}/{1}/flip'.format(IMAGE_ENDPOINT, image_id)
    params = {
        'save': save,
        'thresholdType': threshold_type,
        'threshold': threshold,
        'max': max_size
    }

    if encode_type:
        params['encodeType'] = encode_type

    return api.post(path, params)
