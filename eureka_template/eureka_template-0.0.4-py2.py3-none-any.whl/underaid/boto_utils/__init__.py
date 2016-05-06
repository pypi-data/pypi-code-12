import underaid
from underaid.boto_utils.connection import BotoUtilsConnection

def connect_to_region(region_name, **kargs):
    profile_name = kargs.get('profile_name', None)

    if profile_name:
        underaid.set_aws_environment(profile_name)

    return BotoUtilsConnection(region_name, **kargs)