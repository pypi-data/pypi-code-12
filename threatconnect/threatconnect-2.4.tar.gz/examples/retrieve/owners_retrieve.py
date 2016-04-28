# -*- coding: utf-8 -*-

""" standard """
import ConfigParser
from random import randint
import sys

""" custom """
from threatconnect import ThreatConnect
from threatconnect.Config.FilterOperator import FilterSetOperator

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

""" Get Owners """
enable_example1 = False
enable_example2 = False
enable_example3 = False


# shared method to display results from examples below
def show_data(result_obj):
    """  """
    for obj in result_obj:
        print('\n{0!s:_^80}'.format(obj.name))
        print('{0!s:<20}{1!s:<50}'.format('ID', obj.id))
        print('{0!s:<20}{1!s:<50}'.format('Type', obj.type))

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
    # print report
    #
    print(tc.report.stats)


def main():
    """ """
    # set threat connect log (tcl) level
    tc.set_tcl_file('log/tc.log', 'debug')
    tc.set_tcl_console_level('critical')

    if enable_example1:
        """ This is a basic example that pull all owners. """
        # optionally set the max results the api should return in one request
        tc.set_api_result_limit(500)

        # get owner object
        owners = tc.owners()

        # retrieve owners
        try:
            owners.retrieve()
        except RuntimeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # show owner data
        show_data(owners)

    if enable_example2:
        """ This example retrieves all owners that a particular indicator appears. """

        # get owner object
        owners = tc.owners()

        # filter results
        try:
            filter1 = owners.add_filter()
            filter1.add_indicator('10.20.30.40')
            filter1.add_pf_name('Example Community')
            filter1.add_pf_type('Community')  # Organization, Community, Source
        except AttributeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # retrieve owners
        try:
            owners.retrieve()
        except RuntimeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # show owner data
        show_data(owners)

    """
    Method:
    get_owners() ->  This method can be used to get a object containing owners filtered by indicator.
    """
    if enable_example3:

        # get owner object
        owners = tc.owners()

        # filter results
        try:
            filter1 = owners.add_filter()
            filter1.add_indicator('10.20.30.40')
        except AttributeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        try:
            filter2 = owners.add_filter()
            filter2.add_filter_operator(FilterSetOperator.AND)
            filter2.add_indicator('notsobad@gmail.com')
        except AttributeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # retrieve owners
        try:
            owners.retrieve()
        except AttributeError as e:
            print('Error: {0!s}'.format(e))
            sys.exit(1)

        # show owner data
        show_data(owners)

if __name__ == "__main__":
    main()
