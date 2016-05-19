"""
Uploading a stack to AWS, and checking it exists.
"""
import os

from botocore.exceptions import ClientError
from datetime import datetime
from time import sleep

from cloudtemplatemanager.base import Base
import logging
import re


class Stack(Base):
    """
    Model representing a Cloudformation Template and its deployed Stack
    """

    ROLLBACK_IN_PROGRESS = 'ROLLBACK_IN_PROGRESS'
    ROLLBACK_COMPLETE = 'ROLLBACK_COMPLETE'

    def __init__(self, title, template, parameters, bucket, tags, dry_run=False, role=None, profile=None,
                 region='us-east-1', session=None):
        """
        Ingest Template Parameters

        :param str title: Cloudformation Stack Title
        :param str template: Path to Cloudformation JSON template on file.
        :param dict[str, str] parameters: Dictionary of values for template parameters
        :param str bucket: S3 URI for cloudformation upload location.
        :param str role: AWS IAM Role ARN.
        :param str profile: AWS IAM Credentials Profile
        :param botocore.Session session:
        :return:
        """

        self.dry_run = dry_run
        self.response = None
        self.template = template
        self.template_body = None
        self.title = title
        self.region = region
        self.logger = logging.getLogger(__name__)

        self._parameters = parameters
        self._bucket = bucket
        self._role = role
        self._profile = profile
        self._session = session
        self._tags = tags
        self._credentials = None
        self._s3_url = None
        self._stack = None

        self.cloudformation_client = None
        self.cloudformation = None

        super(Stack, self).__init__()

    def load(self):
        """
        Load the template from file, and validate it.

        :return cloudtemplatemanager.stack.Stack:
        """
        if self._session is None:
            self.init_credentials()

        self.cloudformation = self._session().resource('cloudformation')
        self.cloudformation_client = self._session().client('cloudformation')

        # Load cloudformation template
        template_path = os.path.realpath(os.path.expanduser(self.template))
        with open(template_path) as fp:
            self.template_body = fp.read()

        return self

    def upload(self):
        """
        Upload the template to an S3 bucket.

        :return str url: S3 HTTP URL
        """
        s3 = self._session().resource('s3')
        s3_client = self._session().client('s3')

        bucket, key = self._parse_bucket(self._bucket, self.template)
        self.logger.debug("Starting upload of '{title}' to {bucket}.".format(title=self.title, bucket=bucket))

        # Check s3 bucket exists
        self.logger.debug("Checking bucket '{bucket_name}' exists.".format(bucket_name=bucket))
        if not self._bucket_exists(bucket=bucket, s3=s3):
            self.logger.debug("Bucket '{bucket_name}' doesn't exist".format(bucket_name=bucket))
            self.logger.info("Creating bucket '{bucket_name}'.".format(bucket_name=bucket))
            s3.create_bucket(
                ACL='private', Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )

            # Wait for our bucket to be created
            s3_client.get_waiter('bucket_exists').wait(Bucket=bucket)

            self.logger.debug("Enabling Versioning on 's3://{0}'".format(bucket=bucket))
            s3.BucketVersioning(bucket).enable()

        self.logger.debug("Uploading '{title}' to s3://{bucket_name}.".format(title=self.title, bucket_name=bucket))

        s3.Object(bucket, key).put(
            Body=self.template_body,
            ACL='private'
        )

        self._s3_url = self._build_bucket_url(key=key, bucket=bucket)

        return self

    def deploy(self):
        """
        Deploy the Template to a Cloudformation Stack.

        :return cloudtemplatemanager.stack.Stack:
        """

        stack_params = self._build_stack_params()
        self._stack = self.cloudformation.Stack(self.title)
        try:
            if self.can_create():
                self.create(stack_params)
            elif self.can_update():
                self.update(stack_params)
        except NoUpdateException:
            self.response = {
                'status': False,
                'code': 'NO_UPDATE',
                'message': 'No updates to be performed',
            }
        return self

    def can_update(self):
        """
        Check if the stack is in a state where it can be updated

        :return bool: True if the stack can be updated. False if the stack can not be updated.
        """
        if self._stack.stack_status == 'ROLLBACK_IN_PROGRESS':
            raise Exception("Stack '{0}' is rolling back".format(self._stack.name))
        elif self._stack.stack_status in ['CREATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE', 'UPDATE_COMPLETE']:
            return True
        return False

    def can_create(self):
        """
        Check if the stack is in a state where it can be created.

        :return bool:
        """
        try:
            self.logger.debug("Stack '{0}' has status '{1}'".format(self.title, self._stack.stack_status))
            # If Stack is rolling back
            if self._stack.stack_status == Stack.ROLLBACK_IN_PROGRESS:
                raise StackIsRollingBack(self.title)
            # If Stack has finished roll back
            elif self._stack.stack_status == Stack.ROLLBACK_COMPLETE:
                self._stack.delete()
                self.cloudformation_client.get_waiter('stack_delete_complete').wait(StackName=self.title)
            return False
        except ClientError as e:
            if 'does not exist' in e.response['Error']['Message']:
                return True
            elif e.response['Error']['Message'] == 'No updates are to be performed.':
                raise NoUpdateException(self.title)
            else:
                raise e

    def _build_stack_params(self):
        """
        Build Parameters for boto3 (create|update)_stack

        :return dict[str, str]:
        """

        create_stack_params = {
            'StackName': self.title,
            'Capabilities': ['CAPABILITY_IAM'],
        }

        # Generate Tags
        tags = map(
            lambda tag_pair: {'Key': tag_pair[0], 'Value': tag_pair[1]},
            self._tags.items()
        )

        if tags:
            create_stack_params['Tags'] = tags

        # Generate params
        parameters = map(lambda param_pair: {
            'ParameterKey': param_pair[0],
            'ParameterValue': param_pair[1],
            'UsePreviousValue': False
        }, self._parameters.items())

        if parameters:
            create_stack_params['Parameters'] = parameters

        create_stack_params['TemplateURL'] = self._s3_url

        return create_stack_params

    def _build_bucket_url(self, bucket, key):
        """
        Returns an S3 HTTP url

        :param str bucket: s3 bucket name
        :param str key: s3 bucket key
        :return:
        """
        if self.region == 'us-east-1':
            bucket_url_format = 'http://{bucket_name}.s3.amazonaws.com/{key}'
        else:
            bucket_url_format = 'http://{bucket_name}.s3-{region}.amazonaws.com/{key}'

        return bucket_url_format.format(region=self.region, bucket_name=bucket, key=key)

    @staticmethod
    def _bucket_exists(bucket, s3):
        """
        Check a bucket exists

        :param str bucket: Bucket Name
        :param s3:
        :return bool: True if bucket exists, False if bucket does not exist.
        """
        try:
            s3.meta.client.head_bucket(Bucket=bucket)
            return True
        except ClientError as e:
            if e.message.endswith('Forbidden'):
                raise e
            return False

    @staticmethod
    def _parse_bucket(bucket, template_name=None):
        """
        Return a bucket and key from an s3 url with or without protocol prefix.

        :param str bucket: s3 bucket uri
        :return str, str: s3 bucket name, and 3 key.
        """
        bucket = bucket.replace('s3://', '')
        matches = re.match(r'^(?P<bucket>[^/]+)(?P<key>.*)', bucket)
        bucket = matches.group('bucket')
        key = matches.group('key')
        key = key if key else '/'
        if template_name is not None:
            key = os.path.basename(template_name) if key == '/' else key

        return str(bucket), str(key)

    def create(self, stack_params):
        """
        Try to create the stack, and if it already exists, then update it

        :param stack_params:
        :return:
        """
        try:
            self.cloudformation_client.validate_template(
                TemplateURL=stack_params['TemplateURL']
            )
            stack = self.cloudformation.create_stack(**stack_params)
        except ClientError as create_exception:
            # Stack already exists in this case
            if create_exception.response['Error']['Code'] == 'AlreadyExistsException':
                self.logger.info(
                    'Updating existing stack: {message}'.format(message=create_exception.response['Error']['Message'])
                )
                stack = self.update(stack_params)
            else:
                raise create_exception

        return stack

    def update(self, stack_params, stack=None):
        """
        Perform a stack update.

        :param dict stack_params:
        :param stack:
        :return:
        """

        changeset_name = "{stack}-{date:%Y-%m-%d-%H%M%S}".format(stack=self.title, date=datetime.now())
        # changeset_client_token = "{stack}-{token}".format(stack=self.stack_name, token=uuid.uuid4())

        change_set = self.cloudformation_client.create_change_set(
            ChangeSetName=changeset_name,
            # ClientToken=changeset_client_token,
            **stack_params
        )

        changeset_description = self.cloudformation_client.describe_change_set(
            ChangeSetName=changeset_name,
            StackName=self.title
        )

        self.logger.info('Changeset Status: \'{0}\''.format(changeset_description['Status']))

        if changeset_description['Status'] in ['UPDATE_IN_PROGRESS', 'CREATE_IN_PROGRESS', 'CREATE_PENDING']:
            self.logger.info('Waiting for changeset \'{0}\' to finish creating...'.format(
                changeset_name
            ))
            while changeset_description['Status'] in ['CREATE_IN_PROGRESS', 'CREATE_PENDING']:
                sleep(5)
                changeset_description = self.cloudformation_client.describe_change_set(
                    ChangeSetName=changeset_name,
                    StackName=self.title
                )
        self.logger.debug('Created changeset \'{0}\' with status \'{1}\''.format(
            changeset_name,
            changeset_description['Status']
        ))

        if changeset_description['Status'] == 'FAILED':
            if not changeset_description['Changes']:
                self.logger.info('Template has no changes')
                # If there are no changes
                return stack

        if not self.dry_run:
            self.cloudformation_client.execute_change_set(
                ChangeSetName=change_set['Id'],
                StackName=self.title
            )

        return stack


class NoUpdateException(Exception):
    """
    Thrown if the stack has no updates to be performed.
    """

    def __init__(self, title):
        super(NoUpdateException, self).__init__("No changes in template for stack '{0}'".format(title))


class StackIsRollingBack(Exception):
    """
    Thrown if the stack is in a state where it is rolling back
    """

    def __init__(self, stack_name):
        super(StackIsRollingBack, self).__init__("Stack '{0}' is rolling back".format(stack_name))
