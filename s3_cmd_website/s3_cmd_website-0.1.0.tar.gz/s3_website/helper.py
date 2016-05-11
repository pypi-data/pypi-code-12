import os.path
import re
import sys
import yaml
from datetime import timedelta
import logging
import log

from six import integer_types


def s3cmd_path():
    """
    The full path of the s3cmd executable
    """
    return 's3cmd'


def file_exists(file_path):
    """
    Check to see if a file exists

    :param file_path: string - The path to the file
    """
    return os.path.isfile(file_path)


def load_yaml(yaml_file_path, logger):
    """
    Read a yaml file from the filesystem and return it as a dict
    Returns 'None' if the file is not found

    :param yaml_file_path: string - Location of the yaml file to be read
    :param logger: Logger - Logger for logging events
    """
    if file_exists(yaml_file_path):
        with open(yaml_file_path, 'r') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError, exc:
                mark = ("at position: (%s:%s)" % (exc.problem_mark.line+1,
                                                  exc.problem_mark.column+1)
                        if hasattr(exc, 'problem_mark') else '')
                logger.error("Error has occurred in configuration file '%s' %s"
                             % (yaml_file_path, mark))
                return None
    else:
        return None


def maxage_in_seconds(maxage):
    """
    Determine if we need to convert the maxage string from human readable or if
     it is already an integer
    """
    if isinstance(maxage, integer_types):
        return maxage
    else:
        td = timedelta_from_duration_string(maxage)
        return int(td.total_seconds())


def timedelta_from_duration_string(time_string):
    """
    Convert time duration string to number of seconds.
    Supports: year|month|day|hour|minute|second
    Example: 1 hour returns 3600
             1 day returns 86400

    :param time_string: string - The time as a string or an integer as seconds
    """
    if re.match(r'^\d+$', time_string):
        return timedelta(seconds=int(time_string))

    td_args = {}
    for part in time_string.split(','):
        part = part.strip()
        m = re.match(r'(\d+)\s+(year|month|day|hour|minute|second)s?', part)
        if not m:
            raise ValueError('Unable to parse duration'
                             ' string: {}'.format(part))

        if m.group(2) == 'month':
            td_args['days'] = int(m.group(1)) * 30
        elif m.group(2) == 'year':
            td_args['days'] = int(m.group(1)) * 365
        else:
            td_args[m.group(2) + 's'] = int(m.group(1))

    return timedelta(**td_args)


def output(message):
    """
    Output a message to stdout and flush the output
    Adds a newline to the end of the message

    :param message: string - The message to be printed
    """
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def prefix(string, string_prefix):
    """
    Check to see if a prefix is present in a string
    If not, add it

    :param string: string - string to check against
    :param string_prefix: string - prefix to check
    """
    if string.startswith(string_prefix):
        return string
    else:
        return '%s%s' % (string_prefix, string)


def add_s3_prefix(s3_bucket):
    """
    Ensure a bucket has the s3:// prefix

    :param s3_bucket: string - The bucket name
    """
    s3_prefix = 's3://'
    return prefix(s3_bucket, s3_prefix)


def add_cf_prefix(cf_distribution):
    """
    Ensure a CloudFront distribution has the cf:// prefix

    :param cf_distribution: string - The distribution name
    """
    cf_prefix = 'cf://'
    return prefix(cf_distribution, cf_prefix)


def required_configuration(required_attributes):
    """
    Ensure all required configuration attributed are present for

    :param required_attributes: List(string) - List of attributed required
     to be in the s3 website configuration object passed into the function
    """
    def outer(function):
        """
        Outer function so we can pass in the function with a parameter in
         the decorator

        :param function: function - The function to be executed after the
         decorator
        """
        def inner(**kwargs):
            """
            Check the s3_website_config object against the required attributes
             list and error if any are not present

            :param **kwargs -
                s3_website_config: dict - Configuration for the website
                 creation
            """
            logger = logging.getLogger(log.ROOT_LOGGER_NAME)
            config = kwargs['s3_website_config']
            all_attributes_present = True
            for attr in required_attributes:
                if not hasattr(config, attr) or getattr(config, attr) is None:
                    logger.error("Missing configuration item '%s'" % attr)
                    all_attributes_present = False
            if all_attributes_present:
                return function(**kwargs)
            else:
                return False
        return inner
    return outer
