from urllib.parse import urlencode


class Shipping:
    def __init__(self, first_name, last_name, address_1, city, state, zip, country, email, address_2="", company=""):
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.email = email

    def to_dict(self):
        """
        Returns well-format dict for API POST. This is not the same as "__dict__". The keys are different.
        :return: Dict
        """
        return {
            'firstname': self.first_name,
            'lastname': self.last_name,
            'country': self.country,
            'address1': self.address_1,
            'address2': self.address_2 or "-",
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'email': self.email,
            'company': self.company
        }

    def to_url_query_format(self):
        """
        Returns a URL query format string of all shipping attributes.
        :return:  String
        """
        return urlencode(self.to_dict())
