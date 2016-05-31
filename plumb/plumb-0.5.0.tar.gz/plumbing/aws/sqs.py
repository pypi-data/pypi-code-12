import logging
from . import SQSResource
from ..serializers import JSON


class Source(SQSResource, JSON):
    """Uses the boto3 Queue object.

    Uses get_queue_by_name(), or receives the queue during initialization step.

    Relies on receive_messages() as described in:
    http://boto3.readthedocs.org/en/latest/reference/services/sqs.html#queue
    """

    # http://boto3.readthedocs.org/en/latest/reference/services/sqs.html
    # http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html
    # https://github.com/boto/boto3-sample/blob/master/transcoder.py

    #
    # TODO: use queue name for logging.
    #

    # For reference value, see:
    # http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html
    LONG_POLLING_TIMEOUT = 20  # seconds

    def __init__(self, queue=None, queue_name=None, sqs=None):
        """Prepare the source with a configured SQS backend.

        The SQS queue object can be passed, or the queue name. If both are
        passed, the object is preferred.

        Keyword parameters:
        * queue: SQS client object.
        * queue_name: alternatively, the queue name.
        * sqs: optionally, a SQS resource handle can be passed.

        """
        self.log = logging.getLogger('sqs.source')
        if queue is None:
            queue = self._get_queue(queue_name, sqs=sqs)
        self.queue = queue
        self.log.debug('using SQS queue URL="%s"' % self.queue.url)

    def _package_from_message(self, msg):
        """Parse the raw package from the message coming from the backend."""
        try:
            return self.deserialize(msg.body)
        except Exception as e:
            self.log.error('could not parse incoming message')
            self.log.debug('offending message: %s' % msg.body)
            raise e

    def _get_message(self):
        """Returns a single (deleted) message from backend, or None.

        Uses queue.receive_messages() to poll for a package. Polls the backend
        until it gets a new message. Blocks for LONG_POLLING_TIMEOUT.

        Counts on LONG_POLLING_TIMEOUT seconds being a good polling timeout,
        and 1 being the default number of messages to pull.
        """
        # receive_messages() returns a list, even if asked for just one.
        msgs = self.queue.receive_messages(
            WaitTimeSeconds=self.LONG_POLLING_TIMEOUT,
        )
        try:
            msg = msgs[0]
        except IndexError:
            # No messages available.
            return None

        msg.delete()
        return msg

    def get_once(self):
        """Returns a package if one is available, or None."""
        msg = self._get_message()
        if msg is not None:
            try:
                msg = self._package_from_message(msg)
            except Exception:
                self.log.warning('dropping offending message')
                msg = None
        return msg

    def get(self, num_tries=-1):
        """Returns a package, or None, after num_tries times.

        Use "num_tries" to specify the number of loops. A value of -1 is an
        infinite loop.
        """
        count = num_tries
        while count != 0:
            pkg = self.get_once()
            if pkg is not None:
                return pkg
            if count > 0:
                count = count - 1
        return None


class Sink(SQSResource, JSON):
    """Uses the boto3 Queue object.

    Uses get_queue_by_name(), or receives the queue during initialization step.

    Relies on send_message() as described in:
    http://boto3.readthedocs.org/en/latest/reference/services/sqs.html#queue
    """

    # http://boto3.readthedocs.org/en/latest/reference/services/sqs.html
    # http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html
    # https://github.com/boto/boto3-sample/blob/master/transcoder.py

    def __init__(self, queue=None, queue_name=None, sqs=None):
        """Prepare the sink with a configured SQS backend.

        Either the SQS queue object or its name must be passed (queue object is
        preferred).

        Keyword parameters:
        * queue: the queue object.
        * queue_name: alternatively, the queue name.
        * sqs: optionaly, a SQS handler to get the queue by name.
        """
        self.log = logging.getLogger('sqs.sink')
        if queue is None:
            queue = self._get_queue(queue_name, sqs)
        self.queue = queue
        self.log.debug('using SQS queue URL="%s"' % self.queue.url)

    def put(self, pkg):
        """Sends the raw package to the queue.

        Positional parameters:
        * the raw package dict.
        """
        msg = self.serialize(pkg)
        self.log.debug('sending to queue JSON encoded package: %s' % msg)
        self.queue.send_message(MessageBody=msg)
