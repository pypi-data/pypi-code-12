from botor.aws.sts import sts_conn
from botor.decorators import rate_limited
from joblib import Parallel, delayed


@sts_conn('iam')
@rate_limited()
def list_roles(**kwargs):
    client = kwargs['client']
    roles = []
    marker = {}

    while True:
        response = client.list_roles(**marker)
        roles.extend(response['Roles'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            return roles


@rate_limited()
@sts_conn('iam', service_type='client')
def get_role_inline_policy_names(role, client=None, **kwargs):
    marker = {}
    inline_policies = []

    while True:
        response = client.list_role_policies(
            RoleName=role['RoleName'],
            **marker
        )
        inline_policies.extend(response['PolicyNames'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            return inline_policies


def get_role_inline_policies(role, **kwargs):
    policy_names = get_role_inline_policy_names(role, **kwargs)

    policies = zip(
        policy_names,
        Parallel(n_jobs=20, backend="threading")(
            delayed(get_role_inline_policy_document)
            (role, policy_name, **kwargs) for policy_name in policy_names
        )
    )
    policies = dict(policies)

    return policies


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_inline_policy_document(role, policy_name, client=None, **kwargs):
    response = client.get_role_policy(
        RoleName=role['RoleName'],
        PolicyName=policy_name
    )
    return response.get('PolicyDocument')


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_instance_profiles(role, client=None, **kwargs):
    marker = {}
    instance_profiles = []

    while True:
        response = client.list_instance_profiles_for_role(
            RoleName=role['RoleName'],
            **marker
        )
        instance_profiles.extend(response['InstanceProfiles'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            break

    return [
        {
            'path': ip['Path'],
            'instance_profile_name': ip['InstanceProfileName'],
            'create_date': ip['CreateDate'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'instance_profile_id': ip['InstanceProfileId'],
            'arn': ip['Arn']
        } for ip in instance_profiles
    ]


@sts_conn('iam', service_type='client')
@rate_limited()
def get_role_managed_policies(role, client=None, **kwargs):
    marker = {}
    policies = []

    while True:
        response = client.list_attached_role_policies(
            RoleName=role['RoleName'],
            **marker
        )
        policies.extend(response['AttachedPolicies'])

        if response['IsTruncated']:
            marker['Marker'] = response['Marker']
        else:
            break

    return [{'name': p['PolicyName'], 'arn': p['PolicyArn']} for p in policies]


@sts_conn('iam', service_type='resource')
@rate_limited()
def all_managed_policies(resource=None, **kwargs):
    managed_policies = {}

    for policy in resource.policies.all():
        for attached_role in policy.attached_roles.all():
            policy_dict = {
                "name": policy.policy_name,
                "arn": policy.arn,
                "version": policy.default_version_id
            }

            if attached_role.arn not in managed_policies:
                managed_policies[attached_role.arn] = [policy_dict]
            else:
                managed_policies[attached_role.arn].append(policy_dict)

    return managed_policies
