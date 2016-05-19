import awsauthhelper
from argparse import Namespace


class Base(Namespace):
    def init_credentials(self):
        self._credentials = awsauthhelper.Credentials(**vars(self))

        if self._credentials.has_role():
            self._credentials.assume_role()
        self.session = self._credentials.create_session()  # use session() instead of 'boto3'
