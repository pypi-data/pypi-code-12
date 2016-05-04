from plytix.retailers import API_URL
from plytix.retailers.exceptions import BadResponseError, BadRequestError, PlytixRetailersAPIError
from plytix.retailers.models.site import Site
from tests import RetailersTestCase

import httpretty


class TestRetailersSites(RetailersTestCase):

    @httpretty.activate
    def test_retailers_sites_list(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="sites"),
                               '''
                               {
                                    "meta": {
                                         "total": 1,
                                         "total_pages": 1,
                                         "page": 1,
                                         "success": true
                                    },
                                    "sites": [
                                        {
                                            "url": "retailershop.com",
                                            "uri": "https://analytics.plytix.com/api/retailers/v0.1/sites/555ef67a1d5ca71fe489e794",
                                            "id": "555ef67a1d5ca71fe489e794",
                                            "name": "Retailer Shop"
                                        }
                                    ]
                               }
                               ''')
        # Get site's list
        sites = self.client.sites.list()
        self.assertGreater(len(sites), 0)
        self.assertEqual(sites.page, 1)
        self.assertEqual(sites.total, 1)
        self.assertEqual(sites.total_pages, 1)
        self.assertEqual(sites.has_more, False)

        site = sites[0]
        self.assertEqual(site.url, 'retailershop.com')
        self.assertEqual(site.id, '555ef67a1d5ca71fe489e794')
        self.assertEqual(site.name, 'Retailer Shop')

    @httpretty.activate
    def test_retailers_sites_list_params(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="sites"),
                               '''
                               {
                                    "meta": {
                                         "total": 2,
                                         "total_pages": 1,
                                         "page": 1,
                                         "success": true
                                    },
                                    "sites": [
                                        {
                                            "url": "retailershop.dk",
                                            "id": "555ef7201d5ca71fe489e795"
                                        },
                                        {
                                            "url": "retailershop.com",
                                            "id": "555ef67a1d5ca71fe489e794"
                                        }
                                    ]
                               }
                               ''')
        # Get site's list
        sites = self.client.sites.list(fields=['url', 'id'], sort='-name')
        self.assertGreater(len(sites), 0)
        for site in sites:
            self.assertIsNone(site.name)
            self.assertIsNotNone(site.url)
            self.assertIsNotNone(site.id)

    @httpretty.activate
    def test_retailers_sites_search(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="sites/search"),
                               '''
                               {
                                    "meta": {
                                         "total": 1,
                                         "total_pages": 1,
                                         "page": 1,
                                         "success": true
                                    },
                                    "sites": [
                                        {
                                            "url": "retailershop.dk",
                                            "uri": "https://analytics.plytix.com/api/retailers/v0.1/sites/555ef7201d5ca71fe489e795",
                                            "id": "555ef7201d5ca71fe489e795",
                                            "name": "Retailer Shop DK"
                                        }
                                    ]
                               }
                               ''')
        # Get site's by name
        sites = self.client.sites.search(name='Retailer Shop DK')
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites.page, 1)
        self.assertEqual(sites.total, 1)
        self.assertEqual(sites.total_pages, 1)
        self.assertEqual(sites.has_more, False)

        # Get site's by protocol
        sites = self.client.sites.search(protocol='https')
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites.page, 1)
        self.assertEqual(sites.total, 1)
        self.assertEqual(sites.total_pages, 1)
        self.assertEqual(sites.has_more, False)

        # Get site's by url
        sites = self.client.sites.search(url='retailershop.dk')
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites.page, 1)
        self.assertEqual(sites.total, 1)
        self.assertEqual(sites.total_pages, 1)
        self.assertEqual(sites.has_more, False)

    @httpretty.activate
    def test_retailers_sites_search_params(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="sites/search"),
                               '''
                               {
                                    "meta": {
                                         "total": 2,
                                         "total_pages": 1,
                                         "page": 1,
                                         "success": true
                                    },
                                    "sites": [
                                        {
                                            "url": "retailershop.dk",
                                            "id": "555ef7201d5ca71fe489e795"
                                        },
                                        {
                                            "url": "retailershop.com",
                                            "id": "555ef67a1d5ca71fe489e794"
                                        }
                                    ]
                               }
                               ''')
        # Get site's list
        sites = self.client.sites.search(name="retailershop", fields=['url', 'id'], sort='-name')
        self.assertGreater(len(sites), 0)
        for site in sites:
            self.assertIsNone(site.name)
            self.assertIsNotNone(site.url)
            self.assertIsNotNone(site.id)

    @httpretty.activate
    def test_retailers_sites_create(self):
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="sites"),
                               '''
                               {
                                   "site": {
                                       "debug": true,
                                       "protocol": "https",
                                       "name": "Retailer Shop",
                                       "url": "retailershop.com",
                                       "timezone": "Europe/Madrid",
                                       "id": "555ef67a1d5ca71fe489e794"
                                   },
                                   "meta": {
                                       "success": true
                                   }
                               }
                               ''')
        # Creates our new site
        site_info = {
            "platform_version": "1.0.0",
            "plaftorm_name": "Wordpress",
            "subplatform_version": "5.3.2",
            "subplatform_name": "Woocommerce",
            "plytix_plugin_version": "0.6.1",
            "sync_pictures": True,
            "use_cdn": True
        }

        new_site = Site(debug=True, name='Retailer Shop', url='retailershop.com', protocol='https',
                        timezone='Europe/Madrid', info=site_info)
        self.assertIsNone(new_site.id)

        # Saves the site in our account
        new_site = self.client.sites.create(new_site)
        self.assertIsNotNone(new_site.id)

    @httpretty.activate
    def test_retailers_sites_create_invalid_site(self):
        # Should not be used
        httpretty.register_uri(httpretty.POST,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="sites"),
                               '''
                               {
                                   "meta": {
                                       "success": false
                                   },
                                   "message": "Invalid protocol",
                                   "status": 400
                               }
                               ''',
                               status=400)

        # Creates our new site
        try:
            new_site = Site(debug=True, name='My new site', url='mynewsite.com', protocol='ftp', timezone='Europe/Madrid')
            self.client.sites.create(new_site)
            self.assertEqual(True, False)
        except Exception as e:
            self.assertIsInstance(e, BadRequestError)

        try:
            self.client.sites.create(['no', 'valid', 'site'])
        except Exception as e:
            self.assertIsInstance(e, TypeError)

    @httpretty.activate
    def test_retailers_sites_update(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/555ef67a1d5ca71fe489e794"),
                               '''
                               {
                                   "site": {
                                       "debug": true,
                                       "protocol": "https",
                                       "name": "Retailer Shop",
                                       "url": "retailershop.com",
                                       "timezone": "Europe/Madrid",
                                       "id": "555ef67a1d5ca71fe489e794"
                                   },
                                   "meta": {
                                       "success": true
                                   }
                               }
                               ''',
                               status=200)

        httpretty.register_uri(httpretty.PUT,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/555ef67a1d5ca71fe489e794"),
                               '''
                               {
                                   "site": {
                                       "debug": false,
                                       "protocol": "https",
                                       "name": "Updated site",
                                       "url": "retailershop.com",
                                       "timezone": "Europe/Madrid",
                                       "id": "555ef67a1d5ca71fe489e794"
                                   },
                                   "meta": {
                                       "success": true
                                   }
                               }
                               ''')

        # Get the site
        site = self.client.sites.get('555ef67a1d5ca71fe489e794')
        url = site.url
        protocol = site.protocol
        timezone = site.timezone

        new_name = 'Updated site'
        self.assertNotEqual(site.name, new_name)

        # Update
        site.name = new_name
        debug = not site.debug
        site.debug = debug
        updated_site = self.client.sites.update(site)
        self.assertEqual(updated_site.name, new_name)
        self.assertEqual(updated_site.debug, debug)
        self.assertEqual(updated_site.url, url)
        self.assertEqual(updated_site.protocol, protocol)
        self.assertEqual(updated_site.timezone, timezone)

    @httpretty.activate
    def test_retailers_sites_update_invalid_site(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/555ef67a1d5ca71fe489e794"),
                               '''
                               {
                                   "site": {
                                       "debug": true,
                                       "protocol": "https",
                                       "name": "Retailer Shop",
                                       "url": "retailershop.com",
                                       "timezone": "Europe/Madrid",
                                       "id": "555ef67a1d5ca71fe489e794"
                                   },
                                   "meta": {
                                       "success": true
                                   }
                               }
                               ''',
                               status=200)

        # Should not be used
        httpretty.register_uri(httpretty.PUT,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/555ef67a1d5ca71fe489e794"),
                               '',
                               status=400)
        # Get the site
        site = self.client.sites.get('555ef67a1d5ca71fe489e794')

        # Invalid protocol
        protocol = 'ftp'
        self.assertNotEqual(site.protocol, protocol)

        # Update
        site.protocol = protocol
        try:
            site = self.client.sites.update(site)
        except BaseException as e:
            self.assertIsInstance(e, BadRequestError)

        # Invalid timezone
        timezone = 'Europe/Malaga'
        self.assertNotEqual(site.timezone, timezone)

        # Update
        site.timezone = timezone
        try:
            site = self.client.sites.update(site)
        except BaseException as e:
            self.assertIsInstance(e, BadRequestError)

        # Invalid ID
        site.id = 'no-valid-id'
        try:
            site = self.client.sites.update(site)
        except BaseException as e:
            self.assertIsInstance(e, ValueError)

        try:
            self.client.sites.update(['no', 'valid', 'site'])
        except Exception as e:
            self.assertIsInstance(e, TypeError)

    @httpretty.activate
    def test_retailers_sites_get(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/555ef67a1d5ca71fe489e794"),
                               '''
                               {
                                   "site": {
                                       "debug": true,
                                       "protocol": "https",
                                       "name": "Retailer Shop",
                                       "url": "retailershop.com",
                                       "id": "555ef67a1d5ca71fe489e794"
                                   },
                                   "meta": {
                                       "success": true
                                   }
                               }
                               ''',
                               status=200)

        # Get the site
        site = self.client.sites.get('555ef67a1d5ca71fe489e794', fields=['debug', 'picture_sizes', 'protocol', 'name', 'url', 'id'])

        self.assertIsNotNone(site.debug)
        self.assertIsNotNone(site.protocol)
        self.assertIsNotNone(site.name)
        self.assertIsNotNone(site.url)
        self.assertIsNone(site.timezone)
        self.assertIsNotNone(site.id)

        self.assertEqual(site.debug, True)
        self.assertEqual(site.protocol, 'https')
        self.assertEqual(site.name, 'Retailer Shop')
        self.assertEqual(site.url, 'retailershop.com')
        self.assertEqual(site.id, '555ef67a1d5ca71fe489e794')

    @httpretty.activate
    def test_retailers_sites_get_not_found(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/{}".format(self.api_key)),
                               '''
                               {
                                   "meta": {
                                       "success": false
                                   },
                                   "message": "Resource not found."
                               }
                               ''',
                               status=404)

        # Get the site
        site_id = self.api_key
        site = self.client.sites.get(site_id)
        self.assertIsNone(site)

    @httpretty.activate
    def test_retailers_sites_get_bad_request(self):
        httpretty.register_uri(httpretty.GET,
                               "{api}/{endpoint}".format(api=API_URL, endpoint="site/invalid_id"),
                               '''
                               {
                                   "meta": {
                                       "success": false
                                   },
                                   "message": "Bad input parameter."
                               }
                               ''',
                               status=400)
        try:
            # Get the site
            site_id = 'invalid_id'
            site = self.client.sites.get(site_id)
            self.assertIsNone(site)
            self.assertEqual(True, False)
        except TypeError as e:
            self.assertIsInstance(e, TypeError)
        except ValueError as e:
            self.assertIsInstance(e, ValueError)
        except Exception as e:
            self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()