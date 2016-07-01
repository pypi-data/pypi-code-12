from xml.etree import ElementTree as Etree
from xml.dom import minidom
from elavonvtpv.enum import RequestType
from elavonvtpv.Response import Response
import datetime
import hashlib
import requests


class Request:
    def __init__(self, secret, request_type, merchant_id, order_id, currency=None, amount=None, card=None,
                 tss_info=None, settle=True, account=None, channel=None, comment1=None, comment2=None,
                 past_reference=None, authorization_code=None, refund_hash=None):
        """
        Defines a Request object
        :param secret: the shared secret between Elavon and your account
        :param request_type: RequestType enum object containing the type of the request to be sent to Elavon
        :param merchant_id: the credentials of the elavon merchant account
        :param order_id: number unique to the request for all accounts associated with the merchant
        :param currency: Currency enum object containing the code of the currency to be use in the transaction
        :param amount: amount of currency to be charged, in the smallest unit of currency possible
        :param card: CreditCard object containing the data pertaining to the customer's credit card
        :param tss_info: TssInfo object containing the data pertaining to the anti-fraud system
        :param settle: flag indicating if the transaction must be settled automatically by Elavon
        :param account: the sub-account to be used for the request
        :param channel: Channel enum object indicating the channel by which the transaction is made
        :param comment1: optional comment to include in the request
        :param comment2: optional comment to include in the request
        :param past_reference: reference of the transaction to which this one refers
        :param authorization_code: authorization code given with the transaction to which this one refers
        :param refund_hash: hash provided by Elavon, needed to make refunds
        """
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.secret = secret
        self.request_type = request_type
        self.merchant_id = merchant_id
        self.order_id = order_id
        self.currency = currency
        self.amount = amount
        self.card = card
        self.tss_info = tss_info
        self.settle = settle
        self.account = account
        self.channel = channel
        self.comment1 = comment1
        self.comment2 = comment2
        self.past_reference = past_reference
        self.authorization_code = authorization_code
        self.refund_hash = refund_hash

    def __hash(self):
        """
        Builds the request hash from the data contained within
        :return: the hash string that will latter be cyphered
        """
        res = "%s.%s.%s.%s.%s" % (str(self.timestamp), str(self.merchant_id), str(self.order_id), str(self.amount),
                                  str(self.currency.value))
        if self.card:
            res += ".%s" % str(self.card.number)

        return res.encode('utf-8')

    def sha1_hash(self):
        """
        returns a secure hash in SHA-1 for this request
        :return: secure hash in SHA-1
        """
        sha1_hash = hashlib.sha1(self.__hash()).hexdigest()
        sha1_hash += ".%s" % self.secret

        return hashlib.sha1(sha1_hash.encode('utf-8')).hexdigest()
        # return hashlib.sha1(self.__hash()).hexdigest()

    def md5_hash(self):
        """
        returns a secure hash in MD5 for this request
        :return: secure hash in MD5
        """
        md5_hash = hashlib.md5(self.__hash()).hexdigest()
        md5_hash += ".%s" % self.secret

        return hashlib.md5(md5_hash.encode('utf-8')).digest()

    def __basic_to_etree_element(self):
        """
        creates the basic structure of an Elavon request
        :return: the basic root element of the request containing those fields that exist en every request type
        """
        request = Etree.Element('request')
        request.set('timestamp', self.timestamp)
        request.set('type', self.request_type.name)

        merchant_id = Etree.SubElement(request, 'merchantid')
        merchant_id.text = self.merchant_id

        if self.account:
            account = Etree.SubElement(request, 'account')
            account.text = self.account

        order_id = Etree.SubElement(request, 'orderid')
        order_id.text = self.order_id

        return request

    def __channel_to_etree_element(self):

        channel = Etree.Element('channel')
        channel.text = self.channel.value

        return channel

    def __past_reference_to_etree_element(self):

        past_reference = Etree.Element('pasref')
        past_reference.text = self.past_reference

        return past_reference

    def __authorization_code_to_etree_element(self):

        authorization_code = Etree.Element('authcode')
        authorization_code.text = self.past_reference

        return authorization_code

    def __amount_to_etree_element(self):

        amount = Etree.Element('amount')
        amount.set('currency', self.currency.value)
        amount.text = self.amount

        return amount

    def __auto_settle_to_etree_element(self):

        auto_settle = Etree.Element('autosettle')
        auto_settle.set('flag', '1' if self.settle else '0')

        return auto_settle

    def __comments_to_etree_element(self):
        comments = Etree.Element('comments')

        if self.comment1:
            comment1 = Etree.SubElement(comments, 'comment', id='1')
            comment1.text = self.comment1
        if self.comment2:
            comment2 = Etree.SubElement(comments, 'comment', id='2')
            comment2.text = self.comment2

        return comments

    def __sh1_hash_to_etree_element(self):

        sha1_hash = Etree.Element('sha1hash')
        sha1_hash.text = self.sha1_hash()

        return sha1_hash

    def __md5_hash_to_etree_element(self):

        md5_hash = Etree.Element('md5hash')
        md5_hash.text = self.md5_hash()

        return md5_hash

    def __auth_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__channel_to_etree_element())
        request.append(self.__amount_to_etree_element())
        request.append(self.card.to_etree_element())
        request.append(self.__auto_settle_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        if self.tss_info:
            request.append(self.tss_info.to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __manual_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__channel_to_etree_element())
        request.append(self.__authorization_code_to_etree_element())
        request.append(self.__amount_to_etree_element())
        request.append(self.card.to_etree_element())
        request.append(self.__auto_settle_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        if self.tss_info:
            request.append(self.tss_info.to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __obt_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.card.to_etree_element())
        request.append(self.__auto_settle_to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __offline_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__past_reference_to_etree_element())
        request.append(self.__authorization_code_to_etree_element())
        request.append(self.__amount_to_etree_element())
        request.append(self.card.to_etree_element())
        request.append(self.__auto_settle_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        if self.tss_info:
            request.append(self.tss_info.to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __rebate_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__past_reference_to_etree_element())
        request.append(self.__authorization_code_to_etree_element())
        request.append(self.__amount_to_etree_element())
        request.append(self.__auto_settle_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __void_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__past_reference_to_etree_element())
        request.append(self.card.to_etree_element())
        request.append(self.__authorization_code_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __tss_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__amount_to_etree_element())
        request.append(self.card.to_etree_element())
        request.append(self.__auto_settle_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        if self.tss_info:
            request.append(self.tss_info.to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __settle_to_etree(self):
        request = self.__basic_to_etree_element()
        request.append(self.__past_reference_to_etree_element())
        if self.amount and self.currency:
            request.append(self.__amount_to_etree_element())
        request.append(self.__authorization_code_to_etree_element())
        if self.comment1 or self.comment2:
            request.append(self.__comments_to_etree_element())
        request.append(self.__sh1_hash_to_etree_element())
        # request.append(self.__md5_hash_to_etree_element())

        return Etree.ElementTree(request)

    def __to_etree(self):
        if self.request_type is RequestType.auth:
            return self.__auth_to_etree()
        elif self.request_type is RequestType.manual:
            return self.__manual_to_etree()
        elif self.request_type is RequestType.obt:
            return self.__obt_to_etree()
        elif self.request_type is RequestType.offline:
            return self.__offline_to_etree()
        elif self.request_type is RequestType.rebate:
            return self.__rebate_to_etree()
        elif self.request_type is RequestType.void:
            return self.__void_to_etree()
        elif self.request_type is RequestType.TSS:
            return self.__tss_to_etree()
        elif self.request_type is RequestType.settle:
            return self.__settle_to_etree()

    def to_xml_string(self):
        binary = Etree.tostring(self.__to_etree().getroot(), encoding='utf8', method='xml')
        return binary.decode('utf-8')

    def to_pretty_xml(self):
        return minidom.parseString(self.to_xml_string()).toprettyxml()

    def send(self, url):
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url=url, data=self.to_pretty_xml(), headers=headers)
        return Response(response.content)
