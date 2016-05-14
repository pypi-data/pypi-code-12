"""
"""

import monocular.api as Api
import monocular.util as Util

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
    return Api.post(path, params)

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
    return Api.post(path, params)

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
    return Api.delete(path, params)

def find_all():
    """
    Find all owned detectors.

    Usage::
        >>> detector_dict = monocular.detectors.find_all()
    """
    path = '{0}/'.format(DETECTOR_ENDPOINT)
    params = {}
    return Api.get(path, params)

def find_one(detector_id):
    """
    Find a particular detector.

    Usage::
        >>> detector = monocular.detectors.find_one(detector_id)
    """

    path = '{0}/{1}'.format(DETECTOR_ENDPOINT, detector_id)
    params = {}
    return Api.get(path, params)

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

            if Util.validate_image(image):
                params['image'] = Util.produce_request_image(image)
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

    return Api.post(path, params)

def train(detector_id):
    """
    Train a detector using its attatched images.

    Usage::
        >>> monocular.detectors.train(detector_id)
    """
    path = '{0}/{1}'.format(DETECTOR_ENDPOINT, detector_id)
    params = {}
    return Api.get(path, params)
