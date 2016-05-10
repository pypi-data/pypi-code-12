from urllib.parse import urlencode


class CreditCard:
    def __init__(self, number, expiration_date, cvv):
        """
        Defines a Credit Card object
        :param number: the credit card number
        :param expiration_date: the credit card expiration date
        :param cvv: the credit card validation code
        """
        self.number = number
        self.expiration_date = expiration_date
        self.cvv = cvv

    def to_dict(self):
        """
        Returns well-format dict for API POST. This is not the same as "__dict__". The keys are different.
        :return: Dict
        """
        return {
            'ccnumber': self.number,
            'ccexp': self.expiration_date,
            'cvv': self.cvv
        }

    def to_url_query_format(self):
        """
        Returns a URL query format string of all credit card attributes.
        :return:  String
        """
        return urlencode(self.to_dict())
