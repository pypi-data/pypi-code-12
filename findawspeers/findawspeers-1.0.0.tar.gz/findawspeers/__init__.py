import argparse
import json
from pprint import PrettyPrinter

import awsauthhelper
from boto.utils import get_instance_metadata


class FindAwsPeers(object):
    """
    Find peers for the specified instance
    """

    @classmethod
    def load(cls, args):
        """
        Parse cli arguments, and initialise the command

        :param List[str] args: List of cli args
        :return: findawspeers.FindAwsPeers
        """
        argparser = argparse.ArgumentParser()
        argparser.add_argument('--instance-id',
                               help=(
                                   'Specify an optional instance-id to specify as self. If not specified, '
                                   'find-aws-peers will try to determine the instance-id of the instance it is being '
                                   'run on.'
                               ),
                               default=None)
        # argparser.add_argument('--filters',
        #                        help=(
        #                            'Filter instances based on tags. If not specified, autoscaling groups will be used'
        #                            ' as the filter.'
        #                        ),
        #                        default=None)
        argparser.add_argument('--do-not-filter-self',
                               help=(
                                   'If this flag is set, then the current instance will not be included. ie, only'
                                   'siblings will be returned.'
                               ),
                               action='store_false',
                               default=True, dest='filter_self')

        awsargparser = awsauthhelper.AWSArgumentParser(role_session_name='find-aws-peers', region='us-east-1',
                                                       parents=[argparser])

        cli_options = awsargparser.parse_args(args=args[1:])

        credentials = awsauthhelper.Credentials(**vars(cli_options))
        if credentials.has_role():
            credentials.assume_role()

        return cls(
            instance_id=cli_options.instance_id,
            filters=None,  # cli_options.filters,
            region=cli_options.region,
            filter_self=cli_options.filter_self,
            session=credentials.create_session()
        )

    def __init__(self, instance_id, filters, region, session, filter_self):
        """

        :return:
        """
        self.instance_id = instance_id
        self.filters = filters
        self.region = region
        self.session = session
        self.filter_self = filter_self

    def run(self):

        ec2 = self.session(region=self.region).resource('ec2')

        if self.instance_id is None:
            self.instance_id = get_instance_metadata(data='meta-data/instance-id').keys()[0]

        if self.filters is None:
            instance = ec2.Instance(self.instance_id)

            autoscaling_group_tags = dict(map(
                lambda tag_pair: (tag_pair['Key'], tag_pair['Value']),
                filter(
                    lambda tag_pair: tag_pair['Key'] == 'aws:autoscaling:groupName',
                    instance.tags
                )
            ))

            self.filters = [{
                'Name': 'tag-key',
                'Values': ['aws:autoscaling:groupName'],
            }, {
                'Name': 'tag-value',
                'Values': [
                    autoscaling_group_tags['aws:autoscaling:groupName']
                ]
            }]

        instances = ec2.instances.filter(Filters=self.filters)

        excluded_instances = []
        if self.filter_self:
            excluded_instances.append(self.instance_id)

        peer_metadata = map(
            lambda instance: {
                'instance_id': instance.id,
                'private_ip': instance.private_ip_address,
                'public_ip': instance.public_ip_address,
            } if (instance.state['Name'] == 'running') and (instance.id not in excluded_instances) else None,
            instances
        )

        def exists(it):
            return (it is not None)

        peer_metadata = filter(exists, peer_metadata)

        print json.dumps(
            peer_metadata,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
