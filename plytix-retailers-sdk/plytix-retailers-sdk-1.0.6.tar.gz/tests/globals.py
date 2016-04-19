from plytix.retailers import API_URL
from plytix.retailers.connection import PlytixRetailersConnection
from plytix.retailers.exceptions import *
from plytix.retailers.fields import *
from plytix.retailers.models.brand import Brand
from plytix.retailers.models.folder import Folder
from plytix.retailers.models.product import Product
from plytix.retailers.models.site import Site
from plytix.retailers.services import BaseEndpoint

from tests import RetailersTestCase

import httpretty
import unittest


class TestRetailersGlobals(RetailersTestCase):

    def test_retailers_globals_to_dict(self):
        brand = {
            'name': 'brand',
            'website': 'brand.com',
            'picture': 'pic',
        }
        self.assertDictEqual(brand, Brand.parse(brand).to_dict())

        folder = {
            'name': 'folder',
            MODEL_FOLDERS: [{
                'name': 'Sub {}'.format(i),
                'id': 'sub {}'.format(i),
            } for i in range(2)],
            MODEL_PRODUCTS: [{
                'id': str(i),
                'name': 'Prod {}'.format(i),
                'ean': 'PROD-{}'.format(i),
                'gtin': 'PROD-{}'.format(i),
                'jan': 'PROD-{}'.format(i),
                'sku': 'PROD-{}'.format(i),
                'upc': 'PROD-{}'.format(i),
                'folder': None,
                'thumb': 'thumb',
            } for i in range(4)],
            'parent': None,
        }

        self.assertDictEqual(folder, Folder.parse(folder).to_dict(complete=True))

    @httpretty.activate
    def test_retailers_globals_services(self):
        try:
            BaseEndpoint('connection')
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ClientNotValidError)

        conn = PlytixRetailersConnection(self.api_key, self.api_pwd)
        endpoint = BaseEndpoint(conn)

        response_200 = '{api_url}/{endpoint}'.format(api_url=API_URL, endpoint='response/200')
        response_400 = '{api_url}/{endpoint}'.format(api_url=API_URL, endpoint='response/400')
        response_404 = '{api_url}/{endpoint}'.format(api_url=API_URL, endpoint='response/404')
        response_500 = '{api_url}/{endpoint}'.format(api_url=API_URL, endpoint='response/500')

        # POST
        httpretty.register_uri(httpretty.POST, response_200, '{"name":"folder"}', status=200)
        httpretty.register_uri(httpretty.POST, response_400, '{"meta": {"success": false},"message": "Bad input parameter."}', status=400)
        httpretty.register_uri(httpretty.POST, response_404, '{"meta": {"success": false},"message": "Resource not found."}', status=404)
        httpretty.register_uri(httpretty.POST, response_500, '', status=500)

        # GET
        httpretty.register_uri(httpretty.GET, response_200, '', status=200)
        httpretty.register_uri(httpretty.GET, response_400, '{"meta": {"success": false},"message": "Bad input parameter."}', status=400)
        httpretty.register_uri(httpretty.GET, response_404, '{"meta": {"success": false},"message": "Resource not found."}', status=404)
        httpretty.register_uri(httpretty.GET, response_500, '', status=500)

        # PUT
        httpretty.register_uri(httpretty.PUT, response_200, '', status=200)
        httpretty.register_uri(httpretty.PUT, response_400, '{"meta": {"success": false},"message": "Bad input parameter."}', status=400)
        httpretty.register_uri(httpretty.PUT, response_404, '{"meta": {"success": false},"message": "Resource not found."}', status=404)
        httpretty.register_uri(httpretty.PUT, response_500, '', status=500)

        # _create
        folder = Folder('folder')

        try:
            endpoint._create()
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        # 200
        response = endpoint._create(folder, endpoint='response/200', fields=['name'])
        self.assertEqual(response.status_code, 200)

        # 400
        try:
            response = endpoint._create(data='{"name":"folder"}', endpoint='response/400')
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

        # 404
        try:
            response = endpoint._create(data='{"name":"folder"}', endpoint='response/404')
            self.assertEqual(response.status_code, 404)
        except Exception as e:
            self.assertIsInstance(e, ResourceNotFoundError)

        # 500
        try:
            response = endpoint._create(folder, endpoint='response/500')
            self.assertEqual(response.status_code, 500)
        except Exception as e:
            self.assertIsInstance(e, BadResponseError)

        # _get
        try:
            endpoint._get('no-valid-id')
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        object_id = '555f12c21d5ca72ddedd5968'

        # 200
        response = endpoint._get(object_id, endpoint='response/200', fields='name')
        self.assertEqual(response.status_code, 200)

        # 400
        try:
            response = endpoint._get(object_id, endpoint='response/400')
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

        # 404
        try:
            response = endpoint._get(object_id, endpoint='response/404')
            raise AssertionError('ReseourceNotFoundError not raised.')
        except Exception as e:
            self.assertIsInstance(e, ResourceNotFoundError)

        # 500
        try:
            response = endpoint._get(object_id, endpoint='response/500')
            self.assertEqual(response.status_code, 500)
        except Exception as e:
            self.assertIsInstance(e, BadResponseError)


        # _list

        # 200
        response = endpoint._list(endpoint='response/200')
        self.assertEqual(response.status_code, 200)

        # 400
        try:
            response = endpoint._list(endpoint='response/400')
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

        # 404
        try:
            response = endpoint._list(endpoint='response/404')
            raise AssertionError('ReseourceNotFoundError not raised.')
        except Exception as e:
            self.assertIsInstance(e, ResourceNotFoundError)
        # 500
        try:
            response = endpoint._list(endpoint='response/500')
            self.assertEqual(response.status_code, 500)
        except Exception as e:
            self.assertIsInstance(e, BadResponseError)

        # _search
        # 200
        response = endpoint._search(endpoint='response/200', fields='name')
        self.assertEqual(response.status_code, 200)

        # 400
        try:
            response = endpoint._search(endpoint='response/400', fields='name')
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

        # 404
        try:
            response = endpoint._search(endpoint='response/404', fields=['name'])
            raise AssertionError('ReseourceNotFoundError not raised.')
        except Exception as e:
            self.assertIsInstance(e, ResourceNotFoundError)

        # 500
        try:
            response = endpoint._search(endpoint='response/500', fields=['name'])
            self.assertEqual(response.status_code, 500)
        except Exception as e:
            self.assertIsInstance(e, BadResponseError)

        # _update
        # 200
        folder.id = object_id
        response = endpoint._update(folder, endpoint='response/200', fields='name')
        self.assertEqual(response.status_code, 200)

        # 400
        try:
            response = endpoint._update(folder, endpoint='response/400', fields='name')
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

        # 404
        try:
            response = endpoint._update(folder, endpoint='response/404', fields=['name'])
            raise AssertionError('ReseourceNotFoundError not raised.')
        except Exception as e:
            self.assertIsInstance(e, ResourceNotFoundError)

        # 500
        try:
            response = endpoint._update(folder, endpoint='response/500', fields=['name'])
            self.assertEqual(response.status_code, 500)
        except Exception as e:
            self.assertIsInstance(e, BadResponseError)

        try:
            folder.id = 'no-valid-id'
            endpoint._update(folder)
            raise AssertionError
        except Exception as e:
            self.assertIsInstance(e, ValueError)

if __name__ == '__main__':
    unittest.main()
