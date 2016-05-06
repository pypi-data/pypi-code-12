from boto import vpc, ec2
from underaid.boto_utils.exceptions import BotoUtilsException

class BotoUtilsConnection:

    AMI_STORE_ACCOUNT_ID = '867515917767'

    def __init__(self, region_name, **kargs):
        self.region_name = region_name
        self.kargs = kargs

    @property
    def vpc_connection(self):
        return vpc.connect_to_region(self.region_name, **self.kargs)

    @property
    def ec2_connection(self):
        return ec2.connect_to_region(self.region_name, **self.kargs)

    def get_vpc_subnets(self, vpc_id, logical_id):
        subnets = self.vpc_connection.get_all_subnets(
            filters={
                'vpcId': vpc_id,
                'tag:aws:cloudformation:logical-id': logical_id
            }
        )

        if not subnets:
            raise BotoUtilsException(
                "No subnets found in region '{0}' for vpc '{1}' "
                "with logical_id '{2}'".
                format(self.region_name, vpc_id, logical_id)
            )

        return subnets

    def get_vpc_subnet_ids(self, vpc_id, logical_id):
        subnets = self.get_vpc_subnets(vpc_id, logical_id)

        return [subnet.id for subnet in subnets]

    def get_latest_snapshot(self, filters={}):
        snapshots = self.ec2_connection.get_all_snapshots(
            filters=filters
        )

        if not snapshots:
            raise BotoUtilsException(
                "No Snapshot found in region '{0}' for filters {1}"
                .format(self.region_name, filters)
            )

        return max(snapshots, key=lambda s: s.start_time)

    def get_latest_snapshot_id(self, filters={}):
        return self.get_latest_snapshot(filters).id

    def get_vpc_security_groups(self, vpc_id, logical_id):
        security_groups = self.ec2_connection.get_all_security_groups(
            filters={
                'vpc-id': vpc_id,
                'tag:aws:cloudformation:logical-id': logical_id
            }
        )

        if not security_groups:
            raise BotoUtilsException(
                "No security groups found in region '{0}' for vpc '{1}' "
                "with logical_id '{2}'"
                .format(sel.region_name, vpc_id, logical_id)
            )

        return security_groups

    def get_vpc_security_group(self, vpc_id, logical_id):
        security_groups = self.get_vpc_security_groups(vpc_id, logical_id)

        if len(security_groups) > 1:
            raise BotoUtilsException(
                "Ambiguous security group found in region '{0}' for vpc '{1}' "
                "with logical_id '{2}'"
                .format(self.region_name, vpc_id, logical_id)
            )

        return security_groups[0]

    def get_vpc_security_group_id(self, vpc_id, logical_id):
        return self.get_vpc_security_group(vpc_id, logical_id).id

    def get_latest_ami(self, name):
        images = self.ec2_connection.get_all_images(
            filters={"tag:Name": "*{0}*".format(name)},
            owners=['self', self.AMI_STORE_ACCOUNT_ID]
        )

        if not images:
            raise BotoUtilsException(
                "No AMI found in region '{0}' "
                "with name '{1}'"
                .format(self.region_name, name)
            )

        return max(images, key=lambda image: image.creationDate)

    def get_latest_ami_id(self, name):
        return self.get_latest_ami(name).id
