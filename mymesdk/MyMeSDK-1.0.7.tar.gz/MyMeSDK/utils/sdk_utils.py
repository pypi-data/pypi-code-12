
import binascii
import io
import logging

from PIL import Image

from ..myme_objects import MyMeFace, MyMePerson

DEBUG = 'debug'
INFO = 'info'
ERROR = 'error'
EXCEPTION = 'exception'

verbose = False

class colors(object):
    # HIGH INTENSITY COLORS
    CYAN =   '\033[96m'
    PURPLE = '\033[95m'
    BLUE =   '\033[94m'
    YELLOW = '\033[93m'
    GREEN =  '\033[92m'
    RED =    '\033[91m'

    # REGULAR COLORS
    black =     '\033[30m'
    red =       '\033[31m'
    green =     '\033[32m'
    yellow =    '\033[33m'
    blue =      '\033[34m'
    purple =    '\033[35m'
    cyan =      '\033[36m'
    lightgrey = '\033[37m'

    # MARKINGS
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'
    END =           '\033[0m'
    REVERSE =       '\033[07m'
    STRIKETHROUGH = '\033[09m'
    INVISIBLE =     '\033[08m'
    DISABLE =       '\033[02m'


def print_and_log(message, type = 'info', bold = False, color = None,
                  logger_name = None, comma=False, use_console_only=False):
    global verbose

    if logger_name:
        main_logger = logging.getLogger(logger_name)
    else:
        main_logger = logging.getLogger()

    if (type == ERROR or type == EXCEPTION) and color == None:
        bold = True
        color = colors.RED

    #disable consosle printing for now
    if type in [ERROR, EXCEPTION] or verbose > 0:
        if bold and color:
           print color  + colors.BOLD + message + colors.END
        elif color:
           print color + message + colors.END
        elif bold:
           print colors.BOLD + message + colors.END
        else:
          print message

    if use_console_only:
        return
    # if (type == INFO):
    #     main_logger.info(message)
    # elif (type == EXCEPTION):
    #     main_logger.exception(message)
    # elif (type == ERROR):
    #     main_logger.error(message)
    # elif type == DEBUG:
    #     main_logger.debug(message)

1
def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

def int_to_bytes(num, length=0, little_endian=True):
    """
    Given an int, returns a byte array representing the int
    :param num: The number to convert
    :param length: Length of output string (will zero-pad to get to this length)
    :param little_endian: if True, will return byte array in reversed order
    :return:
    """
    if not length:
        length = len(str(num))
    h = '{:02X}'.format(num)
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s[::-1] if little_endian else s

def db_face_to_myme_face(db_face):
    return MyMeFace(id=db_face.id, detected_time=db_face.detected_time,
                    signature=db_face.get_signature(),
                    face_image=db_face.get_image(),
                    image_fetch_failed=db_face.image_fetch_failed)

def db_person_to_myme_person(db_person):
    if db_person is None:
        return None
    myme_person = MyMePerson(db_id=db_person.id,
                        name=db_person.name,
                        profile_pic=db_person.profile_pic,
                        faces=[db_face_to_myme_face(face) for
                                   face in db_person.faces])
    return myme_person

#get image_bytearray - jpeg binary content and return PIL image object
def bytearray_to_image(image_bytearray):
    if image_bytearray is None:
        return None
    image = Image.open(io.BytesIO(image_bytearray))
    return image