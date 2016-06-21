from bozor.exceptions import BozorException
from bozor.aws.arn import ARN

from botor.aws.iam import get_role_inline_policies
from botor.aws.iam import get_role_instance_profiles
from botor.aws.iam import get_role_managed_policies
from botor import Botor

from inflection import camelize, underscore


def _conn_from_arn(arn):
    """
    Extracts the account number from an ARN.
    :param arn: Amazon ARN containing account number.
    :return: dictionary with a single account_number key that can be merged with an existing
    connection dictionary containing fields such as assume_role, session_name, region.
    """
    role_arn = ARN(arn)
    if role_arn.error:
        raise BozorException('Bad ARN: {arn}'.format(arn=arn))
    return dict(
        account_number=role_arn.account_number,
    )


def _get_role_name(role):
    """
    Given a possibly sparsely populated role dictionary, try to retrieve the role name.
    First try the role_name field.  If that doesn't exist, try to parse the role name from
    the ARN.
    :param role: dict containing (at the very least) role_name and/or arn
    :return: role name
    """
    if role.get('RoleName'):
        return role.get('RoleName')

    if role.get('Arn'):
        arn = role.get('Arn')
        role_arn = ARN(arn)
        if role_arn.error:
            raise BozorException('Bad ARN: {arn}'.format(arn=arn))
        return role_arn.parsed_name

    raise BozorException('Cannot extract role name from input: {input}.'.format(input=role))


def _get_base(role, **conn):
    """
    Determine whether the boto get_role call needs to be made or if we already have all that data
    in the role object.
    :param role: dict containing (at the very least) role_name and/or arn.
    :param conn: dict containing enough information to make a connection to the desired account.
    :return: Camelized dict describing role containing all all base_fields.
    """
    base_fields = frozenset(['Arn', 'AssumeRolePolicyDocument', 'Path', 'RoleId', 'RoleName', 'CreateDate'])
    needs_base = False

    for field in base_fields:
        if field not in role:
            needs_base = True
            break

    if needs_base:
        role_name = _get_role_name(role)
        role = Botor.go('iam.client.get_role', RoleName=role_name, **conn)
        role = role['Role']

        # cast CreateDate from a datetime to something JSON serializable.
        role.update(dict(CreateDate=str(role['CreateDate'])))

    return role


def _modify(role, func):
    """
    Modifies each role.keys() string based on the func passed in.
    Often used with inflection's camelize or underscore methods.

    :param role: dictionary representing role to be modified
    :param func: function to run on each key string
    :return: dictionary where each key has been modified by func.
    """
    for key in role:
        new_key = func(key)
        if key != new_key:
            role[new_key] = role[key]
            del role[key]
    return role


def modify(role, format='camelized'):
    """
    Calls _modify and either passes the inflection.camelize method or the inflection.underscore method.

    :param role: dictionary representing role to be modified
    :param format: string 'camelized' or 'underscored'
    :return:
    """
    if format == 'camelized':
        return _modify(role, camelize)
    elif format == 'underscored':
        return _modify(role, underscore)


def get_role(role, output='camelized', **conn):
    """
    Orchestrates all the calls required to fully build out an IAM Role in the following format:

    {
        "Arn": ...,
        "AssumeRolePolicyDocument": ...,
        "CreateDate": ...,  # str
        "InlinePolicies": ...,
        "InstanceProfiles": ...,
        "ManagedPolicies": ...,
        "Path": ...,
        "RoleId": ...,
        "RoleName": ...,
    }

    :param role: dict containing (at the very least) role_name and/or arn.
    :param output: Determines whether keys should be returned camelized or underscored.
    :param conn: dict containing enough information to make a connection to the desired account.
    Must at least have 'assume_role' key.
    :return: dict containing a fully built out role.
    """
    role = modify(role, 'camelized')
    if role.get('Arn'):  # otherwise, account_number can be included in **conn
        conn.update(_conn_from_arn(role.get('Arn')))
    role = _get_base(role, **conn)
    role.update(
        {
            'managed_policies': get_role_managed_policies(role, **conn),
            'inline_policies': get_role_inline_policies(role, **conn),
            'instance_profiles': get_role_instance_profiles(role, **conn)
        }
    )
    return modify(role, format=output)
