'''
    flaskext.fulfil
    ---------------

    A Flask extension providing Fulfil.IO Api access.

    :copyright: (c) 2016 by Fulfil.IO Inc.
    :license: BSD, see LICENSE for more details.
'''
from fulfil_client import Client

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Fulfil.Io Inc.'
__license__ = 'BSD'
__copyright__ = '(c) 2016 by Fulfil.IO Inc.'
__all__ = ['Fulfil']


class Fulfil(object):
    """

    To get started you will wrap your application's app object something like
    this::

        app = Flask(__name__)
        fulfil = Fulfil(app)

    Configuration::

        FULFIL_SUBDOMAIN: the subdomain of your Fulfil account.
        FULFIL_API_KEY: The API_KEY to access Fulfil services.

    :param app: The Flask application object. Defaults to None.
    """
    client = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        '''Initalizes the application with the extension.
        :param app: The Flask application object.
        '''
        self.client = Client(
            app.config['FULFIL_SUBDOMAIN'],
            app.config['FULFIL_API_KEY'],
        )

    def model(self, name):
        return self.client.model(name)

    def record(self, model_name, record_id):
        return self.client.record(model_name, record_id)
