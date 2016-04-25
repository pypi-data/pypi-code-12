# -*- coding: utf-8 -*-
__author__ = 'dsedad'

from lxml import etree as et
from uuid import uuid4
from decimal import Decimal
import datetime
from tzlocal import get_localzone
import os


class Signer(object):

    def __init__(self, directory, cert_private, cert_public, timezone, cert_ca, cert_ca_crl):
        self.directory = directory
        self.cert_private = cert_private
        self.cert_public = cert_public
        self.timezone = timezone
        self.cert_ca = cert_ca
        self.cert_ca_crl = cert_ca_crl

    @staticmethod
    def dummy_event(*args, **kwargs):
        import json
        result = json.dumps(args, kwargs)
        return result

    def sign(self, key_password, source, destination, myevent=None):
        from ixmldsig import IXmlDSig
        from lxml import etree as et
        from capi import load as capi_load
        import json
        import gzip
        import codecs

        try:
            source = os.path.join(self.directory, source)
            destination = os.path.join(self.directory, destination)

            capi = capi_load(mode='sign', key_password=key_password, cert_private=self.cert_private, cert_public=self.cert_public)
            ixmldsig = IXmlDSig(sign_fn=capi.createSignature, get_dn=capi.extractSubjectDN, tz=self.timezone,
                                cert_file=self.cert_public)

            if myevent is None:
                myevent = Signer.dummy_event

            xml_in_ext = os.path.splitext(source)[1]

            # Load .gz or xml
            if xml_in_ext.lower() == '.gz':
                xml_in = gzip.open(source, 'rb')
            else:
                xml_in = codecs.open(source, 'r', encoding='utf-8')

            xml_out_ext = os.path.splitext(destination)[1]
            if xml_out_ext.lower() == '.gz':
                xml_out = gzip.open(destination, 'wb')
            else:
                xml_out = codecs.open(destination, 'w', encoding='utf-8')

            # Parse tree
            tree = et.parse(xml_in)
            root = tree.getroot()

            # Find invoices tag
            xml_invoices = root.find('invoices')

            # Write header
            xml_out.write('<envelope format="' + root.attrib['format'] + '">')
            xml_out.write("<invoices>")

            assert xml_invoices is not None, u'<invoices> tag ne postoji'

            all_invoices = xml_invoices.findall('invoice')
            all_cnt = xml_invoices.findall('invoice').__len__()
            cnt = 0
            for invoice in all_invoices:
                cnt += 1
                signed = ixmldsig.sign(invoice)
                xml_out.write(signed.encode('utf-8'))
                pct = int(100.0 * float(cnt)/float(all_cnt))
                yield myevent(str(pct))

        except Exception as e:
            yield myevent(u'<h3>Greška pri potpisivanju</h3> {}\nERR'.format(e), 1, True)

        else:
            xml_out.write('</invoices>')
            summary_signed = ixmldsig.sign_summary()
            xml_out.write(summary_signed.encode('utf-8'))
            xml_out.write('</envelope>')
            sign_result = {'timestamp': ixmldsig.summary['timestamp'],
                           'cnt': ixmldsig.summary['cnt'],
                           'sum': ixmldsig.summary['sum'],
                           'file': '/invoices/'+os.path.basename(xml_out.name)}
            sign_result_json = json.dumps(sign_result)
            yield myevent(sign_result_json, 0, True)

        finally:
            try:
                xml_out.flush()
                xml_out.close()
                xml_in.close()
            except:
                pass

    def verify(self, source, myevent=None):
        from ixmldsig import IXmlDSig
        from lxml import etree as et
        import json
        import gzip
        import codecs
        from capi import load as capi_load

        try:
            source = os.path.join(self.directory, source)
            capi = capi_load(mode='verify', cert_ca=self.cert_ca, cert_ca_crl=self.cert_ca_crl)
            ixmldsig = IXmlDSig(verify_fn=capi.verifySignature)
            if myevent is None:
                myevent = Signer.dummy_event

            xml_in_ext = os.path.splitext(source)[1]

            # Load .gz or xml
            if xml_in_ext.lower() == '.gz':
                xml_in = gzip.open(source, 'rb')
            else:
                xml_in = codecs.open(source, 'r', encoding='utf-8')

            tree = et.parse(xml_in)
            root = tree.getroot()

            # Find invoices tag
            xml_invoices = root.find('invoices')

            assert xml_invoices is not None, u'<invoices> tag ne postoji'

            all_invoices = xml_invoices.findall('invoice')
            all_cnt = xml_invoices.findall('invoice').__len__()
            cnt = 0
            for invoice in all_invoices:
                verified = ixmldsig.verify(invoice)
                if not verified:
                    for exc in ixmldsig.verify_exceptions:
                        assert False, u'<br>PROBLEM: Pogrešan potpis e-računa, r.br.: {}, uuID: {}<br>DETALJI: {}'\
                            .format(ixmldsig.inv_cnt, exc['uuid'], unicode(exc['exception']))
                else:
                    cnt += 1
                    pct = int(100.0 * float(cnt)/float(all_cnt))
                yield myevent(str(pct))

        except Exception as e:
            yield myevent(u'<h3>Greška pri verifikaciji</h3> {}<br>ERR'.format(e), 1, True)
        else:
            summary = root.find('summary')
            try:
                result = ixmldsig.verify_summary(summary)
                verify_result = {'timestamp': ixmldsig.summary['timestamp'],
                                 'cnt': str(ixmldsig.summary['cnt']),
                                 'sum': str(ixmldsig.summary['sum'])}

                verify_result_json = json.dumps(verify_result)

                yield myevent(verify_result_json, 0, True)

            except Exception as e:
                yield myevent(u'<br>PROBLEM: Pogrešan potpis SUMMARY<br>  DETALJI:<br>{}<br>ERR'.format(unicode(e)), 1, True)

def convert_dn(dnstr):
    """
     Convert DN X509 string to dictionary
     example input: 'CN=4200040010007, O="\\"PING\\" d.o.o. Sarajevo", L=Sarajevo, ST=FBiH, C=BA'
    """
    def unquote(str):
        import re
        str = str.decode('string-escape')
        matched = re.match(r'^\"(.*)\"$', str)
        if matched:
            return matched.group(1)
        else:
            return str

    dn1 = dnstr.split(',')
    result = {}
    for elem in dn1:
        elem = elem.lstrip()
        eq_pos = elem.index('=')
        result[elem[:eq_pos]]=unquote(elem[eq_pos+1:])
    return result

class IXmlDSig(object):
    """
    Sign invoice file or single invoice.
    """
    def __init__(self, sign_fn=None, verify_fn=None, get_dn=None, cert_file=None, tz = get_localzone()):
        """
        sign_fn: xmldsig signature function
        verify_fn: xmldsig signature function
        tz: timezone
        """
        self.sign_fn = sign_fn
        self.verify_fn = verify_fn
        self.get_dn = get_dn
        self.init_summary()
        self.tz = tz
        if cert_file:
            self.sign_dn = self.get_subjectDN(cert_file)

    def init_summary(self):
        self.__last_dn = None
        self.uuid_list = []
        self.inv_sum = Decimal(0)
        self.inv_cnt = 0
        self.last_uuid = None
        self.verify_exceptions = []
        self.timestamp = None
        self.summary = {}

    def verify_dn(self, ent_id, ent_name):
        assert ent_id != None, u"Ne postoji id tag"
        assert self.sign_dn['CN'] == ent_id.text, u"Pogresan id preduzeca: \"{}\"".format(ent_id.text)

        assert ent_name != None, u"Ne postoji name tag"
        assert self.sign_dn['O'] == ent_name.text, u"Pogresan naziv preduzeca: \"{}\"".format(ent_name.text)

    def get_subjectDN(self, cert_file):
        pem_cert_file = open(cert_file, 'r')
        cert = pem_cert_file.read()
        pem_cert_file.close()

        return convert_dn(self.get_dn(cert))

    def sign(self, invoice):
        """
         Sign invoice xml and return signed xml (as string)
        """
        if type(invoice) in (type(unicode()), type(str())):
            invoice = et.fromstring(invoice)

        uuid = et.SubElement(invoice, "uuid")
        uuid.text = str(uuid4())

        timestamp = et.SubElement(invoice, "timestamp")
        timestamp.text = str(datetime.datetime.now(self.tz).isoformat())

        self.last_uuid = uuid.text

        # Add uuid to list of uuids
        self.uuid_list.append(uuid.text)

        # Find amount, ent_id, ent_name
        amount = invoice.find('header').find('pay').find('amount')
        ent_id = invoice.find("header").find("payee").find("id")
        ent_name = invoice.find("header").find("payee").find("short_name")

        # Check DN
        # self.verify_dn(ent_id, ent_name)

        # Calc sum & count
        self.inv_sum = self.inv_sum + Decimal(amount.text)
        self.inv_cnt = self.inv_cnt + 1

        # Sign and write
        invoice_str = et.tostring(invoice, encoding='utf8', method='xml', pretty_print = True)
        return self.sign_fn(invoice_str).encode("utf-8")

    def verify(self, invoice):
        """
         Verify invoice xml
        """
        if type(invoice) in (type(unicode()), type(str())):
            invoice = et.fromstring(invoice)
        amount = invoice.find('header').find('pay').find('amount')

        inv_date_str = invoice.find('header').find('date').text
        inv_date_str = inv_date_str[:10]
        inv_date = datetime.datetime.strptime(inv_date_str, '%Y-%m-%d').date()

        # Calc sum & count
        self.inv_sum = self.inv_sum + Decimal(amount.text)
        self.inv_cnt = self.inv_cnt + 1

        # Populate uuid in uuid_list
        uuid_tag = invoice.find('uuid')
        assert uuid_tag != None, u"Invoice ne posjeduje uuid tag"

        uuid_tag = uuid_tag.text
        self.uuid_list.append(uuid_tag)

        # Verify invoice signature
        invoice_str = unicode(et.tostring(invoice))
        try:
            dn_str = self.verify_fn(invoice_str, None, inv_date)
            assert dn_str == self.__last_dn or self.__last_dn == None, u"Greska! Postoje razliciti DN-ovi u invoice datoteci"
            self.__last_dn = dn_str

            dn = convert_dn(dn_str)

            payee_proxy_signer = invoice.find("header").find("payee_proxy_signer")
            if payee_proxy_signer is not None:
                payee_proxy_signer_id = payee_proxy_signer.find("id")
                assert payee_proxy_signer_id is not None, u"Ne postoji id tag proxy potpisnika"
                assert dn['CN'] == payee_proxy_signer_id.text, u"Pogresan id proxy potpisnika: \"{}\"".format(payee_proxy_signer_id.text)

                ent_name = payee_proxy_signer.find("short_name")
                assert ent_name is not None, u"Ne postoji name tag proxy potpisnika"
                assert dn['O'] == ent_name.text, u"Pogresan naziv proxy potpisnika: \"{}\"".format(ent_name.text)
            else:
                ent_id = invoice.find("header").find("payee").find("id")
                assert ent_id != None, u"Ne postoji id tag"
                assert dn['CN'] == ent_id.text, u"Pogresan id preduzeca: \"{}\"".format(ent_id.text)

                ent_name = invoice.find("header").find("payee").find("short_name")
                assert ent_name != None, u"Ne postoji name tag"
                assert dn['O'] == ent_name.text, u"Pogresan naziv preduzeca: \"{}\"".format(ent_name.text)

            return True
        except Exception as e:
            self.verify_exceptions.append({"uuid": uuid_tag, "exception": e})
            return False

    def sign_summary(self):
        summary = et.Element("summary")
        count = et.SubElement(summary, "count")
        count.text = str(self.inv_cnt)
        sum = et.SubElement(summary, "sum")
        sum.text = str(self.inv_sum)
        uuids = et.SubElement(summary, "uuids")
        uuids.text = ','.join(self.uuid_list)
        timestamp = et.SubElement(summary, "timestamp")
        timestamp.text = str(datetime.datetime.now(self.tz).isoformat())

        # Sign summary
        summary_src = et.tostring(summary, encoding='utf8', pretty_print = True)
        summary_signed = self.sign_fn(summary_src)
        self.summary = {"sum": sum.text, "cnt": count.text, "uuids": uuids.text, "timestamp": timestamp.text}
        return summary_signed.encode("utf-8")

    def verify_summary(self, summary):
        """
        Verify invoices summary
        """
        if type(summary) in (type(unicode()), type(str())):
            summary = et.fromstring(summary)

        sum = Decimal(summary.find('sum').text)
        count = int(summary.find('count').text)
        uuids = summary.find('uuids').text
        timestamp = summary.find('timestamp').text
        timestamp_date = datetime.datetime.strptime(timestamp[:10], '%Y-%m-%d').date()

        self.summary = {"sum": sum, "cnt": count, "uuids": uuids, "timestamp": timestamp}

        assert sum == self.inv_sum, u"PROBLEM: Potpisana suma {} <> sume racuna {}".format(sum, self.inv_sum)
        assert count == self.inv_cnt, u"PROBLEM: Potpisani broj racuna {} <> broja racuna {}".format(count, self.inv_cnt)
        assert uuids == ",".join(self.uuid_list), u"PROBLEM: UUID racuna ne odgovaraju onim u kontrolnom bloku"

        summary_str = unicode(et.tostring(summary))
        try:
            dn_str = self.verify_fn(summary_str, None, timestamp_date)
            assert dn_str == self.__last_dn or self.__last_dn == None, \
                u"Greska! Postoje razliciti DN-ovi u invoice datoteci"
            self.__last_dn = dn_str

        except Exception as e:
            raise Exception(u'Greška provjere summary potpisa. Detalji: {}'.format(e.errmsg))

        return True

