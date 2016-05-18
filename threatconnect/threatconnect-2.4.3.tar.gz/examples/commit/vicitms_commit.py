# -*- coding: utf-8 -*-

""" standard """
import ConfigParser
from random import randint
import re
import sys

""" custom """
from threatconnect import ThreatConnect
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.VictimAssetObject import VictimAssetObject

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
# - These victims must be created before running this script
#
owner = 'Example Community'  # org or community
lu_id = 1  # adversary id for loop update
mu_id = 4  # adversary id for manual update
# dl_id = 999999  # adversary id to delete
email_id = 17  # email resource id to associate with adversary
email_address = 'notsobad@gmail.com'  # email address to associate to adversary
rn = randint(1, 1000)  # random number generator for testing


def main():
    """ """
    # (Optional) SET THREAT CONNECT LOG (TCL) LEVEL
    tc.set_tcl_file('log/tc.log', 'debug')
    tc.set_tcl_console_level('critical')

    # (Required) Instantiate a Resource Object
    resources = tc.victims()

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
            res.set_name('LU Victim #{0:n}'.format(rn))
            res.set_nationality('Nationality #{0:n}'.format(rn))
            res.set_org('Org #{0:n}'.format(rn))
            res.set_suborg('Sub Org #{0:n}'.format(rn))
            res.set_work_location('Location #{0:n}'.format(rn))

            #
            # resource assets (assets are automatically loaded for victims)
            #
            res.load_assets()
            for asset_obj in res.assets:
                if asset_obj.type == 'EmailAddress' and re.findall('victim', asset_obj.name):
                    # existing email address assets can be updated
                    asset = VictimAssetObject(ResourceType.VICTIM_EMAIL_ADDRESSES)
                    asset.set_address('victim_{0:n}@victimsareus.com'.format(rn))
                    asset.set_address_type('Personal')
                    res.update_asset(asset_obj.id, asset)
                if asset_obj.type == 'SocialNetwork' and re.findall('victim_', asset_obj.name):
                    asset = VictimAssetObject(ResourceType.VICTIM_SOCIAL_NETWORKS)
                    res.delete_asset(asset_obj.id, asset)

            # social network assets can be added to a victim
            asset = VictimAssetObject(ResourceType.VICTIM_SOCIAL_NETWORKS)
            asset.set_account('victim_{0:n}'.format(rn))
            asset.set_network('Twitter')
            res.add_asset(asset)

            #
            # working with indicator associations
            #
            # TODO: verify this is supported

            # # existing indicator associations can be retrieved and iterated through
            # for association in res.indicator_associations:
            #     print(association)
            #     # add delete flag to all indicator association that have a confidence under 10
            #     if association.confidence < 10:
            #         res.disassociate_indicator(association.resource_type, association.indicator)
            #
            # # indicator associations can be added to a resource by providing the resource type and value
            # res.associate_indicator(ResourceType.EMAIL_ADDRESSES, email_address)

            #
            # working with group associations
            #

            # existing group associations can be retrieved and iterated through
            for association in res.group_associations:
                # add delete flag to all group association that match DELETE
                if re.findall('LU', association.name):
                    res.disassociate_group(association.resource_type, association.id)

            # group associations can be added to a resource by providing the resource type and id
            res.associate_group(ResourceType.EMAILS, email_id)

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

    # properties can be added
    resource.set_nationality('Nationality #{0:d}'.format(rn))
    resource.set_org('Org #{0:d}'.format(rn))
    resource.set_suborg('Sub Org #{0:d}'.format(rn))
    resource.set_work_location('Location #{0:d}'.format(rn))

    # email address assets can be added to new victim
    asset = VictimAssetObject(ResourceType.VICTIM_EMAIL_ADDRESSES)
    asset.set_address('victim_{0:d}@victimsareus.com'.format(rn))
    asset.set_address_type('Personal')
    resource.add_asset(asset)

    # network account assets can be added to new victim
    asset = VictimAssetObject(ResourceType.VICTIM_NETWORK_ACCOUNTS)
    asset.set_account('victim_{0:d}'.format(rn))
    asset.set_network('victimsareus Active Directory')
    resource.add_asset(asset)

    # phone assets can be added to new victim
    asset = VictimAssetObject(ResourceType.VICTIM_PHONES)
    asset.set_phone_type('555-5{0:d}'.format(rn))
    resource.add_asset(asset)

    # social network assets can be added to new victim
    asset = VictimAssetObject(ResourceType.VICTIM_SOCIAL_NETWORKS)
    asset.set_account('victim_{0:d}'.format(rn))
    asset.set_network('Twitter')
    resource.add_asset(asset)

    # website assets can be added to new victim
    asset = VictimAssetObject(ResourceType.VICTIM_WEBSITES)
    asset.set_website('www.victimsareus_{0:d}.com'.format(rn))
    resource.add_asset(asset)

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
    resource = resources.add('MU Victim #{0:d}'.format(rn), owner)  # this will overwrite exising resource name
    resource.set_id(mu_id)  # set the id to the existing resource

    # existing properties can be updated
    resource.set_nationality('Nationality #{0:d}'.format(rn))
    resource.set_org('Org #{0:d}'.format(rn))
    resource.set_suborg('Sub Org #{0:d}'.format(rn))
    resource.set_work_location('Location #{0:d}'.format(rn))

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
