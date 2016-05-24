# coding=utf-8
"""
Tipsa API
"""
__copyright__ = 'Copyright 2015, Abalt'

from datetime import date
import requests
import xmltodict

WEBSERVICE_URL = 'http://webservices.tipsa-dinapaq.com:8099/SOAP'

DETAILS_URL = 'http://dinapaqweb.tipsa-dinapaq.com:8085/dinapaqweb/detalle_envio.php?servicio=%(guid)s&fecha=%(date)s'

LOGIN_PARAMS = {'service': 'LoginWSservice'}

LOGIN_XML = u"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
       <soap:Body>
           <LoginWSService___LoginCli>
               <strCodAge>%(agency_code)s</strCodAge>
               <strCod>%(client_code)s</strCod>
               <strPass>%(client_password)s</strPass>
           </LoginWSService___LoginCli>
       </soap:Body>
    </soap:Envelope>"""

CREATE_PARAMS = {'service': 'WebServService'}

CREATE_XML = u"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
       <soap:Header>
           <ROClientIDHeader xmlns="http://tempuri.org/">
               <ID>%(guid)s</ID>
           </ROClientIDHeader>
       </soap:Header>
       <soap:Body>
           <WebServService___GrabaEnvio4 xmlns="http://tempuri.org/">
               <strCodAgeCargo>%(cargo_agency_code)s</strCodAgeCargo>
               <strCodAgeOri>%(origin_agency_code)s</strCodAgeOri>
               <dtFecha>%(date)s</dtFecha>
               <strCodTipoServ>%(service_code)s</strCodTipoServ>
               <strCodCli>%(client_code)s</strCodCli>
               <strNomOri>%(origin_name)s</strNomOri>
               <strNomDes>%(destination_name)s</strNomDes>
               <strDirDes>%(destination_address)s</strDirDes>
               <strPobDes>%(destination_city)s</strPobDes>
               <strCPDes>%(destination_postal_code)s</strCPDes>
               <strTlfDes>%(destination_phone)s</strTlfDes>
               <strObs>%(notes)s</strObs>
               <intPaq>%(int_paq)s</intPaq>
               <dPesoOri>%(origin_weight)s</dPesoOri>
               <boInsert>%(insert)s</boInsert>
               <strRef>%(reference)s</strRef>
               <boDesEmail>%(email_notification)s</boDesEmail>
               <strDesDirEmails>%(email)s</strDesDirEmails>
           </WebServService___GrabaEnvio4>
       </soap:Body>
    </soap:Envelope>"""


class TipsaAPI(object):
    agency_code = ''
    client_code = ''
    client_password = ''
    guid = ''

    create_mandatory_params = ['service_code', 'destination_name', 'destination_address', 'destination_postal_code']

    def __init__(self, agency_code, client_code, client_password):
        self.agency_code = agency_code
        self.client_code = client_code
        self.client_password = client_password

    def _make_request(self, params, payload):
        response = requests.request('POST', WEBSERVICE_URL, data=payload,
                                    headers={'cache-control': 'no-cache',
                                             'content-type': 'text/xml; charset=utf8'},
                                    params=params)
        response_dict = xmltodict.parse(response.content)
        return response_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']

    def login(self):
        payload = LOGIN_XML % (
            {
                'agency_code': self.agency_code,
                'client_code': self.client_code,
                'client_password': self.client_password
            }
        )
        payload = payload.encode('utf-8')
        response_dict = self._make_request(LOGIN_PARAMS, payload)
        self.guid = response_dict['v1:LoginWSService___LoginCliResponse']['v1:strSesion']

    def create(self, params_dict):
        today = date.today()

        request_dict = {
            'guid': self.guid,
            'cargo_agency_code': self.agency_code,
            'origin_agency_code': self.agency_code,
            'date': today.strftime('%Y/%m/%d'),
            'client_code': self.client_code,
            'origin_name': '',
            'destination_city': '',
            'destination_phone': '',
            'notes': '',
            'int_paq': 1,
            'origin_weight': 1,
            'insert': 1,
            'reference': '',
            'email_notification': '0',
            'email': ''
        }
        request_dict.update(params_dict)

        for param in self.create_mandatory_params:
            if param not in request_dict:
                raise Exception('You must define a %s' % param)

        if str(request_dict['service_code']) not in ['14', '48', '10', 'MV', '20']:
            raise Exception('Incorrect service_code')

        payload = CREATE_XML % request_dict
        payload = payload.encode('utf-8')
        response_dict = self._make_request(CREATE_PARAMS, payload)
        albaran = response_dict['v1:WebServService___GrabaEnvio4Response']['v1:strAlbaranOut']
        guid = response_dict['v1:WebServService___GrabaEnvio4Response']['v1:strGuidOut']
        return {
            'albaran': albaran,
            'guid': guid,
            'url': DETAILS_URL % {'guid': guid, 'date': today.strftime('%d/%m/%Y')}
        }
