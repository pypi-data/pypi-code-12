
import base64
import cStringIO
import datetime

from base64 import decodestring
from PIL import Image


def PIL_image_to_base64(pil_img):
    if pil_img is None:
        return ""
    buffer = cStringIO.StringIO()
    pil_img.save(buffer, format=pil_img.format)
    return base64.b64encode(buffer.getvalue())


def base64_to_PIL_Image(base64_str):
    if base64_str is None:
        return None

    decoded_str = cStringIO.StringIO(base64.b64decode(base64_str))
    return Image.open(decoded_str)


class MyMeFace(object):
    """
    Represents a DbFace object in the SDK database
    """

    id = None
    """ MyMeFace ID """

    detected_time = None
    """ Time detected - datetime.time object """

    signature = None
    """ Face's signature (array of 128 ints) """

    def __init__(self, id=None, detected_time=None, signature=None):
        """
        :param db: Id of the face in the SDK Faces database
        :param detected_time: Time when face was detected (datetime object)
        :param signature: Face's signature (array of 128 ints)
        """
        self.id = id
        self.detected_time = detected_time
        self.signature=signature


class MyMeFaceImage(object):
    """
    Represents a DbFaceImage object in the SDK Database
    """
    id = None
    """ Id of the corresponding DbFaceImage object in the SDK DB """

    detected_time = None
    """ Time detected - datetime.time object """

    image = None
    """ face image - PIL.Image object containing the face image """

    def __init__(self, id=None, detected_time=None, image=None, face_id=None):
        """
        :param id: Id of the corresponding DbFaceImage object in the SDK DB
        :param detected_time: time when face contained in image was detected
        :param image: PIL image object containing the face image
        :param face_id: Id of the face to which the image belongs
        :return:
        """
        self.id = id
        self.detected_time = detected_time
        self.image = image
        self.face_id = face_id


    def to_dict(self):
        obj_dict = dict()
        obj_dict['id'] = self.id
        obj_dict['detected_time'] = self.detected_time.strftime('%s')
        obj_dict['image'] = PIL_image_to_base64(self.image)
        return obj_dict


    @staticmethod
    def dict_to_face_image(face_img_dict):
        if face_img_dict is None:
            return None
        fi = MyMeFaceImage()
        fi.id = face_img_dict.get('id')
        timestamp = int(face_img_dict.get('detected_time'))
        fi.detected_time = datetime.datetime.fromtimestamp(timestamp)
        fi.image = base64_to_PIL_Image(face_img_dict.get('image'))
        return fi


class MyMePerson(object):
    """
    Represents a person in the SDK database which has a collection of images
    and face signatures.
    """

    id = None
    """ Id of the corresponding DbPerson object in the SDK DB """

    name = None
    """ Name of the person, if set using :func:`MyMeSDK.api.set_name_to_person`,
    None otherwise """

    profile_picture = None
    """ Profile picture of the person (PIL Image object), if set using
    :func:`MyMeSDK.api.set_profile_picture`, None otherwise
    """

    images = None
    """ list of :class:`MyMeSDK.myme_objects.MyMeFaceImage` objects corresponding
    to face images that have been fetched and stored for this person
    """

    def __init__(self, id=None, name=None, profile_picture=None, images=None):
        """
        :param db_id: Id of the person in the SDK People database
        :param name: Person's name
        :param profile_picture: Person's picture (PIL Image object)
        :param images: List of images (MyMeFaceImage objects) that
                            that have been fetched and saved for this person
        """
        self.id = id
        self.name = name
        self.profile_picture = profile_picture
        self.images = images

    def to_dict(self):
        obj_dict = dict()
        obj_dict['id'] = self.id
        obj_dict['name'] = self.name
        obj_dict['profile_picture'] = PIL_image_to_base64(self.profile_picture)
        obj_dict['images'] = [face_img.to_dict() for face_img in self.images]
        return obj_dict

    @staticmethod
    def dict_to_person(p_dict):
        if p_dict is None:
            return None
        p = MyMePerson()
        p.id = p_dict.get('id')
        p.name = p_dict.get('name')
        p.profile_picture = base64_to_PIL_Image(p_dict.get('profile_picture'))
        p.images = [MyMeFaceImage.dict_to_face_image(face_img_dict)
                    for face_img_dict in p_dict.get('images')]
        return p

class BoundingBox(object):

    x = 0
    """ top left corner of the bounding box - x value"""

    def __init__(self, x, y, w, h):
        """
         All coordinates (x,y,w,h) are floating point numbers between 0 and 1
         which correspond to normalized locations on the full image.
         On a normalized image, the top left corner is treated as (x=0, y=0)
         and the bottom left corner is treated as (x=1, y=1)

         :param x: top left corner of the bounding box - x value
         :param y: top left corner of the bounding box - y value
         :param w: width of the bounding box
         :param h: heigth of the boudning box
         """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class OcrLine(object):
    """ Represents an OCR line detected """

    text = None
    """text: UTF8 string containing a line of text found in the image"""

    def __init__(self, text, bounding_box):
        self.text = text
        self.bounding_box = bounding_box

class MyMeImage(object):

    def __init__(self, frame_idx, detected_time=None, full_image=None):
        """
        :param frame_idx: Frame index of image
        :param detected_time: Time when image was taken (datetime object)
        :param full_image: PIL object containing the image
        """
        self.frame_idx = frame_idx
        self.detected_time = detected_time
        self.full_image = full_image
