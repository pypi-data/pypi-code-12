import argparse
import logging
import os
import sys
import time

from kerb_sts import auth
from kerb_sts.config import Config
from kerb_sts.handler import KerberosHandler

DEFAULT_REGION = 'us-east-1'


def _get_default_credentials_filename():
    """
    Returns the path to the default AWS credentials file. This
    is where the temporary access keys will be stored unless
    otherwised specified by the user.
    :return: The path to the default credentials file
    """

    return os.path.expanduser('~/.aws/credentials')


def _get_options():
    """
    Parses the command line options.
    :return: an options object
    """
    parser = argparse.ArgumentParser(description="Generates 1 hour temporary AWS IAM credentials.")
    parser.add_argument('--adfs', help="ADFS IdP domain name",
                        dest='adfs_url')
    parser.add_argument('-c', '--credentials_file', help="AWSCLI credentials file (defaults ~/.aws/credentials)",
                        dest='credentials_file', default=_get_default_credentials_filename())
    parser.add_argument('--configure', help="Sets up Kerb-STS by generating a config file at ~/.kerb-sts/config",
                        dest='configure', action='store_true', default=False)
    parser.add_argument('--daemon', help="Run as a daemon. This will auto-renew credentials every half hour",
                        dest='daemon', action='store_true', default=False)
    parser.add_argument('-r', '--default_role', help="Name of the Role to use as the default",
                        dest='default_role', default=None)
    parser.add_argument('-d', '--domain', help="AD Domain if using a Kerberos keytab or NTLM auth. Requires a username and password/keytab",
                        dest='domain', default=None)
    parser.add_argument('--keytab', help="The Kerberos keytab file. Requires a username and domain",
                        dest='keytab', default=None)
    parser.add_argument('--list', help="List the available roles",
                        dest='list', action='store_true', default=False)
    parser.add_argument('-p', '--password', help="AD Password if generating a temporary Kerberos token. Requires a username and domain",
                        dest='password', default=None)
    parser.add_argument('--refresh', help="Time to wait (minutes) between refreshing the tokens.",
                        dest='refresh', default=30)
    parser.add_argument('--region', help="AWS Region for STS (defaults to {})".format(DEFAULT_REGION),
                        dest='region', default=DEFAULT_REGION)
    parser.add_argument('-u', '--username', help="AD Username if generating a temporary Kerberos token. Requires a domain and password/keytab",
                        dest='username', default=None)
    parser.add_argument('-v', '--verbose', help="Turns on debug logging",
                        dest="verbose", action='store_true', default=None)
    return parser.parse_args()


def _setup_logging(options):
    """
    Sets up logging based on some command line options.
    :param options: options parsed from the command line
    """
    if options.verbose:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging_level)
    logging.debug("logging level set to {}".format(logging_level))


def _configure():
    """
    Generates a configuration file for subsequent runs to consume.
    """
    adfs_url = raw_input(
        "ADFS AWS sign in URL ie: "
        "https://yourdomain.com/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices): "
    )
    region = raw_input("AWS region. defaults to {}: ".format(DEFAULT_REGION))
    if region == '':
        region = DEFAULT_REGION

    config = Config(adfs_url=adfs_url, region=region)
    config.save()


def _setup_config(options):
    """
    Creates a config object and overrides any values
    provided on the command line.
    :param options: parsed command line options
    :return: the Config object
    """
    config = Config.load()

    if options.adfs_url:
        config.adfs_url = options.adfs_url
    logging.debug("adfs url set to {}".format(config.adfs_url))

    if options.region:
        config.region = options.region
    logging.debug("region set to {}".format(config.region))

    return config


def _setup_authenticator(options):
    """
    Creates an Authenticator object based on
    what credential information was passed as arguments.
    :param options: pasred command line options
    :return: an Authenticator object
    """
    if options.username and options.domain:
        if options.password:
            authenticator = auth.NtlmAuthenticator(
                username=options.username,
                password=options.password,
                domain=options.domain
            )
        elif options.keytab:
            authenticator = auth.KeytabAuthenticator(
                username=options.username,
                keytab=options.keytab,
                domain=options.domain
            )
        else:
            raise Exception("username and domain provided but no password or keytab was given")
    elif options.username or options.domain:
        raise Exception("both username and domain are required for ntlm or keytab authentication")
    else:
        authenticator = auth.KerberosAuthenticator()

    return authenticator


def _generate_tokens(options, config, authenticator):
    """
    Generates a set of AWS IAM credentials for each available role
    for the principal.
    :param options: the parsed command line arguments
    :param config: the kerb configuration
    :param authenticator: the Authenticator object used to handle ADFS authentication
    """
    logging.info("--------------------------------")
    if options.list:
        logging.info("    listing available roles     ")
    else:
        logging.info("       generating tokens        ")
    logging.info("--------------------------------")

    logging.info("region: {}".format(config.region))
    logging.info("url: {}".format(config.adfs_url))
    logging.info("credentials file: {}".format(options.credentials_file))
    if options.default_role:
        logging.info("default role: {}".format(options.default_role))
    logging.info("auth type: {}".format(authenticator.get_auth_type()))

    h = KerberosHandler()
    h.handle_sts_by_kerberos(config.region, config.adfs_url, options.credentials_file,
                             options.default_role, options.list, authenticator)
    logging.info("--------------------------------")


def main():
    """
    Application entrypoint. Parses the command line options, sets up the configuration for the token
    generation, and then starts generating token(s) for the given options.
    :return:
    """
    options = _get_options()

    _setup_logging(options)

    if options.configure:
        _configure()
        sys.exit(0)

    config = _setup_config(options)
    if not config.is_valid():
        logging.error(
            "invalid configuration. please run --configure to generate a config file or supply a valid ADFS URL")
        sys.exit(1)

    try:
        authenticator = _setup_authenticator(options)
    except Exception as ex:
        logging.error(ex)
        sys.exit(1)

    while True:
        try:
            _generate_tokens(options, config, authenticator)
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        if not options.daemon:
            break
        logging.info('')
        time.sleep(60 * options.refresh)

if __name__ == "__main__":
    main()
