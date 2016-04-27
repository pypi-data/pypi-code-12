from plytix.retailers import enum
from plytix.retailers.fields import *
from plytix.retailers.models import BaseModel


PRODUCT_OWNERSHIP = enum(ALL='ALL', OWN='OWN', THIRD='THIRD')


class Product(BaseModel):
    """ Model: Product
    """
    def __init__(self, name, ean, gtin, jan, sku, upc, folder, thumb=None, id=None, brand_id=None, brand_name=None):
        """
        :param name: Name.
        :param owner: Owner.
        :param sku: SKU.
        :param folder: Parent folder.
        :param thumb: Thumbnail.
        :param id: Identifier.
        :param brand_id: Product's brand identifier.
        :param brand_name: Product's brand name.
        :return:
        """
        self.id = id
        self.name = name
        self.ean = ean
        self.gtin = gtin
        self.jan = jan
        self.sku = sku
        self.upc = upc
        self.thumb = thumb
        self.folder = folder

        self.brand_id = brand_id
        self.brand_name = brand_name

    def to_dict(self, include_id=True):
        """
        :return: A dictionary within the product's field.
        """
        product = {
            FIELD_PRODUCT_NAME: self.name,
            FIELD_PRODUCT_EAN: self.ean,
            FIELD_PRODUCT_GTIN: self.gtin,
            FIELD_PRODUCT_JAN: self.jan,
            FIELD_PRODUCT_SKU: self.sku,
            FIELD_PRODUCT_UPC: self.upc,
            FIELD_PRODUCT_FOLDER: self.folder,
        }
        if self.id and include_id:
            product[FIELD_PRODUCT_ID] = self.id
        if self.thumb:
            product[FIELD_PRODUCT_THUMB] = self.thumb
        if self.brand_id:
            product[FIELD_PRODUCT_BRAND_ID] = self.brand_id
        if self.brand_name:
            product[FIELD_PRODUCT_BRAND_NAME] = self.brand_name
        return product

    @staticmethod
    def parse(data):
        """
        :param data: The product data.
        :return: The Product object.
        """
        id = data[FIELD_PRODUCT_ID]
        name = data[FIELD_PRODUCT_NAME]
        ean = data[FIELD_PRODUCT_EAN]
        gtin = data[FIELD_PRODUCT_GTIN]
        jan = data[FIELD_PRODUCT_JAN]
        sku = data[FIELD_PRODUCT_SKU]
        upc = data[FIELD_PRODUCT_UPC]
        thumb = data[FIELD_PRODUCT_THUMB]
        folder = data[FIELD_PRODUCT_FOLDER]
        brand_id = data.get(FIELD_PRODUCT_BRAND_ID, None)
        brand_name = data.get(FIELD_PRODUCT_BRAND_NAME, None)

        return Product(name, ean, gtin, jan, sku, upc, folder, thumb=thumb, id=id, brand_id=brand_id, brand_name=brand_name)


class Picture(BaseModel):
    """ Model: Picture
    """
    def __init__(self, url_to_latest, url_to_version):
        """
        :param url_to_latest: URL to the latest version of this picture.
        :param url_to_version: URL to the current version of this picture.
        """
        self.url_to_latest = url_to_latest
        self.url_to_version = url_to_version

    def to_dict(self):
        """
        :return: A dictionary within the Picture's field.
        """
        picture = {
            FIELD_PICTURE_URL_TO_LATEST: self.url_to_latest,
            FIELD_PICTURE_URL_TO_VERSION: self.url_to_version,
        }

        return picture

    @staticmethod
    def parse(data):
        """
        :param data: The Picture data.
        :return: The Picture object.
        """
        url_to_latest = data.get(FIELD_PICTURE_URL_TO_LATEST)
        url_to_version = data.get(FIELD_PICTURE_URL_TO_VERSION)

        return Picture(url_to_latest, url_to_version)


class ProductPicture(BaseModel):
    """ Model: ProductPicture

        Represent a product picture object.
    """
    def __init__(self, picture_id, version, original, thumbs=None):
        """
        :param picture_id: ProductPicture identifier.
        :param version: ProductPicture's version.
        :param original: Picture object containing url to the original picture.
        :param thumbs: List of Picture objects containing url to the thumbnails requested.
        """
        self.version = version
        self.picture_id = picture_id
        self.original = original
        self.thumbs = thumbs

    def to_dict(self):
        """
        :return: A dictionary within the Picture's field.
        """
        picture = {
            FIELD_PRODUCT_PICTURE_PICTURE_ID: self.picture_id,
            FIELD_PRODUCT_PICTURE_VERSION: self.version,
            FIELD_PRODUCT_PICTURE_ORIGINAL: self.original,
            FIELD_PRODUCT_PICTURE_THUMBS: self.thumbs,
        }

        return picture

    @staticmethod
    def parse(data):
        """
        :param data: The Picture data.
        :return: The Picture object.
        """
        picture_id = data.get(FIELD_PRODUCT_PICTURE_PICTURE_ID)
        version = data.get(FIELD_PRODUCT_PICTURE_VERSION)
        original = data.get(FIELD_PRODUCT_PICTURE_ORIGINAL)
        if original:
            original = Picture.parse(original)

        thumbs = data.get(FIELD_PRODUCT_PICTURE_THUMBS)
        if thumbs:
            assert isinstance(thumbs, dict)
            thumbs = {size: Picture.parse(data) for size, data in thumbs.items()}
        return ProductPicture(picture_id, version, original, thumbs=thumbs)


class ProductPictureList(BaseModel):
    """ Model: ProductPictureList
    """
    def __init__(self, product_id, pictures):
        """
        :param id: Identifier.
        :param pictures: List of the product pictures.
        """
        self.product_id = product_id
        self.pictures = pictures

    def to_dict(self):
        """
        :return: A dictionary within the product's field.
        """
        product = {
            FIELD_PRODUCT_PICTURE_LIST_ID: self.product_id,
            FIELD_PRODUCT_PICTURE_LIST_PICTURES: [picture.to_dict() for picture in self.pictures],
        }
        return product

    @staticmethod
    def parse(data):
        """
        :param data: The product data.
        :return: The ProductPictureList object.
        """
        product_id = data[FIELD_PRODUCT_PICTURE_LIST_ID]
        pictures = [ProductPicture.parse(picture) for picture in data[FIELD_PRODUCT_PICTURE_LIST_PICTURES]]
        return ProductPictureList(product_id, pictures)