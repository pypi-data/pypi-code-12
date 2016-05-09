from urllib.parse import urlencode


class Order:
    """
    Defines a Order that can be converted to Dict with the appropriate format for API POST.
    """
    def __init__(self, reference, description, tax, shipping_price, po_number, ip_address, amount):
        """
        Constructor
        :param reference: order identifier
        :param description: order description
        :param tax: order amount without shipping price
        :param shipping_price: shipping specific price
        :param po_number: PO number
        :param ip_address: requester IP
        :param amount: total amount of the order
        """
        self.reference = reference
        self.description = description
        self.tax = '{0:.2f}'.format(float(tax))
        self.shipping_price = '{0:.2f}'.format(float(shipping_price))
        self.po_number = po_number
        self.ip_address = ip_address
        self.amount = amount,

    def to_dict(self):
        """
        Returns well-format dict for API POST. This is not the same as "__dict__". The keys are different.
        :return: Dict
        """
        return {
            'orderid': self.reference,
            'orderdescription': self.description,
            'shipping': self.shipping_price,
            'ipaddress': self.ip_address,
            'tax': self.tax,
            'ponumber': self.po_number,
            'amount': self.amount,
        }

    def to_url_query_format(self):
        """
        Returns a URL query format string of all order attributes.
        :return:  String
        """
        return urlencode(self.to_dict())
