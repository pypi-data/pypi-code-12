
import io
import requests

from PIL import ExifTags, Image
from StringIO import StringIO

from utils.sdk_utils import print_and_log, INFO, DEBUG, ERROR

import sys
if (sys.version_info.major == 2 and
    (sys.version_info.minor < 7 or
     (sys.version_info.minor == 7 and sys.version_info.micro < 9))):
    # workaround for issue where https request do not work with old Python versions
    # see https://urllib3.readthedocs.io/en/latest/security.html#insecureplatformwarning
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()

class CloudRequest(object):
    FACE_SERVER_URL = 'https://mymeapi.orcam.com/face'

    @staticmethod
    def return_face_thumbnail_as_jpeg_binary(pilImage, x_perc, y_perc, w_perc, h_perc):
        cropped_w, cropped_h = pilImage.size
        x = max(int(cropped_w * x_perc), 0)
        y = max(int(cropped_h * y_perc), 0)
        w = min(int(cropped_w * w_perc), cropped_w)
        h = min(int(cropped_h * h_perc), cropped_h)

        cropped_image = pilImage.crop((x, y, x + w, y + h))
        cropped_image.thumbnail((128, 128))  # the method does mutation in place.

        # debug - show
        #cropped_image.show()

        output = io.BytesIO()
        cropped_image.save(output, format='JPEG')
        binary_data = output.getvalue()
        return binary_data

    # get piImage and return pilImage with aspect ratio of 1:1 or 4:3 or 3:4 (server requirement)
    @staticmethod
    def crop_to_correct_aspect_ratio(pilImage):
        w, h = pilImage.size
        ratio43 = 4.0 / 3.0
        ratio34 = 3.0 / 4.0
        ratio11 = 1.0
        imageRatio = float(w) / float(h)
        closest_correct_aspect = min([ratio43, ratio34, ratio11], key=lambda x: abs(x - imageRatio))

        if imageRatio == closest_correct_aspect:
            # no need to do anything
            return pilImage

        elif imageRatio > closest_correct_aspect:
            new_width = h*closest_correct_aspect
            new_height = h
        else:
            new_width = int(w)
            new_height = int(w/closest_correct_aspect)

        left = int(abs(w-new_width)/2)
        top = int(abs(h-new_height)/2)
        right = int(abs(w+new_width)/2)
        bottom = int(abs(h+new_height)/2)
        return pilImage.crop((left,top,right,bottom))

    # check exif tag and  rotated image if needed. returns pilImage
    @staticmethod
    def rotate_image_if_needed(pilImage):
        if pilImage._getexif() == None:
            return pilImage
        exif = dict((ExifTags.TAGS[k], v) for k, v in pilImage._getexif().items() if k in ExifTags.TAGS)
        if 'Orientation' not in exif.keys():
            return pilImage
        orientation = exif['Orientation']
        if orientation == 3:
            rotatedPilImage = pilImage.rotate(180, expand=True)
        elif orientation == 6:
            rotatedPilImage = pilImage.rotate(270, expand=True)
        elif orientation == 8:
            rotatedPilImage = pilImage.rotate(90, expand=True)
        else:
            rotatedPilImage = pilImage

        return rotatedPilImage

    @staticmethod
    def obtain_image_for_recognition_from_path(file_path):
        pilImage = Image.open(file_path)
        rotatedPilImage = CloudRequest.rotate_image_if_needed(pilImage)
        cropedPilImage = CloudRequest.crop_to_correct_aspect_ratio(rotatedPilImage)
        return cropedPilImage

    @staticmethod
    def obtain_image_for_recognition_from_url(url):
        response = requests.get(url)
        pilImage = Image.open(StringIO(response.content))
        rotatedPilImage = CloudRequest.rotate_image_if_needed(pilImage)
        cropedPilImage = CloudRequest.crop_to_correct_aspect_ratio(rotatedPilImage)
        return cropedPilImage

    @staticmethod
    def request_faces_sigs_from_server(pilImage):
        mem_image_file = io.BytesIO()
        pilImage.save(mem_image_file, format='JPEG')
        files = {'image': ('image.jpg', mem_image_file.getvalue(), 'image/jpeg')}
        post_response = requests.post(url=CloudRequest.FACE_SERVER_URL, files=files)
        return post_response.json()


    @staticmethod
    def get_sig_from_image_url(jpg_url):
        """
        Generates a face signature and cropped binary image of face the found at
        jpg_url

        :param jpg_url: URL to a jpeg image containing one face
        :return: On success: (face_signature, cropped_binary_image)
                 On failure: (None, None)
                 face_signature is a list of 128 ints
                 cropped_binary_image is the cropped face image in binary format (bytes)
        """
        try:
            # prepare image for sending to server (crop/rotate..)
            pil_image = CloudRequest.obtain_image_for_recognition_from_url(jpg_url)
            return CloudRequest._get_sig_from_image_helper(pil_image, jpg_url)
        except Exception as ex:
            print_and_log('ERROR trying to get image from url:{}\n{}'
                          ''.format(jpg_url, ex))
            return None, None


    @staticmethod
    def get_sig_from_image_file_path(file_path):
        """
        Generates a face signature and cropped binary image of the face found at
        file_path

        :param file_path: path to a jpeg image containing one face
        :return: On success: (face_signature, cropped_binary_image)
                 On failure: (None, None)
                 face_signature is a list of 128 ints
                 cropped_binary_image is the cropped face image in binary format (bytes)
        """
        try:
            # prepare image for sending to server (crop/rotate..)
            pil_image = CloudRequest.obtain_image_for_recognition_from_path(file_path)
            return CloudRequest._get_sig_from_image_helper(pil_image, file_path)
        except Exception as ex:
            print_and_log('ERROR trying to get image from path:{}\n{}'
                          ''.format(file_path, ex))
            return None, None


    @staticmethod
    def _get_sig_from_image_helper(pil_image, image_src):
        # send request to server
        json_reply = CloudRequest.request_faces_sigs_from_server(pil_image)

        if len(json_reply) == 0:
            print_and_log('ERROR: no face found in image at: {}'
                          ''.format(image_src), ERROR)
            return None, None

        if 'errno' in json_reply:
            print_and_log('ERROR when trying to get singature for image from '
                          'the server. errno: {}'.format(json_reply['errno']),
                          ERROR)
            return None, None


        if len(json_reply)>1:
            print_and_log('ERROR: Found {} faces in image at: {}. Feature only '
                          'works on images with one face.'
                          ''.format(len(json_reply), image_src), ERROR)
            return None,None

        # it's a for loop, but for now there is only one face supported (see check above)
        for faces_recognized in json_reply:
            image_binary = CloudRequest.return_face_thumbnail_as_jpeg_binary(
                    pil_image,
                    float(faces_recognized['position']['x']),
                    float(faces_recognized['position']['y']),
                    float(faces_recognized['position']['w']),
                    float(faces_recognized['position']['h']))

            sig = [int(x) for x in faces_recognized['signature'].split(',') if x != '']
            if len(sig) != 128:
                print_and_log('ERROR: got singature of wrong size: {} instead of '
                              '128'.format(len(sig)))
                return None, None

            return sig, image_binary
