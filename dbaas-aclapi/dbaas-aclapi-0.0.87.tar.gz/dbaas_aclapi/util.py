import logging

logging.basicConfig()
LOG = logging.getLogger("AclBindApi")
LOG.setLevel(logging.DEBUG)


def get_credentials_for(environment, credential_type):
    from dbaas_credentials.models import Credential
    return Credential.objects.filter(integration_type__type=credential_type,
                                     environments=environment)[0]
