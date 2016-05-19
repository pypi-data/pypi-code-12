import sys

from cloudtemplatemanager import json_pprint
from cloudtemplatemanager.provision import Provision


def cfn_provision(args=sys.argv):
    json_pprint(
        Provision.load(args[1:]).run()
    )
