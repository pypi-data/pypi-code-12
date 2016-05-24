# -*- coding: utf-8 -*-
"""
    koalacompanies.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Company profile module. The model is geared towards ecommerce type systems which need multiple addresses.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import koalacore
from google.appengine.ext import ndb


__author__ = 'Matt Badger'


class Company(koalacore.Resource):
    company_name = koalacore.ResourceProperty(title=u'Company Name')
    contact_first_name = koalacore.ResourceProperty(title=u'Contact First Name')
    contact_last_name = koalacore.ResourceProperty(title=u'Contact Last Name')
    contact_email = koalacore.ResourceProperty(title=u'Contact Email')
    contact_phone = koalacore.ResourceProperty(title=u'Contact Phone')
    contact_mobile = koalacore.ResourceProperty(title=u'Contact Mobile')
    # Addresses
    delivery_address_1 = koalacore.ResourceProperty(title=u'Delivery Address 1')
    delivery_address_2 = koalacore.ResourceProperty(title=u'Delivery Address 2')
    delivery_address_3 = koalacore.ResourceProperty(title=u'Delivery Address 3')
    delivery_city = koalacore.ResourceProperty(title=u'Delivery City')
    delivery_county = koalacore.ResourceProperty(title=u'Delivery County')
    delivery_state = koalacore.ResourceProperty(title=u'Delivery State')
    delivery_post_code = koalacore.ResourceProperty(title=u'Delivery Post Code')
    delivery_country = koalacore.ResourceProperty(title=u'Delivery Country')
    billing_address_1 = koalacore.ResourceProperty(title=u'Billing Address 1')
    billing_address_2 = koalacore.ResourceProperty(title=u'Billing Address 2')
    billing_address_3 = koalacore.ResourceProperty(title=u'Billing Address 3')
    billing_city = koalacore.ResourceProperty(title=u'Billing City')
    billing_county = koalacore.ResourceProperty(title=u'Billing County')
    billing_state = koalacore.ResourceProperty(title=u'Billing State')
    billing_post_code = koalacore.ResourceProperty(title=u'Billing Post Code')
    billing_country = koalacore.ResourceProperty(title=u'Billing Country')

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.atom_field(name='company_name', value=self.company_name),
            koalacore.GAESearchInterface.atom_field(name='contact_first_name', value=self.contact_first_name),
            koalacore.GAESearchInterface.atom_field(name='contact_last_name', value=self.contact_last_name),
            koalacore.GAESearchInterface.atom_field(name='contact_email', value=self.contact_email),
            koalacore.GAESearchInterface.atom_field(name='contact_phone', value=self.contact_phone),
            koalacore.GAESearchInterface.atom_field(name='contact_mobile', value=self.contact_mobile),
            koalacore.GAESearchInterface.atom_field(name='delivery_address_1', value=self.delivery_address_1),
            koalacore.GAESearchInterface.atom_field(name='delivery_address_2', value=self.delivery_address_2),
            koalacore.GAESearchInterface.atom_field(name='delivery_address_3', value=self.delivery_address_3),
            koalacore.GAESearchInterface.atom_field(name='delivery_city', value=self.delivery_city),
            koalacore.GAESearchInterface.atom_field(name='delivery_county', value=self.delivery_county),
            koalacore.GAESearchInterface.atom_field(name='delivery_state', value=self.delivery_state),
            koalacore.GAESearchInterface.atom_field(name='delivery_post_code', value=self.delivery_post_code),
            koalacore.GAESearchInterface.atom_field(name='delivery_country', value=self.delivery_country),
            koalacore.GAESearchInterface.atom_field(name='billing_address_1', value=self.billing_address_1),
            koalacore.GAESearchInterface.atom_field(name='billing_address_2', value=self.billing_address_2),
            koalacore.GAESearchInterface.atom_field(name='billing_address_3', value=self.billing_address_3),
            koalacore.GAESearchInterface.atom_field(name='billing_city', value=self.billing_city),
            koalacore.GAESearchInterface.atom_field(name='billing_county', value=self.billing_county),
            koalacore.GAESearchInterface.atom_field(name='billing_state', value=self.billing_state),
            koalacore.GAESearchInterface.atom_field(name='billing_post_code', value=self.billing_post_code),
            koalacore.GAESearchInterface.atom_field(name='billing_country', value=self.billing_country),
            koalacore.GAESearchInterface.text_field(name='fuzzy_company_name',
                                                value=koalacore.generate_autocomplete_tokens(
                                                        original_string=self.company_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_contact_first_name',
                                                value=koalacore.generate_autocomplete_tokens(
                                                    original_string=self.contact_first_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_contact_last_name',
                                                value=koalacore.generate_autocomplete_tokens(
                                                    original_string=self.contact_last_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_contact_email',
                                                value=koalacore.generate_autocomplete_tokens(
                                                        original_string=self.contact_email)),

        ]


class NDBCompany(koalacore.NDBResource):
    company_name = ndb.StringProperty('cn', indexed=False)
    contact_first_name = ndb.StringProperty('pcfn', indexed=False)
    contact_last_name = ndb.StringProperty('pcln', indexed=False)
    contact_email = ndb.StringProperty('pce', indexed=False)
    contact_phone = ndb.StringProperty('pcp', indexed=False)
    contact_mobile = ndb.StringProperty('pcm', indexed=False)
    delivery_address_1 = ndb.StringProperty('dad1', indexed=False)
    delivery_address_2 = ndb.StringProperty('dad2', indexed=False)
    delivery_address_3 = ndb.StringProperty('dad3', indexed=False)
    delivery_city = ndb.StringProperty('dcty', indexed=False)
    delivery_county = ndb.StringProperty('dcnty', indexed=False)
    delivery_state = ndb.StringProperty('dcntys', indexed=False)
    delivery_post_code = ndb.StringProperty('dpc', indexed=False)
    delivery_country = ndb.StringProperty('dcntry', default='GB', indexed=False)
    billing_address_1 = ndb.StringProperty('bad1', indexed=False)
    billing_address_2 = ndb.StringProperty('bad2', indexed=False)
    billing_address_3 = ndb.StringProperty('bad3', indexed=False)
    billing_city = ndb.StringProperty('bcty', indexed=False)
    billing_county = ndb.StringProperty('bcnty', indexed=False)
    billing_state = ndb.StringProperty('bcntys', indexed=False)
    billing_post_code = ndb.StringProperty('bpc', indexed=False)
    billing_country = ndb.StringProperty('bcntry', default='GB', indexed=False)


class CompanySearchInterface(koalacore.GAESearchInterface):
    _index_name = 'companies'


class CompanyNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBCompany
    _resource_object = Company


class Companies(koalacore.BaseAPI):
    _api_name = 'company'
    _api_model = Company
    _datastore_interface = CompanyNDBInterface
    _search_interface = CompanySearchInterface
