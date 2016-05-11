from urllib.parse import urlencode


class Order:
    """
    Defines a Order that can be converted to Dict with the appropriate format for API POST.
    """
    def __init__(self, reference, description, amount, ip_address=None):
        """
        Constructor
        :param reference: order identifier
        :param description: order description
        :param amount: total amount of the order
        :param ip_address: requester IP
        """
        self.reference = reference
        self.description = description
        self.amount = amount
        self.ip_address = ip_address

    def to_dict(self):
        """
        Returns well-format dict for API POST. This is not the same as "__dict__". The keys are different.
        :return: Dict
        """
        data = {
            'orderid': self.reference,
            'orderdescription': self.description,
            'amount': self.amount,
        }
        if self.ip_address:
            data['ipaddress'] = self.ip_address,
        return data

    def to_url_query_format(self):
        """
        Returns a URL query format string of all order attributes.
        :return:  String
        """
        return urlencode(self.to_dict())
