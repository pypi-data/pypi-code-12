from plytix.retailers.exceptions import PlytixRetailersAPIError, ResourceNotFoundError
from plytix.retailers.fields import *
from plytix.retailers.models.folder import Folder
from plytix.retailers.models.product import PRODUCT_OWNERSHIP
from plytix.retailers.services import BaseEndpoint


class FoldersEndpoint(BaseEndpoint):
    """ Client to consume the folders you manage in your account.
    """
    _BASE_ENDPOINT = 'folders'

    def __init__(self, conn):
        """ Initialize the client to retrieve folders
        :param client: The retailers API Connection with your credentials.
        :return: The FoldersEndpoint object initialized.
        """
        super(FoldersEndpoint, self).__init__(conn)

    def create(self, name, parent_id=None, fields=None):
        """ Create a new folder.
        :param name: The name of the folder to add to your account.
        :param parent_id: The identifier of the parent folder.
        :return: Folder instance of the folder has been created.
        """
        data = {
            'name': name
        }

        endpoint = self._BASE_ENDPOINT
        if parent_id:
            endpoint += '/{id}'.format(id=parent_id)

        try:
            response = super(FoldersEndpoint, self)._create(data=data, endpoint=endpoint, fields=fields)
            data = response.json()
            return Folder.parse(data[MODEL_FOLDER])
        except Exception as e:
            raise PlytixRetailersAPIError(e.message)

    def get(self, id=None, show=PRODUCT_OWNERSHIP.ALL, fields=None, page_length=None, page=None, sort=None):
        """ Get a folder.
        :param id: Identifier of the folder to retrieve. If it is not defined, the method returns the root's folder.
        :param show: Filter the folder by the products ownership. Use the plytix.retailers.models.product.PRODUCT_OWNERSHIP object:
            - PRODUCT_OWNERSHIP.ALL. Show all products.
            - PRODUCT_OWNERSHIP.OWN. Show only your products, added from the Products Feed.
            - PRODUCT_OWNERSHIP.THIRD. Show the products added from the Products Bank.
        :param fields: Fields to retrieve.
        :param page: Result's page.
        :param sort: Result's order.
        :param page_length: The number of results by page.
        :return: Folder instance.
        """

        endpoint = 'folders'
        if id:
            endpoint += '/{id}'.format(id=id)

        qs = {
            INPUT_PRODUCTS_SHOW: show
        }
        if page:
            qs[RESPONSE_METADATA_PAGE] = page
        if sort:
            qs[INPUT_SORT] = sort
        if page_length:
            qs[INPUT_PAGE_LENGTH] = page_length

        try:
            response = super(FoldersEndpoint, self)._get(id, fields=fields, endpoint=endpoint, query_string=qs)
            if response:
                data = response.json()
                return Folder.parse(data[MODEL_FOLDER])
            return response
        except ResourceNotFoundError as rnf:
            return None
        except Exception as e:
            raise e
