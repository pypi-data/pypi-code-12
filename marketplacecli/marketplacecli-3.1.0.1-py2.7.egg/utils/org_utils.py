__author__ = "UShareSoft"

from marketplacecli.exceptions.UForgeException import UForgeException
from marketplacecli.utils import marketplace_utils


def org_get(api, name, on_error_raise=True):
    try:
        org = None
        if name is None:
            org = api.Orgs("default").Get()
            return org
        else:
            orgs = api.Orgs().Getall(None)
            for o in orgs.orgs.org:
                if o.name == name:
                    org = o
    except Exception as e:
        marketplace_utils.print_uforge_exception(e)

    if org is None and on_error_raise:
        raise UForgeException("Unable to find organization")
    return org
