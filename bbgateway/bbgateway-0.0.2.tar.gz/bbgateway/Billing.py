from urllib.parse import urlencode


class Billing:
    def __init__(self, first_name, last_name, company, address_1, city, state, zip, country, phone, email, address_2="",
                 fax="", website=""):
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.phone = phone
        self.fax = fax
        self.email = email
        self.website = website

    def to_dict(self):
        """
        Returns well-format dict for API POST. This is not the same as "__dict__". The keys are different.
        :return: Dict
        """
        return {
            'firstname': self.first_name,
            'lastname': self.last_name,
            'company': self.company,
            'address1': self.address_1,
            'address2': self.address_2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'country': self.country,
            'phone': self.phone,
            'fax': self.fax,
            'email': self.email,
            'website': self.website
        }

    def to_url_query_format(self):
        """
        Returns a URL query format string of all billing attributes.
        :return:  String
        """
        return urlencode(self.to_dict())
