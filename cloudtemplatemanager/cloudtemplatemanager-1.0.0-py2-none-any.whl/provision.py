import awsauthhelper
import argparse
import yaml
from voluptuous import Schema, Required, Optional, Length

from cloudtemplatemanager import json_pprint
from cloudtemplatemanager.stack import Stack
from cloudtemplatemanager.base import Base


class Provision(Base):
    """
    CLI Wrapper for Stack Provisioner
    """

    def __init__(self, **kwargs):
        self.config = None
        self.region = 'us-east-1'
        self.parameters_file = None
        super(Provision, self).__init__(**kwargs)

    @classmethod
    def load(cls, args):
        """
        Parse cli arguments and return a command object to run.

        :param List[str] args:
        :return:
        """
        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument('-f', '--force',
                                     help='Force the provisioner to delete stacks if they are in an error state.',
                                     action='store_true', default=False)
        argument_parser.add_argument('--config', help='A file containing parameters', required=False)
        argument_parser.add_argument('--platform', help='Cloud Provider to deploy to', default='aws', choices=['aws'])
        argument_parser.add_argument('--dry-run', help='Perform a trial run with no changes made', action='store_true',
                                     default=False)

        all_args = awsauthhelper.AWSArgumentParser(role_session_name='cloudtemplatemanager', parents=[argument_parser])

        provisioner = all_args.parse_args(args=args, namespace=cls())
        provisioner.init_credentials()
        return provisioner

    def run(self):
        """
        Load the config file, validate it, upload the template, and deploy the stack.

        :return:
        """

        params = self._validate_params(
            stack_config=self._load_configs()
        )

        json_pprint(params)

        return Stack(region=self.region, session=self.session, **params) \
            .load() \
            .upload() \
            .deploy() \
            .response

    def _load_configs(self):
        """
        Load configs from file, and parse the yaml.

        :return dict[str, str]:
        """
        with open(self.config) as fp:
            return yaml.load(fp.read())

    @staticmethod
    def _validate_params(stack_config):
        """
        Validate the loaded config file

        :param dict[str, str] stack_config:
        :return dict[str, str]:
        """
        validator = Schema({
            Required('title'): str,
            Required('template'): str,
            Required('profile', default='default'): str,
            Required('parameters', default={}): Schema({str: str}, Length(min=1)),
            Required('tags', default={}): Schema({str: str}),
            Optional('bucket'): str,
            Optional('role'): str
        })

        return validator(stack_config)
