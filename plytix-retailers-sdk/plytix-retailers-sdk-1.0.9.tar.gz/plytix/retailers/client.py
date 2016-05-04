from plytix.retailers.connection import PlytixRetailersConnection
from plytix.retailers.services.data import DataEndpoint
from plytix.retailers.services.folders import FoldersEndpoint
from plytix.retailers.services.products import BankEndpoint, ProductsEndpoint
from plytix.retailers.services.sites import SitesEndpoint
from plytix.retailers.services.brands import BrandsEndpoint


class PlytixRetailersClient(object):
    """ Plytix client to consume the Plytix Retailers API. Thanks to the PlytixRetailersClient you will be able to
    integrate Plytix in your application in a easy way. You can manage sites, the products you manage
    or add new ones from the Plytix Products Bank.
    """
    def __init__(self, api_key, api_pwd):
        """
        :param api_key: API key.
        :param api_pwd: API password.
        :return: The PlytixRetialersClient initialized and ready to use.
        """
        self.api_key = api_key
        self.api_pwd = api_pwd
        self._connection = PlytixRetailersConnection(self.api_key, self.api_pwd)

        # Endpoints
        self._bank = None
        self._brands = None
        self._data = None
        self._folders = None
        self._sites = None
        self._products = None

    def __repr__(self):  # pragma: no cover
        class_name = self.__class__.__name__
        return '<{}: {} object>'.format(class_name, class_name)

    @property
    def bank(self):
        """
        :return: Access to the Plytix Products Bank's endpoint.
        """
        if not self._bank:
            self._bank = BankEndpoint(self._connection)
        return self._bank

    @property
    def brands(self):
        """
        :return: Access to the brand's endpoint.
        """
        if not self._brands:
            self._brands = BrandsEndpoint(self._connection)
        return self._brands

    @property
    def data(self):
        """
        :return: Access to the data's endpoint.
        """
        if not self._data:
            self._data = DataEndpoint(self._connection)
        return self._data

    @property
    def folders(self):
        """
        :return: Access to the folder's endpoint.
        """
        if not self._folders:
            self._folders = FoldersEndpoint(self._connection)
        return self._folders

    @property
    def products(self):
        """
        :return: Access to the product's endpoint.
        """
        if not self._products:
            self._products = ProductsEndpoint(self._connection)
        return self._products

    @property
    def sites(self):
        """
        :return: Access to the site's endpoint.
        """
        if not self._sites:
            self._sites = SitesEndpoint(self._connection)
        return self._sites









