

class MyMeFace(object):

    id = None
    """ MyMeFace ID """

    detected_time = None
    """ detected time - datetime.time object"""

    face_image = None
    """ face image - PIL.Image object"""

    image_fetch_failed = False

    def __init__(self, id=None, detected_time=None, signature=None,
                 face_image=None, image_fetch_failed=False):
        """
        :param db: Id of the face in the SDK Faces database
        :param detected_time: Time when face was detected (datetime object)
        :param signature: Face's signature (array of 128 ints)
        :param face_image: PIL image object holding the face image
        :param image_fetch_failed: True if was unable to fetch face image after
        """
        self.id = id
        self.detected_time = detected_time
        self.signature=signature
        self.face_image = face_image
        self.image_fetch_failed = image_fetch_failed

class MyMePerson(object):
    db_id = None
    name = None
    profile_pic = None
    faces = None
    def __init__(self, db_id, name, profile_pic, faces):
        """
        :param db_id: Id of the person in the SDK People database
        :param name: Person's name
        :param profile_pic: Person's picture
        :param faces: List of faces (MyMeFace objects) belonging to the Person
        """
        self.db_id = db_id
        self.name = name
        self.profile_pic = profile_pic
        self.faces = faces

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
