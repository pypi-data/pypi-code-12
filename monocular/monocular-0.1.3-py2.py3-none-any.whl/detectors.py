from monocular import api, util

DETECTOR_ENDPOINT='/detectors'

def create(label):
    """
    Created a detector.

    Usage::
        >>> detector = monocular.detectors.create(label)
    """
    path = '{0}/'.format(DETECTOR_ENDPOINT)
    params = {
        'label': label
    }
    return api.post(path, params)

def add_images(detector_id, image_ids):
    """
    Add multiple images to a detector.

    Usage::
        >>> monocular.detectors.add_images(detector_id, image_ids)
    """
    path = '{0}/{1}/images/'.format(DETECTOR_ENDPOINT, detector_id)
    params = {
        'data': image_ids
    }
    return api.post(path, params)

def remove_images(detector_id, image_ids):
    """
    Remove images from a detector.

    Usage::
        >>> monocular.detectors.remove_images(detector_id, image_ids)
    """
    path = '{0}/{1}/images/'.format(DETECTOR_ENDPOINT, detector_id)
    params = {
        'data': image_ids
    }
    return api.delete(path, params)

def find_all():
    """
    Find all owned detectors.

    Usage::
        >>> detector_dict = monocular.detectors.find_all()
    """
    path = '{0}/'.format(DETECTOR_ENDPOINT)
    params = {}
    return api.get(path, params)

def find_one(detector_id):
    """
    Find a particular detector.

    Usage::
        >>> detector = monocular.detectors.find_one(detector_id)
    """

    path = '{0}/{1}'.format(DETECTOR_ENDPOINT, detector_id)
    params = {}
    return api.get(path, params)

def detect(detector_id, **kwargs):
    """
    Run a detector on an image.

    Usage::
        >>> boxes = monocular.detectors.detect(detector_id, image)
    """
    path = '{0}/{1}/detect'.format(DETECTOR_ENDPOINT, detector_id)
    params = {}
    if kwargs is not None:
        if 'image' in kwargs:
            image = kwargs.get('image')

            if util.validate_image(image):
                params['image'] = util.produce_request_image(image)
            else:
                raise ValueError('Image must be a PIL image')

        elif 'url' in kwargs:
            params['url'] = kwargs.get('url')
        elif 'image_id' in kwargs:
            path = '{0}/{1}/detect/{2}'.format(DETECTOR_ENDPOINT, detector_id, image_id)
        else:
            raise TypeError('Missing required keyword argument image or url')
    else:
        raise TypeError('Missing required keyword argument image or url')

    return api.post(path, params)

def train(detector_id):
    """
    Train a detector using its attatched images.

    Usage::
        >>> monocular.detectors.train(detector_id)
    """
    path = '{0}/{1}'.format(DETECTOR_ENDPOINT, detector_id)
    params = {}
    return api.get(path, params)
