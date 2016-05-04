from plytix.retailers.services import ResponseList, ResponseDict
from plytix.retailers.exceptions import PlytixRetailersAPIError, BadResponseError
from plytix.retailers.fields import *
from plytix.retailers.models.brand import Brand
from plytix.retailers.services import BaseEndpoint


class BrandsEndpoint(BaseEndpoint):
    """ Endpoint to consume brand resources.
    """
    _BASE_ENDPOINT = 'brands'
    _BASE_ENDPOINT_RESOURCE = 'brand'

    def search(self, name, page=None, page_length=None, fields=None, sort=None):
        """ Search brands
        :param name: Search by brand name.
        :param page: Result's page.
        :param page_length: The number of results by page.
        :param fields: Fields to retrieve.
        :param sort: Result's order.
        :return: ResponseList of Brand instances.
        """
        data = {
            INPUT_PRODUCTS_SEARCH_NAME: name
        }
        endpoint = self._BASE_ENDPOINT + '/search'
        try:
            response = super(BrandsEndpoint, self)._search(endpoint=endpoint, data=data, page=page, page_length=page_length, sort=sort, fields=fields)
            data = response.json()
            page = data[RESPONSE_METADATA][RESPONSE_METADATA_PAGE]
            total_pages = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL_PAGES]
            total = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL]

            return ResponseList([Brand.parse(brand) for brand in data[MODEL_ACCOUNTS]], page, total, total_pages)
        except Exception as e:
            raise e