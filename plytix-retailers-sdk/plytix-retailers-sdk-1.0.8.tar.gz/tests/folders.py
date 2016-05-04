from plytix.retailers import API_URL
from plytix.retailers.exceptions import *
from plytix.retailers.services.folders import Folder
from plytix.retailers.models.product import PRODUCT_OWNERSHIP
from tests import RetailersTestCase

import httpretty


class TestRetailersFolders(RetailersTestCase):
    @httpretty.activate
    def test_retailers_folders_get(self):
        # Root folder
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

        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="folders/555f12c21d5ca72ddedd5968"),
                               '''
                               {
                                   "folder": {
                                       "folders": [
                                           {
                                               "items": 0,
                                               "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f13001d5ca72ddedd5969",
                                               "id": "555f13001d5ca72ddedd5969",
                                               "name": "Baz Subfolder"
                                           }
                                       ],
                                       "name": "Baz",
                                       "parent": null,
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f12c21d5ca72ddedd5968",
                                       "products": [ ],
                                       "id": "555f12c21d5ca72ddedd5968"
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
        # Get root folder
        root = self.client.folders.get()
        self.assertIsInstance(root, Folder)
        self.assertIsNone(root.id)
        self.assertIsNone(root.parent)

        # Test subfolders
        if len(root.folders) > 0:
            sub_folder = root.folders[0]
            self.assertIsNotNone(sub_folder)
            folder = self.client.folders.get('555f12c21d5ca72ddedd5968')
            self.assertEqual(sub_folder.id, folder.id)
            self.assertEqual(sub_folder.name, folder.name)

    @httpretty.activate
    def test_retailers_folders_get_params(self):
        # Root folder
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
                                       "success": true,
                                       "total_pages": 1,
                                       "total": 1,
                                       "page": 1
                                   }
                               }
                               ''',
                               status=200)

        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="folders/555f12c21d5ca72ddedd5968"),
                               '''
                               {
                                   "folder": {
                                       "folders": [
                                           {
                                               "items": 0,
                                               "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f13001d5ca72ddedd5969",
                                               "id": "555f13001d5ca72ddedd5969",
                                               "name": "Baz Subfolder"
                                           }
                                       ],
                                       "name": "Baz",
                                       "parent": null,
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f12c21d5ca72ddedd5968",
                                       "products": [ ],
                                       "id": "555f12c21d5ca72ddedd5968"
                                   },
                                   "meta": {
                                       "success": true,
                                       "total_pages": 3,
                                       "total": 3,
                                       "page": 2
                                   }
                               }
                               ''',
                               status=200)
        # Get root folder
        root = self.client.folders.get(page=2, sort='-name', page_length=1)
        self.assertIsInstance(root, Folder)
        self.assertIsNone(root.id)
        self.assertIsNone(root.parent)

        # Test subfolders
        if len(root.folders) > 0:
            sub_folder = root.folders[0]
            self.assertIsNotNone(sub_folder)
            folder = self.client.folders.get('555f12c21d5ca72ddedd5968')
            self.assertEqual(sub_folder.id, folder.id)
            self.assertEqual(sub_folder.name, folder.name)

    @httpretty.activate
    def test_retailers_folders_get_not_found(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="folders/557152491d5ca710c428dc03"),
                               '''
                               {
                                   "meta": {
                                       "success": false,
                                       "total_pages": 0,
                                       "total": 0,
                                       "page": 1
                                   }
                               }
                               ''',
                               status=404)
        # Get root folder
        root = self.client.folders.get('557152491d5ca710c428dc03')
        self.assertIsNone(root)

    @httpretty.activate
    def test_retailers_folders_create(self):
        # Create at root level
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="folders"),
                               '''
                               {
                                   "folder": {
                                       "folders": [ ],
                                       "name": "Baz",
                                       "parent": null,
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f12c21d5ca72ddedd5968",
                                       "products": [ ],
                                       "id": "555f12c21d5ca72ddedd5968"
                                   },
                                   "meta": {
                                       "success": true,
                                       "created": true
                                   }
                               }
                               ''',
                               status=201)

        new_folder = self.client.folders.create('Baz', None)
        self.assertIsInstance(new_folder, Folder)
        self.assertIsNotNone(new_folder.id)
        self.assertIsNone(new_folder.parent)

        # Create subfolder
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="folders/555f12c21d5ca72ddedd5968"),
                               '''
                               {
                                   "folder": {
                                       "folders": [ ],
                                       "name": "Baz subfolder",
                                       "parent": "555f12c21d5ca72ddedd5968",
                                       "uri": "https://analytics.plytix.com/api/retailers/v0.1/folders/555f12c21d5ca72ddedd5968",
                                       "products": [ ],
                                       "id": "555f13001d5ca72ddedd5969"
                                   },
                                   "meta": {
                                       "success": true,
                                       "created": true
                                   }
                               }
                               ''',
                               status=201)

        second_folder = self.client.folders.create('Baz subfolder', '555f12c21d5ca72ddedd5968')
        self.assertIsInstance(second_folder, Folder)
        self.assertIsNotNone(second_folder.id)
        self.assertEqual(second_folder.name, 'Baz subfolder')
        self.assertEqual(second_folder.parent, new_folder.id)

        # Duplicated folder
        try:
            duplicated_folder = self.client.folders.create('Baz subfolder', '555f12c21d5ca72ddedd5968')
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

if __name__ == '__main__':
    unittest.main()
