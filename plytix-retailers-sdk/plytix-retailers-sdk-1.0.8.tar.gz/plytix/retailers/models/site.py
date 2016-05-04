from plytix.retailers.exceptions import *
from plytix.retailers.fields import *
from plytix.retailers.models import BaseModel


FIELD_SITE_INFO_SYNC_PICTURES = 'sync_pictures'
FIELD_SITE_INFO_PLATFORM_NAME = 'platform_name'
FIELD_SITE_INFO_PLATFORM_VERSION = 'platform_version'
FIELD_SITE_INFO_SUBPLATFORM_NAME = 'subplatform_name'
FIELD_SITE_INFO_SUBPLATFORM_VERSION = 'subplatform_version'
FIELD_SITE_INFO_PLYTIX_PLUGIN_VERSION = 'plytix_plugin_version'
FIELD_SITE_INFO_USE_CDN = 'use_cdn'


class Site(BaseModel):
    """ Model: Site
    """
    def __init__(self, debug, name, protocol, timezone, url, info=None, id=None):
        """ Initialize a site object.
        :param debug: Test mode.
        :param name: Name.
        :param protocol: Protocol.
        :param timezone: Timezone.
        :param url: Url.
        :param info: Dictionary with extra information about the site.
        :param id: Identifier.
        :return: The site object.
        """
        if info:
            if not isinstance(info, dict):
                raise ValueError('info must be a dictionary but is {}.'.format(type(info)))

        self.debug = debug
        self.name = name
        self.protocol = protocol
        self.timezone = timezone
        self.url = url
        self.info = info
        self.id = id

    def to_dict(self, include_id=True):
        """
        :return: A dictionary within the site's fields.
        """
        try:
            site = {
                FIELD_SITE_DEBUG: self.debug,
                FIELD_SITE_NAME: self.name,
                FIELD_SITE_URL: self.url,
            }

            if self.protocol:
                site[FIELD_SITE_PROTOCOL] = self.protocol

            if self.timezone:
                site[FIELD_SITE_TIMEZONE] = self.timezone

            if self.info:
                site[FIELD_SITE_INFO] = self.info

            if self.id and include_id:
                site[FIELD_SITE_ID] = self.id

            return site
        except Exception as e:
            raise BadRequestError

    @staticmethod
    def parse(data):
        id = data.get(FIELD_SITE_ID, None)
        debug = data.get(FIELD_SITE_DEBUG, None)
        name = data.get(FIELD_SITE_NAME, None)
        protocol = data.get(FIELD_SITE_PROTOCOL, None)
        timezone = data.get(FIELD_SITE_TIMEZONE, None)
        url = data.get(FIELD_SITE_URL, None)
        info =data.get(FIELD_SITE_INFO, None)

        return Site(debug=debug, name=name, protocol=protocol, timezone=timezone, url=url, info=info, id=id)

