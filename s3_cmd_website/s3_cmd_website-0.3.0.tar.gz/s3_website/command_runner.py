from subprocess import Popen, PIPE


def run(logger, command, operation,
        s3cmd_config_path=None,
        access_key=None,
        secret_key=None,
        region=None,
        ):
    """
    Helper script for running subprocess commands

    :param logger: Logger - Logger for logging events
    :param command: List(string) - the command and options to be executed
    :param operation: String - The operation being performed in text
     e.g. CloudFront creation, CloudFront deletion
    :param s3cmd_config_path: String - Path to the local s3cmd file
    :param access_key: String - Override AWS access key
    :param secret_key: String - Override AWS secret key
    :param region: String - Override the AWS region
    """

    if s3cmd_config_path:
        command.extend(['--config=%s' % s3cmd_config_path], )

    if access_key and secret_key:
        command.extend(['--access_key=%s' % access_key,
                        '--secret_key=%s' % secret_key, ])

    if region:
        command.extend(['--region=%s' % region], )

    logger.debug(command)
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    exit_code = process.returncode

    if exit_code != 0:
        logger.error('An error has occurred while executing the %s', operation)
        logger.error('Output:\n%s\n\n Error:\n%s', stdout, stderr)
    else:
        logger.info(stdout)
    return exit_code
