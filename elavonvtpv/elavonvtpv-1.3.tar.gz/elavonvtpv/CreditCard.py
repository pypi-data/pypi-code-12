from elavonvtpv.enum import CVNIndicator
from xml.etree import ElementTree as ETree


class CreditCard:
    def __init__(self, cvn_indicator, number, expiry, name, card_type, cvn=None):
        """
        Defines a CreditCard object
        :param cvn_indicator: CVNIndicator enum object indicating the presence or lack of thereof of the cvn
        :param number: the credit card number
        :param expiry: the credit card expiration date
        :param name: the name of the credit card titular
        :param card_type: CardType enum object indicating the type of the credit card
        :param cvn: the credit card validation code
        """
        self.cvn_indicator = cvn_indicator
        self.number = number
        self.expiry = expiry
        self.name = name
        self.card_type = card_type
        self.cvn = cvn

    def to_etree_element(self):
        """
        Transforms the CreditCard object into an ElementTree Element so it can be used in the creation of a XML
        :return: An ElmentTree Element containing the data on the CreditCard object
        """
        card = ETree.Element('card')

        presind = ETree.SubElement(card, 'presind')
        presind.text = self.cvn_indicator.value

        number = ETree.SubElement(card, 'number')
        number.text = self.number

        expdate = ETree.SubElement(card, 'expdate')
        expdate.text = self.expiry

        chname = ETree.SubElement(card, 'chname')
        chname.text = self.name

        card_type = ETree.SubElement(card, 'type')
        card_type.text = self.card_type.value

        if self.cvn_indicator == CVNIndicator.present:
            cvn = ETree.SubElement(card, 'cvn')
            cvn__number = ETree.SubElement(cvn, 'number')
            cvn__number.text = self.cvn

        return card
