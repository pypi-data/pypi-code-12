from plytix.retailers.exceptions import *
from plytix.retailers.fields import *
from plytix.retailers.models.site import Site
from plytix.retailers.services import BaseEndpoint, ResponseList


class SitesEndpoint(BaseEndpoint):
    """ Client to consume the sites you manage in your account.
    """
    _BASE_ENDPOINT = 'sites'
    _BASE_ENDPOINT_RESOURCE = 'site'

    def __init__(self, connection):
        """ Initialize the client to retrieve Sites.
        :param connection: The PlytixRetailersConnection with your credentials.
        :return: The SitesEndpoint object initialized.
        """
        super(SitesEndpoint, self).__init__(connection)

    def create(self, site, fields=None):
        """ Create a new site.
        :param site: Site instance for the new site to create.
        :param fields: Fields to retrieve.
        :return: The site has just added to your account. Now, the site includes its unique identifier.
        """
        if not isinstance(site, Site):
            raise TypeError('Not valid site.')

        try:
            response = super(SitesEndpoint, self)._create(site, fields=fields)
            data = response.json()
            return Site.parse(data[MODEL_SITE])
        except Exception as e:
            raise e

    def get(self, id, fields=None):
        """ Get a site.
        :param id: Site's identifier.
        :param fields: Fields of the object to retrieve.
        :return: Site instance of the site requested.
        """
        try:
            response = super(SitesEndpoint, self)._get(id, fields=fields)
            if response:
                data = response.json()
                return Site.parse(data[MODEL_SITE])
            return response
        except ResourceNotFoundError as rnf:
            return None
        except Exception as e:
            raise e

    def list(self, page=None, page_length=None, fields=None, sort=None):
        """ List your sites.
        :param page: Result's page.
        :param page_length: Result's limit.
        :param fields: Fields to retrieve.
        :param sort: Result's order.
        :return: ResponseList of Site instances.
        """
        try:
            response = super(SitesEndpoint, self)._list(page=page, page_length=page_length, sort=sort, fields=fields)
            data = response.json()

            page = data[RESPONSE_METADATA][RESPONSE_METADATA_PAGE]
            total_pages = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL_PAGES]
            total = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL]

            return ResponseList([Site.parse(site) for site in data[MODEL_SITES]], page, total, total_pages)
        except Exception as e:
            raise e

    def search(self, name=None, url=None, protocol=None, page=None, page_length=None, fields=None, sort=None):
        """ Search into your sites.
        :param name: Name.
        :param url: Url.
        :param protocol: Protocol.
        :param page: Result's page.
        :param page_length: The number of results by page.
        :param fields: Fields to retrieve.
        :param sort: Result's order.
        :return: ResponseList object of Site instances.
        """
        data = {}
        if name:
            data[INPUT_SITES_SEARCH_NAME] = name
        if protocol:
            data[INPUT_SITES_SEARCH_PROTOCOL] = protocol
        if url:
            data[INPUT_SITES_SEARCH_URL] = url

        try:
            response = super(SitesEndpoint, self)._search(data=data, page=page, page_length=page_length, sort=sort, fields=fields)
            data = response.json()
            page = data[RESPONSE_METADATA][RESPONSE_METADATA_PAGE]
            total_pages = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL_PAGES]
            total = data[RESPONSE_METADATA][RESPONSE_METADATA_TOTAL]

            return ResponseList([Site.parse(site) for site in data[MODEL_SITES]], page, total, total_pages)
        except Exception as e:
            raise e

    def update(self, site, fields=None):
        """ Save the changes made in a Site instance.
        :param site: Site instance including the changes to save.
        :param fields: Fields of the object to retrieve.
        :return: The Site instance of the updated site after saves it.
        """
        if not isinstance(site, Site):
            raise TypeError('No valid site.')

        try:
            response = super(SitesEndpoint, self)._update(site, fields=fields)
            data = response.json()
            return Site.parse(data[MODEL_SITE])
        except Exception as e:
            raise e










