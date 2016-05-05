from PIL import Image
import io
import requests
from PIL import ExifTags
from utils.sdk_utils import print_and_log, INFO, DEBUG, ERROR

class CloudRequest(object):
    FACE_SERVER_URL = 'http://52.37.219.107/face'

    @staticmethod
    def return_face_thumbnail_as_jpeg_binary(pilImage, x_perc, y_perc, w_perc, h_perc):
        original_w, origial_h = pilImage.size
        x = max(int(original_w * x_perc), 0)
        y = max(int(origial_h * y_perc), 0)
        w = min(int(original_w * w_perc), original_w)
        h = min(int(origial_h * h_perc), origial_h)

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
            croppedImage = pilImage.crop((0, 0, int(h * closest_correct_aspect), h))
        else:
            croppedImage = pilImage.crop((0, 0, w, int(w / closest_correct_aspect)))
        return croppedImage

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
    def obtain_image_for_recognition(file_path):
        pilImage = Image.open(file_path)
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
    def get_sig_from_image_file_path(file_path):
        """
        given a file path, returns the face signature for it and cropped binary image
        None,None is returned in case of errors

        :param file_path: given
        :return: face_signature,  (list of 128 integers),
                 cropped_binary_image - the cropped face image in binary format
        """

        # prepare image for sending to server (crop/rotate..)
        pilImage = CloudRequest.obtain_image_for_recognition(file_path)

        # send request to server
        json_reply = CloudRequest.request_faces_sigs_from_server(pilImage)

        if len(json_reply) == 0:
            print_and_log('ERROR: no face found in image {}'.
                          format(file_path), ERROR)
            return None, None

        if len(json_reply)>1:

            print_and_log('ERROR: more than 1 faces found in image {} {}'.
                          format(file_path, len(json_reply.faces_recognized)), ERROR)
            return None,None

        # it's a for loop, but for now there is only one face supported (see check above)
        for faces_recognized in json_reply:
            image_binary = CloudRequest.return_face_thumbnail_as_jpeg_binary \
                (pilImage,
                 float(faces_recognized['position']['x']),
                 float(faces_recognized['position']['y']),
                 float(faces_recognized['position']['w']),
                 float(faces_recognized['position']['h']))
            sig = [int(x) for x in faces_recognized['signature'].split(',') if x != '']
            print sig
            assert (len(sig) == 128)
            return sig, image_binary
