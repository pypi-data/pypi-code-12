from __future__ import print_function
from foundation_platform.messaging import restAPIClient
import json
import uuid


class imageHandler(object):
    """imageHandler."""

    def __init__(self, image_data):
        """__init__"""
        self.type = "IMAGE"
        self.image_data = image_data
        try:
            self.id = self.get_uuid()
        except Exception:
            raise
        try:
            self.request = self.set_request_params()
        except Exception:
            raise
        # self.printarg()
        try:
            self.generate_message()
        except Exception:
            raise

    def printarg(self):
        """Method printarg."""
        print(self.id)
        print(self.type)
        # print self.request
        print(self.image_data)

    def get_uuid(self):
        """_get_uuid """
        return str(uuid.uuid4())

    def is_image_local(self):
        """_is_image_local"""
        if self.image_data.get('ip') == "localhost":
            return True
        return False

    def set_request_params(self):
        """_create_request """
        req_params = {}
        req_params.update(command="image-create")
        req_params.update(file=self.image_data.get('url'))
        req_params.update(location=self.image_data.get('url'))
        req_params.update(name=self.image_data.get('name'))
        req_params["disk-format"] = "qcow2"
        return req_params

    def generate_message(self):
        message = self.__dict__
        message = json.loads(restAPIClient.obj_to_JSON(message))
        restAPIClient.restAPIClient(message)


''' this is used just for local testing'''


def main():
    image_data_test = {"url": "http://135.1.219.10/templates/redhat7-v2.qcow2",
                       "name": "redhat7-v2",
                       "ip": "135.1.219.10"}
    imageHandler(image_data_test)


if __name__ == '__main__':
    main()
