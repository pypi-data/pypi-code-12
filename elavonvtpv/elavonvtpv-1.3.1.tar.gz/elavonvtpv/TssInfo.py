from xml.etree import ElementTree as ETree


class TssInfo:
    def __init__(self, customer_number, product_id, variable_reference, customer_ip, billing_code, billing_country,
                 shipping_code, shipping_country):
        """
        Defines a TssInfo object
        :param customer_number: number that uniquely identifies the customer among all accounts
        :param product_id: number that uniquely identifies the product among all accounts
        :param variable_reference: customer reference
        :param customer_ip: IP address used by the customer
        :param billing_code: billing postal code
        :param billing_country: country that will appear in the bill
        :param shipping_code: shipping postal code
        :param shipping_country: country which the products will be shipped to
        """
        self.customer_number = customer_number
        self.product_id = product_id
        self.variable_reference = variable_reference
        self.customer_ip = customer_ip
        self.billing_code = billing_code
        self.billing_country = billing_country
        self.shipping_code = shipping_code
        self.shipping_country = shipping_country

    def to_etree_element(self):
        """
        Transforms the TssInfo object into an ElementTree Element so it can be used in the creation of a XML
        :return: An ElmentTree Element containing the data on the TssInfo object
        """
        tss_info = ETree.Element('tssinfo')

        if self.customer_number:
            custnum = ETree.SubElement(tss_info, 'custnum')
            custnum.text = self.customer_number

        if self.product_id:
            prodid = ETree.SubElement(tss_info, 'prodid')
            prodid.text = self.product_id

        if self.variable_reference:
            varref = ETree.SubElement(tss_info, 'varref')
            varref.text = self.variable_reference

        if self.customer_ip:
            custipaddress = ETree.SubElement(tss_info, 'custipaddress')
            custipaddress.text = self.customer_ip

        if self.billing_code or self.billing_country:
            billing_address = ETree.SubElement(tss_info, 'address')
            billing_address.set('type', 'billing')

            if self.billing_code:
                billing_code = ETree.SubElement(billing_address, 'code')
                billing_code.text = self.billing_code

            if self.billing_country:
                billing_country = ETree.SubElement(billing_address, 'country')
                billing_country.text = self.billing_country

        if self.shipping_code or self.shipping_country:
            shipping_address = ETree.SubElement(tss_info, 'address')
            shipping_address.set('type', 'shipping')

            if self.shipping_code:
                shipping_code = ETree.SubElement(shipping_address, 'code')
                shipping_code.text = self.shipping_code

            if self.shipping_country:
                shipping_country = ETree.SubElement(shipping_address, 'country')
                shipping_country.text = self.shipping_country

        return tss_info
