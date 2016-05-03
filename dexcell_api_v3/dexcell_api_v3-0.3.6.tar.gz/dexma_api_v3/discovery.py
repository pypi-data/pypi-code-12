__author__ = 'dcortes'

import sys

from repositories.repository_readings import RepositoryReadings
from repositories.repository_device import RepositoryDevice as RepositoryDevices
from repositories.repository_location import RepositoryLocation as RepositoryLocations
from repositories.repository_cost_electrical_consumption import RepositoryCostElectricalConsumption
from repositories.repository_cost_electrical_demand import RepositoryCostElectricalDemand
from repositories.repository_cost_electrical_summary import RepositoryCostElectricalSummary
from repositories.repository_utility_supplies_electricity import RepositoryUtilitySuppliesElectricity
from repositories.repository_utility_contracts_electricity import RepositoryUtilityContractsElectricity
from repositories.repository_oauth_access_token import RepositoryOauthAccessToken


def change_underscore_to_uppercase(service_name):
    services = service_name.split("_")
    return "Repository{}".format(''.join([service.capitalize() for service in services]))


def service_to_class(service):
    return getattr(sys.modules[__name__], service)


def build(service_name, endpoint="http://api.dexcell.com/v3"):
    service = change_underscore_to_uppercase(service_name)
    if service == "OauthAccessToken": raise Exception("For oauth use method buildOauth with parameters id and secret")
    service_class = service_to_class(service)
    return service_class(endpoint)

def buildOauth(id, secret, endpoint="http://api.dexcell.com/v3"):
    #Special call that don't requiere
    return RepositoryOauthAccessToken(id, secret, endpoint)

