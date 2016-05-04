from plytix.retailers.services import ResponseList, ResponseDict
from plytix.retailers.exceptions import PlytixRetailersAPIError, BadResponseError, ResourceNotFoundError
from plytix.retailers.fields import *
from plytix.retailers.models.folder import Folder
from plytix.retailers.models.product import Product, ProductPictureList
from plytix.retailers.services import BaseEndpoint


class ProductsEndpoint(BaseEndpoint):
    """ Client to consume the products you manage in your account.
    """
    _BASE_ENDPOINT = 'products'
    _BASE_ENDPOINT_RESOURCE = 'product'

    def get(self, id, fields=None):
        """ Get a product.
        :param id: Product's identifier.
        :param fields: Fields of the object to retrieve.
        :return: The product requested.
        """
        try:
            response = super(ProductsEndpoint, self)._get(id, fields=fields)
            if response:
                data = response.json()
                return Product.parse(data[MODEL_PRODUCT])
            return response
        except ResourceNotFoundError as rnf:
            return None
        except Exception as e:
            raise e

    def search(self, folder_list=None, name=None, operator=None, product_list=None, sku_list=None,
               page=None, page_length=None, fields=None, sort=None, group_by=None):
        """ Search products you manage.
        :param folder_list: Folder identifier's list.
        :param name: Search by product name.
        :param operator: [OPERATOR.AND, OPERATOR.OR] Modify the query behaviour to retrieve the union or the intersection of the parameters defined.
        :param product_list: Product identifier's list.
        :param sku_list: SKU identifier's list.
        :param page: Result's page.
        :param page_length: The number of results by page.
        :param fields: Fields to retrieve.
        :param sort: Result's order.
        :param group_by: Group results by account.
        :return: ResponseList object of Product instances.
        """
        data = {}
        if folder_list:
            data[INPUT_PRODUCTS_SEARCH_FOLDERS_LIST] = folder_list
        if group_by:
            data[INPUT_PRODUCTS_SEARCH_GROUP_BY] = group_by
        if name:
            data[INPUT_PRODUCTS_SEARCH_NAME] = name
        if operator:
            data[INPUT_PRODUCTS_SEARCH_OPERATOR] = operator
        if product_list:
            data[INPUT_PRODUCTS_SEARCH_PRODUCTS_LIST] = product_list
        if sku_list:
            data[INPUT_PRODUCTS_SEARCH_SKU_LIST] = sku_list

        endpoint = self._BASE_ENDPOINT
        try:
            response = super(ProductsEndpoint, self)._search(endpoint=endpoint, data=data, page=page, page_length=page_length, sort=sort, fields=fields)
            data = response.json()
            page = data[RESPONSE_METADATA][RESPONSE_METADATA_PAGE]
            total_pages = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL_PAGES]
            total = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL]

            if group_by == PRODUCTS_SEARCH_GROUP_BY_BRAND:
                brands = {}
                if MODEL_ACCOUNTS in data:
                    for account in data[MODEL_ACCOUNTS]:
                        brand = account[MODEL_ACCOUNT]['id']
                        brand_name = account[MODEL_ACCOUNT]['name']

                        brands[brand] = {
                            'name': brand_name,
                            'products': [Product.parse(product) for product in account[MODEL_PRODUCTS]]
                        }
                    return ResponseDict(brands, page, total, total_pages)
                else:
                    raise BadResponseError
            else:
                return ResponseList([Product.parse(product) for product in data[MODEL_PRODUCTS]], page, total, total_pages)
        except Exception as e:
            raise e

    def search_and_group_by_brand(self, **kwargs):
        """ Quick access to search products and group the results by brands.
        :param kwargs: Search's method parameters.
        :return: ResponseDict object where each key is the brand identifier and contains a list of Product instances.
        """
        if 'group_by' in kwargs:
            raise KeyError('group_by')
        return self.search(group_by=PRODUCTS_SEARCH_GROUP_BY_BRAND, **kwargs)

    def pictures(self, product_list, sizes=None, page=None, page_length=None, fields=None, sort=None):
        """ Returns the pictures of each product.
            It returns the url to the originals and the thumbnails for the sizes specified.

            For each url (original or thumbnail) it returns the url to the latest version and also the url
            to the current version.


        :param product_list: Product identifier's list.
        :param sizes: Picture sizes list. A size must follow the format "<width>x<height>", e.g "200x200".
        :param page: Result's page.
        :param page_length: The number of results by page.
        :param fields: Fields to retrieve.
        :param sort: Result's order.
        :return: ResponseList of ProductPictures instances.
        """
        if not isinstance(product_list, list):
            raise TypeError('product_list must be a list.')

        if sizes:
            if not isinstance(sizes, list):
                raise TypeError('sizes must be a list.')


        data = {
            INPUT_PRODUCT_LIST: product_list,
        }
        if sizes:
            data[INPUT_PRODUCT_PICTURE_SIZES] = sizes

        endpoint = 'pictures'
        try:
            response = super(ProductsEndpoint, self)._search(endpoint=endpoint, data=data, page=page,
                                                             page_length=page_length, sort=sort, fields=fields)
            data = response.json()
            page = data[RESPONSE_METADATA][RESPONSE_METADATA_PAGE]
            total_pages = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL_PAGES]
            total = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL]
            items = [ProductPictureList.parse(product) for product in data[MODEL_PRODUCTS]]
            return ResponseList(items, page, total, total_pages)
        except Exception as e:
            raise e


class BankEndpoint(BaseEndpoint):
    """ Client to consume the Plytix Products Bank. You can search products and add them to your managed products.
    """
    _BASE_ENDPOINT = 'bank'

    def search(self, brand_id=None, folder_id=None, name=None, name_list=None, product_id=None, operator=None,
               identifier_list=None, identifier=None, ean_list=None, ean=None, gtin_list=None, gtin=None,
               jan_list=None, jan=None, sku_list=None, sku=None, upc_list=None, upc=None,
               page=None, page_length=None, fields=None, sort=None):
        """ Search products in the Plytix Products Bank.
        :param brand_id: Brand identifier.
        :param folder_id: Folder identifier.
        :param name: Search by product name.
        :param name_list: Search by a list of product names.
        :param product_id: Product identifier.
        :param operator: [OPERATOR.AND, OPERATOR.OR] Modify the query behaviour to retrieve the union or the intersection of the parameters defined.
        :param identifier_list: Global identifier's list.
        :param identifier: Search by an identifier.
        :param ean_list: EAN's list.
        :param ean: Search by EAN.
        :param gtin_list: GTIN's list.
        :param gtin: Search by GTIN.
        :param jan_list: JAN's list.
        :param jan: Search by JAN.
        :param sku_list: SKU identifier's list.
        :param sku: Search by SKU.
        :param upc_list: UPC's list.
        :param upc: Search by UPC.
        :param page: Result's page.
        :param page_length: The number of results by page.
        :param fields: Fields to retrieve.
        :param sort: Result's order.
        :return: ResponseList object of Product instances.
        """
        data = {}
        if brand_id:
            data[INPUT_BANK_SEARCH_ACCOUNT] = brand_id
        if folder_id:
            data[INPUT_BANK_SEARCH_FOLDER] = folder_id
        if name:
            data[INPUT_BANK_SEARCH_NAME] = name
        if name_list:
            data[INPUT_BANK_SEARCH_NAME_LIST] = name_list
        if operator:
            data[INPUT_BANK_SEARCH_OPERATOR] = operator
        if product_id:
            data[INPUT_BANK_SEARCH_PRODUCT] = product_id

        # References
        if identifier_list:
            data[INPUT_BANK_SEARCH_IDENTIFIER_LIST] = identifier_list
        if identifier:
            data[INPUT_BANK_SEARCH_IDENTIFIER] = identifier
        if ean_list:
            data[INPUT_BANK_SEARCH_EAN_LIST] = ean_list
        if ean:
            data[INPUT_BANK_SEARCH_EAN] = ean
        if gtin_list:
            data[INPUT_BANK_SEARCH_GTIN_LIST] = gtin_list
        if gtin:
            data[INPUT_BANK_SEARCH_GTIN] = gtin
        if jan_list:
            data[INPUT_BANK_SEARCH_JAN_LIST] = jan_list
        if jan:
            data[INPUT_BANK_SEARCH_JAN] = jan
        if sku_list:
            data[INPUT_BANK_SEARCH_SKU_LIST] = sku_list
        if sku:
            data[INPUT_BANK_SEARCH_SKU] = sku
        if upc_list:
            data[INPUT_BANK_SEARCH_UPC_LIST] = upc_list
        if upc:
            data[INPUT_BANK_SEARCH_UPC] = upc

        endpoint = self._BASE_ENDPOINT
        try:
            response = super(BankEndpoint, self)._search(endpoint=endpoint, data=data, page=page, page_length=page_length, sort=sort, fields=fields)
            data = response.json()
            page = data[RESPONSE_METADATA][RESPONSE_METADATA_PAGE]
            total_pages = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL_PAGES]
            total = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL]

            return ResponseList([Product.parse(product) for product in data[MODEL_PRODUCTS]], page, total, total_pages)
        except Exception as e:
            raise e

    def add_to(self, destination_folder, folders_list=None, products_list=None):
        """ Add products to your managed products. You must define your destination folder and a folder identifier's list or a product identifier's list.
        :param destination_folder: Folder where store the products to add.
        :param folders_list: Folder identifier's list. All products contained in them will be added to your account.
        :param products_list: Product identifier's list. All of them will be added to your account.
        :return: A list of dictionaries including the product's public ID and the product ID for your account.
        """
        if not isinstance(destination_folder, Folder):
            raise TypeError('Destination folder must be a Folder instance.')

        if not folders_list and not products_list:
            raise ValueError('No folder_list or products_list defined.')

        data = {
            INPUT_BANK_ADD_DESTINATION: destination_folder.id
        }
        if products_list:
            if not isinstance(products_list, list):
                raise ValueError('products_list must be a list.')
            data[INPUT_BANK_ADD_PRODUCTS] = products_list

        if folders_list:
            if not isinstance(folders_list, list):
                raise ValueError('folders_list must be a list.')
            data[INPUT_BANK_ADD_FOLDERS] = folders_list

        endpoint = self._BASE_ENDPOINT + '/add'
        try:
            response = super(BankEndpoint, self)._create(endpoint=endpoint, data=data)
            data = response.json()
            if not data[RESPONSE_METADATA][RESPONSE_SUCCESS]:
                return None
            return data[RESPONSE_PRODUCTS_ADDED]
        except Exception as e:
            raise e







