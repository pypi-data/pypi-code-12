from plytix.retailers.models import BaseModel
from plytix.retailers.fields import FIELD_BRAND_ID, FIELD_BRAND_NAME, FIELD_BRAND_WEBSITE, FIELD_BRAND_PICTURE


class Brand(BaseModel):
    """ Model: Brand
    """
    def __init__(self, name, website=None, picture=None, id=None):
        """
        :param name: Name.
        :param website: Website.
        :param picture: Picture.
        :param id: Identifier.
        :return:
        """
        self.id = id
        self.name = name
        self.website = website
        self.picture = picture

    def to_dict(self, include_id=True):
        """
        :return: A dictionary within the brand's field.
        """
        brand = {
            FIELD_BRAND_NAME: self.name,
        }
        if self.id and include_id:
            brand[FIELD_BRAND_ID] = self.id
        if self.website:
            brand[FIELD_BRAND_WEBSITE] = self.website
        if self.picture:
            brand[FIELD_BRAND_PICTURE] = self.picture
        return brand

    @staticmethod
    def parse(data):
        """
        :param data: The brand data.
        :return: The brand object.
        """
        name = data[FIELD_BRAND_NAME]
        id = data.get(FIELD_BRAND_ID, None)
        website = data.get(FIELD_BRAND_WEBSITE, None)
        picture = data.get(FIELD_BRAND_PICTURE, None)

        return Brand(name, website=website, picture=picture, id=id)
