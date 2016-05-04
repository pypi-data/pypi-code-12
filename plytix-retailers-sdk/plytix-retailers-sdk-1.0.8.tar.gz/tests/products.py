from plytix.retailers import API_URL
from plytix.retailers.exceptions import *
from plytix.retailers.fields import RESPONSE_PRODUCTS_ADDED, RESPONSE_PRODUCT_BANK_ID, RESPONSE_PRODUCT_ID
from plytix.retailers.models.folder import Folder
from plytix.retailers.models.product import Product, Picture, ProductPicture, ProductPictureList, PRODUCT_OWNERSHIP
from plytix.retailers.models import OPERATOR
from tests import RetailersTestCase

import httpretty


class TestRetailersProducts(RetailersTestCase):

    @httpretty.activate
    def test_retailers_products(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="product/555f14711d5ca72ddedd596a"),
                               '''
                               {
                                   "meta": {
                                       "success": true
                                   },
                                   "product": {
                                       "ean": "PROD-00003",
                                       "gtin": "PROD-00003",
                                       "jan": "PROD-00003",
                                       "sku": "PROD-00003",
                                       "upc": "PROD-00003",
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/555f14711d5ca72ddedd596a",
                                       "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                       "folder": "5575499c1d5ca70f37d01d5c",
                                       "id": "555f14711d5ca72ddedd596a",
                                       "name": "Brand product 3"
                                   }

                               }
                               ''',
                               status=200)

        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="products"),
                               '''
                               {
                                   "meta": {
                                       "total": 3,
                                       "total_pages": 2,
                                       "page": 1,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/555f14711d5ca72ddedd596a",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "folder": "5575499c1d5ca70f37d01d5c",
                                           "id": "555f14711d5ca72ddedd596a",
                                           "name": "Brand product 3"
                                       },
                                       {
                                           "ean": "PROD-00004",
                                           "gtin": "PROD-00004",
                                           "jan": "PROD-00004",
                                           "sku": "PROD-00004",
                                           "upc": "PROD-00004",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/555f14711d5ca72ddedd596b",
                                           "thumb": "http://product.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "folder": "5575499d1d5ca70f37d01d5f",
                                           "id": "555f14711d5ca72ddedd596b",
                                           "name": "Brand product 4"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        products = self.client.products.search()
        self.assertGreater(len(products), 0)

        product = products[0]
        self.assertEqual(product.id, '555f14711d5ca72ddedd596a')
        retrieved_product = self.client.products.get(product.id)

        self.assertIsNotNone(retrieved_product)
        self.assertEqual(product.id, retrieved_product.id)
        self.assertEqual(product.name, retrieved_product.name)
        self.assertEqual(product.thumb, retrieved_product.thumb)
        self.assertEqual(product.sku, retrieved_product.sku)

    @httpretty.activate
    def test_retailers_products_params(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="product/555f14711d5ca72ddedd596a"),
                               '''
                               {
                                   "meta": {
                                       "success": true
                                   },
                                   "product": {
                                       "ean": "PROD-00003",
                                       "gtin": "PROD-00003",
                                       "jan": "PROD-00003",
                                       "sku": "PROD-00003",
                                       "upc": "PROD-00003",
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/555f14711d5ca72ddedd596a",
                                       "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                       "folder": "5575499c1d5ca70f37d01d5c",
                                       "id": "555f14711d5ca72ddedd596a",
                                       "name": "Brand product 3"
                                   }

                               }
                               ''',
                               status=200)

        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="products"),
                               '''
                               {
                                   "meta": {
                                       "total": 3,
                                       "total_pages": 2,
                                       "page": 1,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/555f14711d5ca72ddedd596a",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "folder": "5575499c1d5ca70f37d01d5c",
                                           "id": "555f14711d5ca72ddedd596a",
                                           "name": "Brand product 3"
                                       },
                                       {
                                           "ean": "PROD-00004",
                                           "gtin": "PROD-00004",
                                           "jan": "PROD-00004",
                                           "sku": "PROD-00004",
                                           "upc": "PROD-00004",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/555f14711d5ca72ddedd596b",
                                           "thumb": "http://product.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "folder": "5575499d1d5ca70f37d01d5f",
                                           "id": "555f14711d5ca72ddedd596b",
                                           "name": "Brand product 4"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        products = self.client.products.search(folder_list=['5575499c1d5ca70f37d01d5c', '5575499d1d5ca70f37d01d5f'],
                                               name='Brand',
                                               operator=OPERATOR.AND,
                                               product_list=['555f14711d5ca72ddedd596b', '555f14711d5ca72ddedd596a'],
                                               sku_list=['PROD-00003', 'PROD-00004'])
        self.assertGreater(len(products), 0)

        product = products[0]
        self.assertEqual(product.id, '555f14711d5ca72ddedd596a')
        retrieved_product = self.client.products.get(product.id)

        self.assertIsNotNone(retrieved_product)
        self.assertEqual(product.id, retrieved_product.id)
        self.assertEqual(product.name, retrieved_product.name)
        self.assertEqual(product.thumb, retrieved_product.thumb)
        self.assertEqual(product.sku, retrieved_product.sku)

    @httpretty.activate
    def test_retailers_products_grouped_by_brand(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="products"),
                               '''
                               {
                                   "brands": [
                                       {
                                           "brand": {
                                               "id": "555efda31d5ca71fe489e798",
                                               "name": "Brand Account"
                                           },
                                           "products": [
                                               {
                                                   "ean": "PROD-00004",
                                                   "gtin": "PROD-00004",
                                                   "jan": "PROD-00004",
                                                   "sku": "PROD-00004",
                                                   "upc": "PROD-00004",
                                                   "thumb": "https://analytics.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                                   "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/557152491d5ca710c428dc03",
                                                   "folder": "557152471d5ca710c428dbff",
                                                   "id": "557152491d5ca710c428dc03",
                                                   "name": "Brand product 4"
                                               },
                                               {
                                                   "ean": "PROD-00003",
                                                   "gtin": "PROD-00003",
                                                   "jan": "PROD-00003",
                                                   "sku": "PROD-00003",
                                                   "upc": "PROD-00003",
                                                   "thumb": "https://analytics.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                                   "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/557152491d5ca710c428dc02",
                                                   "folder": "557152471d5ca710c428dbff",
                                                   "id": "557152491d5ca710c428dc02",
                                                   "name": "Brand product 3"
                                               }
                                           ]
                                       }
                                   ],
                                   "meta": {
                                       "total": 39,
                                       "total_pages": 20,
                                       "page": 1,
                                       "success": true
                                   }
                               }
                               ''',
                               status=200)

        brands = self.client.products.search_and_group_by_brand()

        self.assertEqual(len(brands), 1)

        brand = brands['555efda31d5ca71fe489e798']
        self.assertEqual(brand['name'], 'Brand Account')
        self.assertEqual(len(brand['products']), 2)
        self.assertIsInstance(brand['products'][0], Product)
        self.assertIsInstance(brand['products'][1], Product)

    def test_retailers_products_grouped_by_brand_wrong(self):
        try:
            brands = self.client.products.search_and_group_by_brand(group_by=PRODUCT_OWNERSHIP.THIRD)
            self.assertEqual(True, False)
        except Exception as e:
            self.assertIsInstance(e, KeyError)

    @httpretty.activate
    def test_retailers_products_not_found(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="product/{}".format(self.api_key)),
                               '',
                               status=404)

        no_valid_id = self.client._connection.api_key
        product = None
        try:
            product = self.client.products.get(no_valid_id)
        except Exception as e:
            self.assertIsInstance(e, ResourceNotFoundError)
        self.assertIsNone(product)

        try:
            product = self.client.products.get('no-valid')
            self.assertEqual(True, False)
        except ValueError as e:
            self.assertIsInstance(e, ValueError)
        except TypeError as e:
            self.assertIsInstance(e, TypeError)
        except Exception as e:
            self.assertEqual(True, False)

    @httpretty.activate
    def test_retailers_products_pictures(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="pictures"),
                               '''
                               {
                                   "meta": {
                                       "total": 1,
                                       "total_pages": 1,
                                       "page": 1,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "pictures": [
                                               {
                                                   "version": "1",
                                                   "picture_id": "55c9cf141d5ca71dd2a0f667",
                                                   "original": {
                                                       "url_to_version": "https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg",
                                                       "url_to_latest": "https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg"
                                                   },
                                                   "thumbs": {
                                                       "300x300": {
                                                           "url_to_version": "https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=1&w=300&s=GZhTSGi_pfthZcYUM6H5Xw_D1sc",
                                                           "url_to_latest": "https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=latest&w=300&s=rUbilbK5SQVqWZwoHc6hGZBACH0"
                                                       }
                                                   }
                                               }
                                           ],
                                           "product_id": "55c9cf151d5ca71dd2a0f66d"
                                       }
                                   ]
                               }
                               ''')
        # Get product pictures list
        product_list = ["55c9cf151d5ca71dd2a0f66d"]
        sizes = ["300x300"]
        products = self.client.products.pictures(product_list, sizes=sizes)
        self.assertEqual(len(products), 1)

        for product in products:
            self.assertIn(product.product_id, product_list)
            self.assertIsInstance(product, ProductPictureList)
            self.assertIsInstance(product.pictures, list)

            pictures = product.pictures
            self.assertEqual(len(pictures), 1)

            picture = product.pictures[0]
            self.assertIsInstance(picture, ProductPicture)
            self.assertEqual('55c9cf141d5ca71dd2a0f667', picture.picture_id)
            self.assertEqual('1', picture.version)

            # Original
            self.assertIsInstance(picture.original, Picture)
            self.assertEqual(picture.original.url_to_latest, 'https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg')
            self.assertEqual(picture.original.url_to_version, 'https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg')

            # Thumbnails
            self.assertIsInstance(picture.thumbs, dict)
            self.assertIn('300x300', picture.thumbs)
            self.assertIsInstance(picture.thumbs['300x300'], Picture)
            self.assertEqual(picture.thumbs['300x300'].url_to_latest, 'https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=latest&w=300&s=rUbilbK5SQVqWZwoHc6hGZBACH0')
            self.assertEqual(picture.thumbs['300x300'].url_to_version, 'https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=1&w=300&s=GZhTSGi_pfthZcYUM6H5Xw_D1sc')

    @httpretty.activate
    def test_retailers_products_pictures_pagination(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="pictures"),
                               '''
                               {
                                   "meta": {
                                       "total": 20,
                                       "total_pages": 4,
                                       "page": 4,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "pictures": [
                                               {
                                                   "version": "1",
                                                   "picture_id": "55c9cf141d5ca71dd2a0f667",
                                                   "original": {
                                                       "url_to_version": "https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg",
                                                       "url_to_latest": "https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg"
                                                   },
                                                   "thumbs": {
                                                       "300x300": {
                                                           "url_to_version": "https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=1&w=300&s=GZhTSGi_pfthZcYUM6H5Xw_D1sc",
                                                           "url_to_latest": "https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=latest&w=300&s=rUbilbK5SQVqWZwoHc6hGZBACH0"
                                                       }
                                                   }
                                               }
                                           ],
                                           "product_id": "55c9cf151d5ca71dd2a0f66d"
                                       }
                                   ]
                               }
                               ''')
        # Get product pictures list
        product_list = ["55c9cf151d5ca71dd2a0f66d"]
        sizes = ["300x300"]
        products = self.client.products.pictures(product_list, sizes=sizes, page=4, page_length=5)
        self.assertEqual(len(products), 1)

        for product in products:
            self.assertIn(product.product_id, product_list)
            self.assertIsInstance(product, ProductPictureList)
            self.assertIsInstance(product.pictures, list)

            pictures = product.pictures
            self.assertEqual(len(pictures), 1)

            picture = product.pictures[0]
            self.assertIsInstance(picture, ProductPicture)
            self.assertEqual('55c9cf141d5ca71dd2a0f667', picture.picture_id)
            self.assertEqual('1', picture.version)

            # Original
            self.assertIsInstance(picture.original, Picture)
            self.assertEqual(picture.original.url_to_latest,
                             'https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg')
            self.assertEqual(picture.original.url_to_version,
                             'https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg')

            # Thumbnails
            self.assertIsInstance(picture.thumbs, dict)
            self.assertIn('300x300', picture.thumbs)
            self.assertIsInstance(picture.thumbs['300x300'], Picture)
            self.assertEqual(picture.thumbs['300x300'].url_to_latest,
                             'https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=latest&w=300&s=rUbilbK5SQVqWZwoHc6hGZBACH0')
            self.assertEqual(picture.thumbs['300x300'].url_to_version,
                             'https://test.plytix.com/pictures/v1/thumbs/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg?api=v1&h=300&id=55c9cf141d5ca71dd2a0f667&v=1&w=300&s=GZhTSGi_pfthZcYUM6H5Xw_D1sc')

    @httpretty.activate
    def test_retailers_products_pictures(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="pictures"),
                               '''
                               {
                                   "meta": {
                                       "total": 1,
                                       "total_pages": 1,
                                       "page": 1,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "pictures": [
                                               {
                                                   "version": "1",
                                                   "picture_id": "55c9cf141d5ca71dd2a0f667",
                                                   "original": {
                                                       "url_to_version": "https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg",
                                                       "url_to_latest": "https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg"
                                                   },
                                                   "thumbs": null
                                               }
                                           ],
                                           "product_id": "55c9cf151d5ca71dd2a0f66d"
                                       }
                                   ]
                               }
                               ''')
        # Get product pictures list
        product_list = ["55c9cf151d5ca71dd2a0f66d"]
        products = self.client.products.pictures(product_list)
        self.assertEqual(len(products), 1)

        for product in products:
            self.assertIn(product.product_id, product_list)
            self.assertIsInstance(product, ProductPictureList)
            self.assertIsInstance(product.pictures, list)

            pictures = product.pictures
            self.assertEqual(len(pictures), 1)

            picture = product.pictures[0]
            self.assertIsInstance(picture, ProductPicture)
            self.assertEqual('55c9cf141d5ca71dd2a0f667', picture.picture_id)
            self.assertEqual('1', picture.version)

            # Original
            self.assertIsInstance(picture.original, Picture)
            self.assertEqual(picture.original.url_to_latest,
                             'https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/latest/Adidas_Decade_High_Top_0.jpg')
            self.assertEqual(picture.original.url_to_version,
                             'https://test.plytix.com/pictures/v1/src/product/a2/3d/4b/56/55c9cf151d5ca71dd2a0f66d/v1/Adidas_Decade_High_Top_0.jpg')

            # Thumbnails
            self.assertIsNone(picture.thumbs)


class TestRetailersBank(RetailersTestCase):

    @httpretty.activate
    def test_retailers_bank_no_input(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 4,
                                       "total_pages": 2,
                                       "page": 2,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand_id": "555f12c21d5ca72ddedd5968",
                                           "brand_name": "Foo Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       },
                                       {
                                           "ean": "PROD-00004",
                                           "gtin": "PROD-00004",
                                           "jan": "PROD-00004",
                                           "sku": "PROD-00004",
                                           "upc": "PROD-00004",
                                           "brand_id": "555efda31d5ca71fe489e798",
                                           "brand_name": "Bar Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "name": "Brand product 4",
                                           "folder": "555f03891d5ca7272be112f6",
                                           "id": "555f03891d5ca7272be112f8",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03891d5ca7272be112f8"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        # Create at root level
        products = self.client.bank.search()
        self.assertEqual(len(products), 2)

    @httpretty.activate
    def test_retailers_bank_name(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 1,
                                       "total_pages": 1,
                                       "page": 1,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand_id": "555f12c21d5ca72ddedd5968",
                                           "brand_name": "Foo Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        # Create at root level
        products = self.client.bank.search(name='Brand product 3')
        self.assertEqual(len(products), 1)

        product = products[0]
        self.assertEqual(product.name, 'Brand product 3')
        self.assertEqual(product.id, '555f03881d5ca7272be112f5')
        self.assertEqual(product.brand_id, "555f12c21d5ca72ddedd5968")
        self.assertEqual(product.brand_name, "Foo Brand")
        self.assertEqual(product.sku, "PROD-00003")
        self.assertEqual(product.thumb, "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc")
        self.assertEqual(product.folder, "555f13001d5ca72ddedd5969")


    @httpretty.activate
    def test_retailers_bank_sku_list(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 4,
                                       "total_pages": 2,
                                       "page": 2,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand_id": "555f12c21d5ca72ddedd5968",
                                           "brand_name": "Foo Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       },
                                       {
                                           "ean": "PROD-00004",
                                           "gtin": "PROD-00004",
                                           "jan": "PROD-00004",
                                           "sku": "PROD-00004",
                                           "upc": "PROD-00004",
                                           "brand_id": "555efda31d5ca71fe489e798",
                                           "brand_name": "Bar Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "name": "Brand product 4",
                                           "folder": "555f03891d5ca7272be112f6",
                                           "id": "555f03891d5ca7272be112f8",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03891d5ca7272be112f8"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        # Create at root level
        products = self.client.bank.search(sku_list=['PROD-00003', 'PROD-00004'])
        self.assertEqual(len(products), 2)

        product_0 = products[0]
        product_1 = products[1]
        self.assertEqual(product_0.name, 'Brand product 3')
        self.assertEqual(product_0.id, '555f03881d5ca7272be112f5')
        self.assertEqual(product_0.brand_id, "555f12c21d5ca72ddedd5968")
        self.assertEqual(product_1.name, 'Brand product 4')
        self.assertEqual(product_1.id, '555f03891d5ca7272be112f8')
        self.assertEqual(product_1.brand_id, "555efda31d5ca71fe489e798")


    @httpretty.activate
    def test_retailers_bank_sku(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 4,
                                       "total_pages": 2,
                                       "page": 2,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": null,
                                           "jan": null,
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand_id": "555f12c21d5ca72ddedd5968",
                                           "brand_name": "Foo Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       },
                                       {
                                           "ean": null,
                                           "gtin": null,
                                           "jan": null,
                                           "sku": "PROD-00004",
                                           "upc": null,
                                           "brand_id": "555efda31d5ca71fe489e798",
                                           "brand_name": "Bar Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "name": "Brand product 4",
                                           "folder": "555f03891d5ca7272be112f6",
                                           "id": "555f03891d5ca7272be112f8",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03891d5ca7272be112f8"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        # Create at root level
        products = self.client.bank.search(sku='PROD-0000')
        self.assertEqual(len(products), 2)

        product_0 = products[0]
        product_1 = products[1]
        self.assertEqual(product_0.name, 'Brand product 3')
        self.assertEqual(product_0.id, '555f03881d5ca7272be112f5')
        self.assertEqual(product_0.brand_id, "555f12c21d5ca72ddedd5968")
        self.assertEqual(product_1.name, 'Brand product 4')
        self.assertEqual(product_1.id, '555f03891d5ca7272be112f8')
        self.assertEqual(product_1.brand_id, "555efda31d5ca71fe489e798")


    @httpretty.activate
    def test_retailers_bank_identifier_list(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 4,
                                       "total_pages": 2,
                                       "page": 2,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "EAN-00003",
                                           "gtin": null,
                                           "jan": null,
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand_id": "555f12c21d5ca72ddedd5968",
                                           "brand_name": "Foo Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       },
                                       {
                                           "ean": null,
                                           "gtin": null,
                                           "jan": null,
                                           "sku": "PROD-00004",
                                           "upc": null,
                                           "brand_id": "555efda31d5ca71fe489e798",
                                           "brand_name": "Bar Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "name": "Brand product 4",
                                           "folder": "555f03891d5ca7272be112f6",
                                           "id": "555f03891d5ca7272be112f8",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03891d5ca7272be112f8"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        # Create at root level
        products = self.client.bank.search(identifier_list=['PROD-00004', 'EAN-00003'])
        self.assertEqual(len(products), 2)

        product_0 = products[0]
        product_1 = products[1]
        self.assertEqual(product_0.name, 'Brand product 3')
        self.assertEqual(product_0.id, '555f03881d5ca7272be112f5')
        self.assertEqual(product_0.brand_id, "555f12c21d5ca72ddedd5968")
        self.assertEqual(product_0.ean, "EAN-00003")
        self.assertEqual(product_1.name, 'Brand product 4')
        self.assertEqual(product_1.id, '555f03891d5ca7272be112f8')
        self.assertEqual(product_1.brand_id, "555efda31d5ca71fe489e798")
        self.assertEqual(product_1.sku, "PROD-00004")


    @httpretty.activate
    def test_retailers_bank_params(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 1,
                                       "total_pages": 1,
                                       "page": 1,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand_id": "555f12c21d5ca72ddedd5968",
                                           "brand_name": "Foo Brand",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        # Create at root level
        products = self.client.bank.search(name='Brand product 3',
                                           folder_id='555f13001d5ca72ddedd5969',
                                           operator=OPERATOR.OR,
                                           product_id='555f03881d5ca7272be112f5',
                                           brand_id='555f12c21d5ca72ddedd5968')
        self.assertEqual(len(products), 1)

        product = products[0]
        self.assertEqual(product.name, 'Brand product 3')
        self.assertEqual(product.id, '555f03881d5ca7272be112f5')
        self.assertEqual(product.brand_id, "555f12c21d5ca72ddedd5968")
        self.assertEqual(product.brand_name, "Foo Brand")
        self.assertEqual(product.sku, "PROD-00003")
        self.assertEqual(product.thumb, "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc")
        self.assertEqual(product.folder, "555f13001d5ca72ddedd5969")

    @httpretty.activate
    def test_retailers_bank_add_products_list(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="folders"),
                               '''
                               {
                                   "folder": {
                                       "folders": [
                                           {
                                               "items": 0,
                                               "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f12c21d5ca72ddedd5968",
                                               "id": "555f12c21d5ca72ddedd5968",
                                               "name": "Baz"
                                           }
                                       ],
                                       "name": "Root",
                                       "parent": null,
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders",
                                       "products": [ ],
                                       "id": null
                                   },
                                   "meta": {
                                       "next_page": null,
                                       "success": true,
                                       "previous_page": null,
                                       "total_pages": 1,
                                       "total": 1,
                                       "page": 1
                                   }
                               }
                               ''',
                               status=200)

        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank"),
                               '''
                               {
                                   "meta": {
                                       "total": 4,
                                       "total_pages": 2,
                                       "page": 2,
                                       "success": true
                                   },
                                   "products": [
                                       {
                                           "ean": "PROD-00003",
                                           "gtin": "PROD-00003",
                                           "jan": "PROD-00003",
                                           "sku": "PROD-00003",
                                           "upc": "PROD-00003",
                                           "brand": "555f12c21d5ca72ddedd5968",
                                           "thumb": "http://products.plytix.com/thumbs/product/88/03/5f/55/555f03881d5ca7272be112f5/Brand_product_3_0.jpg?v=VV8DiQ&w=1000&s=k8mDiLxH5dvxEpAoJEFIDB93hsc",
                                           "name": "Brand product 3",
                                           "folder": "555f13001d5ca72ddedd5969",
                                           "id": "555f03881d5ca7272be112f5",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03881d5ca7272be112f5"
                                       },
                                       {
                                           "ean": "PROD-00004",
                                           "gtin": "PROD-00004",
                                           "jan": "PROD-00004",
                                           "sku": "PROD-00004",
                                           "upc": "PROD-00004",
                                           "brand": "555efda31d5ca71fe489e798",
                                           "thumb": "http://products.plytix.com/thumbs/product/89/03/5f/55/555f03891d5ca7272be112f8/Brand_product_4_0.jpg?v=VV8DiQ&w=1000&s=7O58F2n7krNgoqVN7dRRSp1xwVY",
                                           "name": "Brand product 4",
                                           "folder": "555f03891d5ca7272be112f6",
                                           "id": "555f03891d5ca7272be112f8",
                                           "uri": "https://analytics.plytix.com/api/retailers/v0.1/products/brand/product/555f03891d5ca7272be112f8"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="bank/add"),
                               '''
                               {
                                   "meta": {
                                       "success": true
                                   },
                                   "products_added": [
                                       {
                                           "bank_id": "555f03891d5ca7272be112f8",
                                           "product_id": "55e6d199ed40470efa8a2ede"
                                       }
                                   ]
                               }
                               ''',
                               status=200)

        products = self.client.bank.search()
        products_ids = [p.id for p in products]

        root_folder = self.client.folders.get()
        sub_folder = root_folder.folders[0]

        products_added = self.client.bank.add_to(sub_folder, products_list=products_ids)

        self.assertIsNotNone(products_added)
        self.assertIsInstance(products_added, list)
        self.assertEqual(len(products_added), 1)

        bank_id = products_added[0][RESPONSE_PRODUCT_BANK_ID]
        product_id = products_added[0][RESPONSE_PRODUCT_ID]
        self.assertEqual(bank_id, '555f03891d5ca7272be112f8')
        self.assertEqual(product_id, '55e6d199ed40470efa8a2ede')

    def test_retailers_bank_add_to_params_wrong(self):
        try:
            self.client.bank.add_to({'name': 'Folder'}, folders_list=['555f03891d5ca7272be112f6'])
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, TypeError)

        try:
            folder = Folder('Folder', id='555f03891d5ca7272be112f6')
            self.client.bank.add_to(folder)
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        try:
            folder = Folder('Folder', id='555f03891d5ca7272be112f6')
            self.client.bank.add_to(folder, folders_list='folder-id')
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        try:
            folder = Folder('Folder', id='555f03891d5ca7272be112f6')
            self.client.bank.add_to(folder, products_list='product-id')
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ValueError)


if __name__ == '__main__':
    unittest.main()

