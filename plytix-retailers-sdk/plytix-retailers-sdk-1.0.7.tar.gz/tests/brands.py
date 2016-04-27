from plytix.retailers import API_URL
from plytix.retailers.models.brand import Brand
from tests import RetailersTestCase

import httpretty


class TestRetailersBrands(RetailersTestCase):

    @httpretty.activate
    def test_retailers_brands_search(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="brands/search"),
                               '''
                               {
                                   "brands": [
                                        {
                                         "website": "http://retailer.com",
                                         "id": "555ef5401d5ca71fe489e793",
                                         "name": "Retailer account"
                                       },
                                       {
                                         "website": "http://brand.com",
                                         "id": "555efda31d5ca71fe489e798",
                                         "name": "Brand Account"
                                       }
                                   ],
                                   "meta": {
                                       "total": 2,
                                       "total_pages": 1,
                                       "page": 1,
                                       "success": true
                                   }
                               }
                               ''',
                               status=200)

        brands = self.client.brands.search('account', fields='website,id,name', sort='-name')
        self.assertEqual(len(brands), 2)

        brand = brands[1]
        self.assertIsInstance(brand, Brand)
        self.assertEqual(brand.name, 'Brand Account')
        self.assertEqual(brand.picture, None)
        self.assertEqual(brand.id, '555efda31d5ca71fe489e798')
        self.assertEqual(brand.website, 'http://brand.com')

    @httpretty.activate
    def test_retailers_brands_search_no_results(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="brands/search"),
                               '''
                               {
                                   "brands": [],
                                   "meta": {
                                       "total": 0,
                                       "total_pages": 1,
                                       "page": 1,
                                       "success": true
                                   }
                               }
                               ''',
                               status=200)

        brands = self.client.brands.search('account', page_length=2, fields='website,id,name', sort='-name')
        self.assertEqual(len(brands), 0)

if __name__ == '__main__':
    unittest.main()