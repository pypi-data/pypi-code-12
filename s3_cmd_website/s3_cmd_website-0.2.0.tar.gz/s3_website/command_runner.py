from subprocess import Popen, PIPE


def run(logger, command, operation):
    """
    Helper script for running subprocess commands

    :param logger: Logger - Logger for logging events
    :param command: List(string) - the command and options to be executed
    :param operation: String - The operation being performed in text
     e.g. CloudFront creation, CloudFront deletion
    """

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
