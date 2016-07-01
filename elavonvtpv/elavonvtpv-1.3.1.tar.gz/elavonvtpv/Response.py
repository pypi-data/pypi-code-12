from xml.etree import ElementTree as Etree
import hashlib


class Response:
    def __init__(self, xml):
        """
        Defines a Response object
        :param xml: a string containing xml data
        """
        self.__xml = Etree.fromstring(xml)

    def __getattr__(self, item):
        """
        Search unidentified attributes inside the ElementTree structure inside the __xml attribute.
        :param item: the name of the requested attribute
        :return: the content of the first tag named item in the ElementTree structure
        """
        return self.__xml.find(item).text

    def __hash(self):
        """
        Builds the response hash from the data contained within
        :return: the hash string that will latter be cyphered
        """
        res = "%s.%s.%s.%s.%s.%s.%s" % (str(self.timestamp), str(self.merchant_id), str(self.order_id), str(self.result)
                                        , str(self.message), str(self.pas_ref), str(self.auth_code))
        return res.encode('utf-8')

    def __sha1_hash(self, secret):
        """
        returns a secure hash in SHA-1 for this response
        :param secret: the shared secret between Elavon and your account
        :return: secure hash in SHA-1
        """
        sha1_hash = hashlib.sha1(self.__hash()).hexdigest()
        sha1_hash += ".%s" % secret

        return hashlib.sha1(sha1_hash.encode('utf-8')).digest()

    def validate_origin(self, secret):
        """
        validates the request hash to check if the response was really sent by Elavon
        :param secret: the shared secret between Elavon and your account
        :return: a boolean value indicating the validity of the response hash
        """
        try:
            return self.sha1hash is self.__sha1_hash(secret)
        except AttributeError:
            return False
