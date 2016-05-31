"""
Top level utilities and documentation for the plumbing implementation in AWS.
"""

import boto3


class SQSResource:
    """Mixin to provide _get_queue() to fetch a SQS queue by name."""

    def _get_queue(self, queue_name, sqs=None):
        """Get the queue object by name.

        The SQS resource handle can be passed, otherwise one is instantiated.

        Positional paramters:
        * the queue name.

        Keyword parameters:
        * sqs: optionally the SQS resource handle.
        """
        if sqs is None:
            sqs = boto3.resource('sqs')
        return sqs.get_queue_by_name(QueueName=queue_name)


class SNSResource:
    """Mixin to provide _get_topic() to fetch a SNS topic by name."""

    def _get_topic(self, topic_name, sns=None):
        """Get the topic by name.

        A SNS resource handle can be passed, or one will be obtained with
        default configuration parameters.

        Positional parameters:
        * the topic name.
        * optionaly, a SNS handler to get the topic by name.
        """
        if sns is None:
            sns = boto3.resource('sns')
        # Use property of SNS resource: create_topic() is idempotent.
        # http://boto3.readthedocs.org/en/latest/reference/services/sns.html#sns.Client.create_topic
        return sns.create_topic(Name=topic_name)
