# -*- coding: utf-8 -*-

""" standard """
import ConfigParser
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
# - These threats must be created before running this script
#
owner = 'Example Community'  # org or community
lu_id = 38  # threat id for loop update
mu_id = 39  # threat id for manual update
# dl_id = 999999  # threat id to delete
adversary_id = 5  # adversary resource id to associate with threat
victim_id = 1  # victim resource id to associate with threat
ip_address = '10.20.30.40'  # ip address to associate to threat
rn = randint(1, 1000)  # random number generator for testing


def main():
    """ """
    # (Optional) SET THREAT CONNECT LOG (TCL) LEVEL
    tc.set_tcl_file('log/tc.log', 'debug')
    tc.set_tcl_console_level('critical')

    # (Required) Instantiate a Resource Object
    resources = tc.threats()

    #
    # (Optional) retrieve results from API and update selected resource in loop
    #

    # filters can be set to limit search results
    try:
        filter1 = resources.add_filter()
        filter1.add_owner(owner)  # filter on owner
    except AttributeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    try:
        resources.retrieve()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    for res in resources:

        # a particular resource can be matched by ID, Name or any other supported attribute
        if res.id == lu_id:
            #
            # once a resource is matched any metadata on that resource can be updated
            #
            res.set_name('LU Threat #{0:d}'.format(rn))

            #
            # working with indicator associations
            #

            # existing indicator associations can be retrieved and iterated through
            for association in res.indicator_associations:
                # add delete flag to all indicator association that have a confidence under 10
                if association.confidence < 10:
                    res.disassociate_indicator(association.resource_type, association.indicator)

            # indicator associations can be added to a resource by providing the resource type and value
            res.associate_indicator(ResourceType.ADDRESSES, ip_address)

            #
            # working with group associations
            #

            # existing group associations can be retrieved and iterated through
            for association in res.group_associations:
                # add delete flag to all group association that match DELETE
                if re.findall('LU', association.name):
                    res.disassociate_group(association.resource_type, association.id)

            # group associations can be added to a resource by providing the resource type and id
            res.associate_group(ResourceType.ADVERSARIES, adversary_id)

            #
            # working with victim associations
            #

            # existing victim associations can be retrieved and iterated through
            for association in res.victim_associations:
                # add delete flag to all group association that match DELETE
                if re.findall('LU', association.name):
                    res.disassociate_victim(association.id)

            # victim associations can be added to a resource by providing the resource id
            res.associate_victim(victim_id)

            #
            # working with attributes
            #

            # existing attributes can be loaded into the resource and iterated through
            res.load_attributes()
            for attribute in res.attributes:
                # add delete flag to all attributes that have 'test' in the value.
                if re.findall('test', attribute.value):
                    res.delete_attribute(attribute.id)
                # add update flag to all attributes that have 'update' in the value.
                if re.findall('update', attribute.value):
                    res.update_attribute(attribute.id, 'updated attribute #{0:d}'.format(rn))

            # attributes can be added to a resource by providing the attribute type and value
            res.add_attribute('Description', 'test attribute #{0:d}'.format(rn))

            #
            # working with tags
            #

            # existing tags can be loaded into the resource and iterated through
            res.load_tags()
            for tag in res.tags:
                # add delete flag to all tags that have 'DELETE' in the name.
                if re.findall('DELETE', tag.name):
                    res.delete_tag(tag.name)

            # tags can be added to a resource by providing the tags value
            res.add_tag('DELETE #{0:d}'.format(rn))

            # (Required) commit this resource
            try:
                print('Updating resource {0!s}.'.format(res.name))
                res.commit()
            except RuntimeError as e:
                print('Error: {0!s}'.format(e))
                sys.exit(1)

        #
        # (Optional) delete resource if required
        #

        # delete to any resource that has 'DELETE' in the name.
        elif re.findall('DELETE', res.name):
            try:
                print('Deleting resource {0!s}.'.format(res.name))
                res.delete()  # this action is equivalent to commit
            except RuntimeError as e:
                print('Error: {0!s}'.format(e))
                sys.exit(1)

    #
    # (Optional) ADD RESOURCE EXAMPLE
    #

    # new resources can be added with the resource add method
    resource = resources.add('DELETE #{0:d}'.format(rn), owner)

    # attributes can be added to the new resource
    resource.add_attribute('Description', 'Delete Example #{0:d}'.format(rn))

    # tags can be added to the new resource
    resource.add_tag('TAG #{0:d}'.format(rn))

    # the security label can be set on the new resource
    resource.set_security_label('TLP Green')

    # commit this resource and add attributes, tags and security labels
    try:
        print('Adding resource {0!s}.'.format(resource.name))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    #
    # (Optional) UPDATE RESOURCE EXAMPLE
    #

    # existing resources can also be updated with the resource add method
    resource = resources.add('MU Threat #{0:d}'.format(rn), owner)  # this will overwrite exising resource name
    resource.set_id(mu_id)  # set the id to the existing resource

    # existing attributes can be loaded for modification or deletion
    resource.load_attributes()
    for attribute in resource.attributes:
        if attribute.type == 'Description':
            resource.delete_attribute(attribute.id)

    # attributes can be added to the existing resource
    resource.add_attribute('Description', 'Manual Update Example #{0:d}'.format(rn))

    # existing tags can be loaded for modification or deletion
    resource.load_tags()
    for tag in resource.tags:
        resource.delete_tag(tag.name)

    # tags can be added to the existing resource
    resource.add_tag('TAG #{0:d}'.format(rn))

    # commit this resource and add attributes, tags and security labels
    try:
        print('Updating resource {0!s}.'.format(resource.name))
        resource.commit()
    except RuntimeError as e:
        print('Error: {0!s}'.format(e))
        sys.exit(1)

    #
    # (Optional) DELETE RESOURCE EXAMPLE
    #

    # resources can be deleted with the resource add method
    # resource = resources.add(''.format(rn), owner)  # a valid resource name is not required
    # resource.set_id(dl_id)
    #
    # # delete this resource
    # try:
    #     resource.delete()
    # except RuntimeError as e:
    #     print(e)

    # (Optional) DISPLAY A COMMIT REPORT
    print(tc.report.stats)

    # display any failed api calls
    for fail in tc.report.failures:
        print(fail)


if __name__ == "__main__":
    main()
    sys.exit()
