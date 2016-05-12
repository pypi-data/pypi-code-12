import logging
import os
import subprocess

from requests_kerberos import HTTPKerberosAuth, OPTIONAL
from requests_ntlm import HttpNtlmAuth


class Authenticator(object):
    """
    The Authenticator class is an abstract class for shared functionality
    between the possible authentication types.
    """

    def get_auth_handler(self, session):
        raise NotImplementedError("override this method")

    @staticmethod
    def get_auth_type():
        raise NotImplementedError("override this method")


class KerberosAuthenticator(Authenticator):
    """
    The KerberosAuthenticator uses the local Kerberos install to
    authenticate a user who's machine is logged into to the Domain.
    """

    def __init__(self):
        # Windows does not have support for `klist`. Assume
        # Windows users have a valid Kerberos ticket.
        if os.name != 'nt':
            try:
                subprocess.check_output(['klist', '-s'])
            except subprocess.CalledProcessError:
                logging.info("no kerberos ticket found. running kinit")
                try:
                    subprocess.check_output(['kinit'])
                except subprocess.CalledProcessError:
                    raise Exception("failed to generate a kerberos ticket")

    def get_auth_handler(self, session):
        return HTTPKerberosAuth(mutual_authentication=OPTIONAL)

    @staticmethod
    def get_auth_type():
        return 'kerberos'


class NtlmAuthenticator(Authenticator):
    """
    The NtlmAuthenticator authenticates users with basic credentials
    and a domain.
    """

    def __init__(self, username, password, domain):
        self.username = username
        self.password = password
        self.domain = domain

    def get_auth_handler(self, session):
        return HttpNtlmAuth(
            "{}\\{}".format(self.domain, self.username),
            self.password,
            session
        )

    @staticmethod
    def get_auth_type():
        return 'ntlm'


class KeytabAuthenticator(Authenticator):
    """
    The KeytabAuthenticator allows users to sign keytabs with
    their password and then request valid Kerberos tickets
    with those keytabs without requiring password input.
    """

    def __init__(self, username, keytab, domain):
        self.username = username
        self.keytab = keytab
        self.domain = domain

        if os.name == 'nt':
            raise Exception("keytab is not supported on Windows!")

        # Setup a temporary credentials cache
        credentials_cache = os.path.join(os.getcwd(), 'credentials_cache')
        os.environ['KRB5CCNAME'] = credentials_cache

        # Call kinit to generate a Kerberos ticket for the given username and keytab
        try:
            subprocess.check_output(['kinit', '-c', credentials_cache, '-kt', self.keytab,
                                     "{}@{}".format(self.username, self.domain)])
        except subprocess.CalledProcessError:
            raise Exception("could not generate a valid ticket for the given keytab")

    def get_auth_handler(self, session):
        return HTTPKerberosAuth(mutual_authentication=OPTIONAL)

    @staticmethod
    def get_auth_type():
        return 'keytab'

