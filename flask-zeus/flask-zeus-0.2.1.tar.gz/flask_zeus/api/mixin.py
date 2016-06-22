from flask import current_app
from PIL import Image
from io import StringIO
import qiniu


class UploadMixin(object):

    @staticmethod
    def get_img_size(data):
        try:
            s = StringIO()
            s.write(data)
            img = Image.open(s)
            width = img.width
            height = img.height
        except Exception as e:
            width = 0
            height = 0

        return width, height

    @staticmethod
    def put_data(filename, data):
        q = qiniu.Auth(current_app.config.get('QINIU_AK'), current_app.config.get('QINIU_SK'))
        token = q.upload_token(current_app.config.get('QINIU_BUKET'))
        ret, info = qiniu.put_data(token, filename, data)
        return ret, info