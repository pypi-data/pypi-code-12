# -*- coding: utf-8 -*-

""" standard """
import ConfigParser
import json
from random import randint
import re
import sys

""" custom """
from threatconnect import ThreatConnect
from threatconnect.Config.FilterOperator import FilterOperator
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.RequestObject import RequestObject

# configuration file
config_file = "tc.conf"

# retrieve configuration file
config = ConfigParser.RawConfigParser()
config.read(config_file)

try:
    api_access_id = config.get('threatconnect', 'api_access_id')
    api_secret_key = config.get('threatconnect', 'api_secret_key')
    api_default_org = config.get('threatconnect', 'api_default_org')
    api_base_url = config.get('threatconnect', 'api_base_url')
    api_result_limit = int(config.get('threatconnect', 'api_result_limit'))
except ConfigParser.NoOptionError:
    print('Could not retrieve configuration file.')
    sys.exit(1)

tc = ThreatConnect(api_access_id, api_secret_key, api_default_org, api_base_url)
tc.set_api_result_limit(api_result_limit)
tc.report_enable()

""" Toggle the Boolean to enable specific examples """
enable_example1 = False
enable_example2 = False
enable_example3 = False
enable_example4 = False
owners = ['Example Community']

def show_data(result_obj):
    """  """
    tc.print_mem('before loop')
    for obj in result_obj:
        print('\n{0!s:_^80}'.format(obj.resource_type.name))
        if isinstance(obj.indicator, dict):
            for key, val in obj.indicator.items():
                print('{0!s:<20}{1!s:<50}'.format(key, val))
        else:
            print('{0!s:<20}{1!s:<50}'.format('Indicator', obj.indicator))
        print('{0!s:<20}{1!s:<50}'.format('ID', obj.id))
        print('{0!s:<20}{1!s:<50}'.format('Owner Name', obj.owner_name))
        print('{0!s:<20}{1!s:<50}'.format('Date Added', obj.date_added))
        print('{0!s:<20}{1!s:<50}'.format('Last Modified', obj.last_modified))
        print('{0!s:<20}{1!s:<50}'.format('Rating', obj.rating))
        print('{0!s:<20}{1!s:<50}'.format('TA Rating', obj.threat_assess_rating))
        print('{0!s:<20}{1!s:<50}'.format('Confidence', obj.confidence))
        print('{0!s:<20}{1!s:<50}'.format('TA Confidence', obj.threat_assess_confidence))
        print('{0!s:<20}{1!s:<50}'.format('Type', obj.type))
        print('{0!s:<20}{1!s:<50}'.format('Web Link', obj.weblink))

        #
        # api_uris
        #
        if len(obj.request_uris) > 0:
            print('\n{0!s:-^40}'.format(' Request URIs '))
            for request_uri in obj.request_uris:
                print('{0!s:<20}{1!s:<50}'.format('URI', request_uri))

        #
        # matched filters
        #
        if len(obj.matched_filters) > 0:
            print('\n{0!s:-^40}'.format(' API Matched Filters '))
            for api_filter in obj.matched_filters:
                print('{0!s:<20}{1!s:<50}'.format('Filter', api_filter))

        #
        # resource attributes
        #
        if len(obj.attributes) > 0:
            print('\n{0!s:-^40}'.format(' Attributes '))
            for attr_obj in obj.attributes:
                print('{0!s:<20}{1!s:<50}'.format('  Type', attr_obj.type))
                print('{0!s:<20}{1!s:<50}'.format('  Value', attr_obj.value))
                print('{0!s:<20}{1!s:<50}'.format('  Date Added', attr_obj.date_added))
                print('{0!s:<20}{1!s:<50}'.format('  Last Modified', attr_obj.last_modified))
                print('{0!s:<20}{1!s:<50}\n'.format('  Displayed', attr_obj.displayed))

        #
        # resource security label
        #
        obj.load_security_label()
        if obj.security_label is not None:
            print('\n{0!s:-^40}'.format(' Security Label '))
            print('{0!s:<20}{1!s:<50}'.format('  Name', obj.security_label.name))
            print('{0!s:<20}{1!s:<50}'.format('  Description', obj.security_label.description))
            print('{0!s:<20}{1!s:<50}'.format('  Date Added', obj.security_label.date_added))

        #
        # resource tags
        #
        if len(obj.tags) > 0:
            print('\n{0!s:-^40}'.format(' Tags '))
            for tag_obj in obj.tags:
                print('{0!s:<20}{1!s:<50}'.format('  Name', tag_obj.name))
                print('{0!s:<20}{1!s:<50}\n'.format('  Web Link', tag_obj.weblink))

        #
        # resource file occurrences
        #
        if obj.resource_type == ResourceType.FILES:
            obj.load_file_occurrence()
            if len(obj.file_occurrences) > 0:
                print('\n{0!s:-^40}'.format(' File Occurrence '))
                for fo_obj in obj.file_occurrences:
                    print('{0!s:<20}{1!s:<50}'.format('  File Name', fo_obj.file_name))
                    print('{0!s:<20}{1!s:<50}'.format('  Path', fo_obj.path))
                    print('{0!s:<20}{1!s:<50}\n'.format('  Date', fo_obj.date))

        #
        # resource dns resolution
        #
        if obj.resource_type == ResourceType.HOSTS:
            obj.load_dns_resolutions()
            if len(obj.dns_resolutions) > 0:
                print('\n{0!s:-^40}'.format(' DNS Resolutions '))
                for dr_obj in obj.dns_resolutions:
                    print('{0!s:<20}{1!s:<50}'.format('  IP', dr_obj.ip))
                    print('{0!s:<20}{1!s:<50}'.format('  Owner', dr_obj.owner_name))
                    print('{0!s:<20}{1!s:<50}'.format('  Resolution Date', dr_obj.resolution_date))
                    print('{0!s:<20}{1!s:<50}\n'.format('  Web Link', dr_obj.weblink))

        #
        # resource associations (indicators)
        #
        i_header = True
        for i_associations in obj.indicator_associations:
            if i_header:
                print('\n{0!s:-^40}'.format(' Indicator Associations '))
                i_header = False

            print('{0!s:<20}{1!s:<50}'.format('  ID', i_associations.id))
            print('{0!s:<20}{1!s:<50}'.format('  Indicator', i_associations.indicator))
            print('{0!s:<20}{1!s:<50}'.format('  Type', i_associations.type))
            print('{0!s:<20}{1!s:<50}'.format('  Description', i_associations.description))
            print('{0!s:<20}{1!s:<50}'.format('  Owner', i_associations.owner_name))
            print('{0!s:<20}{1!s:<50}'.format('  Rating', i_associations.rating))
            print('{0!s:<20}{1!s:<50}'.format('  Confidence', i_associations.confidence))
            print('{0!s:<20}{1!s:<50}'.format('  Date Added', i_associations.date_added))
            print('{0!s:<20}{1!s:<50}'.format('  Last Modified', i_associations.last_modified))
            print('{0!s:<20}{1!s:<50}\n'.format('  Web Link', i_associations.weblink))

        #
        # resource associations (groups)
        #
        g_header = True
        for g_associations in obj.group_associations:
            if g_header:
                print('\n{0!s:-^40}'.format(' Group Associations '))
                g_header = False

            print('{0!s:<20}{1!s:<50}'.format('  ID', g_associations.id))
            print('{0!s:<20}{1!s:<50}'.format('  Name', g_associations.name))
            if hasattr(g_associations, 'type'):
                print('{0!s:<20}{1!s:<50}'.format('  Type', g_associations.type))
            print('{0!s:<20}{1!s:<50}'.format('  Owner Name', g_associations.owner_name))
            print('{0!s:<20}{1!s:<50}'.format('  Date Added', g_associations.date_added))
            print('{0!s:<20}{1!s:<50}\n'.format('  Web Link', g_associations.weblink))

        #
        # alternate output modes
        #
        print('\n{0!s:-^40}'.format(' CEF Format '))
        print('{0!s}\n'.format(obj.cef))
        print('\n{0!s:-^40}'.format(' CSV Format '))
        print('{0!s}'.format(obj.csv_header))
        print('{0!s}\n'.format(obj.csv))
        print('\n{0!s:-^40}'.format(' JSON Format '))
        print('{0!s}\n'.format(obj.json))
        print('\n{0!s:-^40}'.format(' Key/Value Format '))
        print('{0!s}\n'.format(obj.keyval))
        print('\n{0!s:-^40}'.format(' LEEF Format '))
        print('{0!s}\n'.format(obj.leef))

    tc.print_mem('after loop')

    #
    # print report
    #
    print(tc.report.stats)


def main():
    """ """
    # set threat connect log (tcl) level
    tc.set_tcl_file('log/tc.log', 'debug')
    tc.set_tcl_console_level('critical')

    if enable_example1:
        """ get community/source status using basic retrieve """

        # build INDICATORS request object
        #
        ro = RequestObject()
        ro.set_http_method('GET')
        ro.set_owner(owners)
        ro.set_owner_allowed(True)
        ro.set_resource_pagination(True)
        ro.set_request_uri('/v2/indicators/bulk')

        #
        # retrieve and display the results
        #
        try:
            results = tc.api_request(ro)
        except RuntimeError as e:
            print(e)
            sys.exit(1)

        if results.headers['content-type'] == 'application/json':
            data = results.json()
            print(json.dumps(data, indent=4))

    if enable_example2:
        """ get bulk indicators """

        # optionally set max results
        tc.set_api_result_limit(500)

        # indicator object
        indicators = tc.bulk_indicators()

        # filter results
        try:
            filter1 = indicators.add_filter()
            filter1.add_owner(owners)
            # filter1.add_pf_confidence(90, FilterOperator.GE)
            # filter1.add_pf_date_added('2014-04-10T00:00:00Z', FilterOperator.GE)
            # filter1.add_pf_rating('4.0', FilterOperator.GE)
            # filter1.add_pf_type('Host')
            # filter1.add_pf_type('Address')
            # filter1.add_pf_last_modified('2015-01-21T00:31:44Z', FilterOperator.GE)
            # filter1.add_pf_threat_assess_confidence('50', FilterOperator.GE)
            # filter1.add_pf_threat_assess_rating('4.0', FilterOperator.GE)
            # filter1.add_pf_tag('EXAMPLE', FilterOperator.EQ)
            # filter1.add_pf_attribute('Description', FilterOperator.EQ)
        except AttributeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # retrieve indicators
        try:
            indicators.retrieve()
        except RuntimeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # show indicator data
        show_data(indicators)

    if enable_example3:
        """ get bulk indicators """

        # optionally set max results
        tc.set_api_result_limit(500)

        # indicator object
        indicators = tc.bulk_indicators()

        # filter results
        try:
            filter1 = indicators.add_filter()
            filter1.add_owner(owners)
            # filter1.add_pf_confidence(50, FilterOperator.GE)
            # filter1.add_pf_rating('2.5', FilterOperator.GE)
            filter1.add_pf_tag('CnC', FilterOperator.EQ)
        except AttributeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # retrieve indicators
        try:
            indicators.retrieve()
        except RuntimeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # show indicator data
        show_data(indicators)

    if enable_example4:
        """ get bulk indicator in csv format """

        # build INDICATORS request object
        #
        ro = RequestObject()
        ro.set_http_method('GET')
        ro.set_owner(owners)
        ro.set_owner_allowed(True)
        ro.set_resource_pagination(True)
        ro.set_request_uri('/v2/indicators/bulk/csv')

        #
        # retrieve and display the results
        #
        results = tc.api_request(ro)
        if results.headers['content-type'] == 'text/csv':
            data = results.content
            print(data)

if __name__ == "__main__":
    main()
