import boto3


class AWSClient(object):
    def __init__(self, key_id=None, secret_key=None, regions=None):
        self.clients = []
        regions = regions or []
        if len(regions) == 0:
            self.clients = [boto3.client('ec2', aws_access_key_id=key_id, aws_secret_access_key=secret_key)]
        for region in regions:
            client = boto3.client('ec2', aws_access_key_id=key_id, aws_secret_access_key=secret_key, region_name=region)
            self.clients.append(client)

    def server_with_role(self, role, env=None):
        return self.servers_with_roles([role], env)

    def servers_with_roles(self, roles, env=None):
        result = []
        roles = set(roles)
        for instance in self.server_details():
            envmatches = (env is None) or (instance['environment'] == env)
            if roles <= set(instance['roles']) and envmatches:
                result.append(instance)
        return result

    def server_details(self):
        filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
        results = []
        for client in self.clients:
            for reservation in client.describe_instances(Filters=filters)['Reservations']:
                for instance in reservation['Instances']:
                    results.append(self._parse_instance(instance))
        return results

    def _parse_instance(self, details):
        tags = {f['Key']: f['Value'] for f in details['Tags']}
        name = tags.get('Name', None)
        return {
            'id': name,
            'internal_ip': details['PrivateIpAddress'],
            'external_ip': details['PublicIpAddress'],
            'name': name,
            'roles': [s.strip() for s in tags.get('Roles', '').split(' ') if s != ''],
            'type': details['InstanceType'],
            'external_dns': details['PublicDnsName'],
            'internal_dns': details['PrivateDnsName'],
            'security_groups': [sg['GroupId'] for sg in details['SecurityGroups']],
            'environment': tags.get('Environment', None)
        }


class FabricFriendlyClient(AWSClient):
    def ips_with_roles(self, roles, env=None):
        def func():
            return [s['external_ip'] for s in self.servers_with_roles(roles, env)]
        return func
