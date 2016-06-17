# -*- coding: utf-8 -*-

""" standard """
import ConfigParser
from datetime import datetime
from random import randint
import re
import sys

""" custom """
from threatconnect import ThreatConnect
from threatconnect.Config.ResourceType import ResourceType

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

#
# CHANGE FOR YOUR TESTING ENVIRONMENT
# - These indicators must be created before running this script
#
owner = 'Example Community'  # org or community
lu_indicator = '10.20.30.40'  # indicators for loop update
mu_indicator = '40.20.30.10'  # indicators id for manual update
adversary_id = 5  # email resource id to associate with indicator
prefixes = {
    'ip': '4.3.254',
    'email': 'badguy',
    'file': 'BAD',
    'host': 'www.badguy',
    'url': 'http://www.badguy'}
rn = randint(1, 100)  # random number generator for testing


def main():
    """ """
    # set threat connect log (tcl) level
    tc.set_tcl_file('log/tc.log', 'debug')
    tc.set_tcl_console_level('critical')
    tc.report_enable()

    # (Required) Instantiate a Resource Object
    resources = tc.indicators()

    # (Optional) Filters can be added here if required to narrow the result set.
    try:
        filter1 = resources.add_filter()
        filter1.add_owner(owner)
    except AttributeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    # (Optional) retrieve all results
    try:
        resources.retrieve()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    # (Optional) iterate through all results if retrieve was used above
    for res in resources:

        # (Optional) match a particular resource by ID, Name or any other supported attribute.
        if lu_indicator == res.indicator or lu_indicator in res.indicator:
            #
            # update resource if required
            #
            res.set_confidence(rn)
            res.set_rating(randint(0, 5))
            res.set_description('Test Description {0:d}'.format(randint(0, 5)))
            res.delete_security_label('TLP Red')
            res.set_security_label('TLP Red')

            #
            # working with indicator associations
            #

            # indicator to indicator associations can be retrieved, but NOT directly associated,

            #
            # working with group associations
            #

            # (Optional) get all group associations
            for association in res.group_associations:
                # add delete flag to all group association that match DELETE
                if re.findall('Loop', association.name):
                    res.disassociate_group(association.resource_type, association.id)

            res.associate_group(ResourceType.ADVERSARIES, adversary_id)

            #
            # working with victim associations
            #

            # (Optional) get all victim associations
            # resources.victim_associations(res)
            # for association in res.association_objects_victims:
            #     print(association)

            #
            # working with attributes
            #
            # (Optional) get all attributes associated with this resource
            res.load_attributes()
            for attribute in res.attributes:
                # add delete flag to all attributes that have 'test' in the value.
                if re.findall('DELETE', attribute.value):
                    res.delete_attribute(attribute.id)
                # add update flag to all attributes that have 'update' in the value.
                if attribute.type == 'Source' and re.findall('UPDATE', attribute.value):
                    res.update_attribute(attribute.id, 'UPDATE Test Attribute %s' % rn)
            # (Optional) add attribute to resource with type and value
            res.add_attribute('Additional Analysis and Context', 'DELETE Test Attribute %s' % rn)

            #
            # working with tags
            #

            # (Optional) get all tags associated with this resource
            res.load_tags()
            for tag in res.tags:
                # add delete flag to all tags that have 'DELETE' in the name.
                if re.findall('DELETE', tag.name):
                    res.delete_tag(tag.name)
            # (Optional) add tag to resource
            res.add_tag('DELETE {0:d}'.format(rn))
            res.add_tag('EXAMPLE')

            # commit changes
            try:
                print('Updating resource {0!s}.'.format(res.indicator))
                res.commit()
            except RuntimeError as e:
                print('Error: {0!s}'.format(e))
                sys.exit(1)

        #
        # delete resource
        #

        # (Optional) add delete flag to previously created indicators
        if isinstance(res.indicator, dict):
            for k, v in res.indicator.items():
                if v is not None and re.findall(prefixes['file'], v):
                    print('Delete resource {0!s}.'.format(res.indicator))
                    res.delete()
                    break
        else:
            for k, v in prefixes.items():
                if re.findall(v, res.indicator):
                    print('Delete resource {0!s}.'.format(res.indicator))
                    res.delete()
                    break

    #
    # add address indicator
    #

    # this requires that the resource was instantiated at the beginning of the script.
    resource = resources.add('4.3.254.{0:d}'.format(rn), owner)
    resource.set_confidence(rn)
    resource.set_rating(randint(1, 5))

    # (Optional) add attribute to newly created resource
    resource.add_attribute('Description', 'TEST attribute #{0:d}'.format(rn))

    # (Optional) add tag to newly created resource
    resource.add_tag('TAG #{0:d}'.format(rn))
    resource.add_tag('EXAMPLE')

    # (Optional) set security label to newly created resource
    resource.set_security_label('TLP Green')

    try:
        print('Adding resource {0!s}.'.format(resource.indicator))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    #
    # add email address indicator
    #

    # this requires that the resource was instantiated at the beginning of the script.
    resource = resources.add('{0!s}_{1!s}@badguysareus.com'.format(prefixes['email'], str(rn).zfill(3)), owner)
    resource.set_confidence(rn)
    resource.set_rating(randint(1, 5))

    # (Optional) add attribute to newly created resource
    resource.add_attribute('Description', 'TEST attribute #{0:d}'.format(rn))

    # (Optional) add tag to newly created resource
    resource.add_tag('TAG #{0:d}'.format(rn))
    resource.add_tag('EXAMPLE')

    # (Optional) set security label to newly created resource
    resource.set_security_label('TLP Green')

    try:
        print('Adding resource {0!s}.'.format(resource.indicator))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    #
    # add file indicator
    #

    # this requires that the resource was instantiated at the beginning of the script.
    resource = resources.add('{0!s}1ba81f1dc6d3637589ffa04366{1!s}'.format(
        prefixes['file'], str(rn).zfill(3)), owner)
    resource.set_indicator('{0!s}530f8e0104d4521958309eb9852e073150{1!s}'.format(
        prefixes['file'], str(rn).zfill(3)))
    resource.set_indicator('{0!s}10a665da94445f5b505c828d532886541900373d29042cc46c3300a186{1!s}'.format(
        prefixes['file'], str(rn).zfill(3)))

    resource.set_confidence(rn)
    resource.set_rating(randint(1, 5))
    resource.set_size(rn)
    fo_date = (datetime.isoformat(datetime(2015, randint(1, 12), randint(1, 29)))) + 'Z'
    resource.add_file_occurrence('badfile_{0!s}.exe'.format(rn), 'C:\windows', fo_date)

    # (Optional) add attribute to newly created resource
    resource.add_attribute('Description', 'TEST attribute #{0:d}'.format(rn))

    # (Optional) add tag to newly created resource
    resource.add_tag('TAG #{0:d}'.format(rn))
    resource.add_tag('EXAMPLE')

    # (Optional) set security label to newly created resource
    resource.set_security_label('TLP Green')

    try:
        print('Adding resource {0!s}.'.format(resource.indicator))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    #
    # add host indicator
    #

    # this requires that the resource was instantiated at the beginning of the script.
    resource = resources.add('{0!s}_{1!s}.com'.format(prefixes['host'], str(rn).zfill(3)), owner)

    resource.set_confidence(rn)
    resource.set_rating(randint(1, 5))

    # (Optional) add attribute to newly created resource
    resource.add_attribute('Description', 'TEST attribute #{0:d}'.format(rn))

    # (Optional) add tag to newly created resource
    resource.add_tag('TAG #{0:d}'.format(rn))
    resource.add_tag('EXAMPLE')

    # (Optional) set security label to newly created resource
    resource.set_security_label('TLP Green')

    try:
        print('Adding resource {0!s}.'.format(resource.indicator))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    #
    # add url indicator
    #

    # this requires that the resource was instantiated at the beginning of the script.
    resource = resources.add('{0!s}_{1!s}.com/clickme.html'.format(
        prefixes['url'], str(rn).zfill(3)), owner)

    resource.set_confidence(rn)
    resource.set_rating(randint(1, 5))

    # (Optional) add attribute to newly created resource
    resource.add_attribute('Description', 'TEST attribute #{0:d}'.format(rn))

    # (Optional) add tag to newly created resource
    resource.add_tag('TAG #{0:d}'.format(rn))
    resource.add_tag('EXAMPLE')

    # (Optional) set security label to newly created resource
    resource.set_security_label('TLP Green')

    try:
        print('Adding resource {0!s}.'.format(resource.indicator))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    # (Optional) display a commit report of all API actions performed
    print(tc.report.stats)

    # display any failed api calls
    for fail in tc.report.failures:
        print(fail)

if __name__ == "__main__":
    main()
    sys.exit()
