import unittest
from ndb_adapter.html_parser import NDBHtmlParser


class HtmlParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = NDBHtmlParser()

    def test_parse(self):
        self.parser.analyze("<div><h2>Test</h2></div>")
        self.assertIsNotNone(self.parser.get_tree())

    def test_parse_find_one(self):
        self.parser.analyze("<div><h2 id='test'>Test</h2></div>")
        found = self.parser.find_one(params={'id': 'test'})
        self.assertEqual(found.data, 'Test')

        found = self.parser.find_one('h2')
        self.assertEqual(found.data, 'Test')

        found = self.parser.find_one('h2', params={'id': 'test'})
        self.assertEqual(found.data, 'Test')

        self.assertEqual(str(found), "<h2 id=\"test\">Test</h2>")

        found = self.parser.find_one(params={'id': 'notFound'})
        self.assertIsNone(found)

    def test_parse_find_all(self):
        self.parser.analyze("<div><h2 class='test'>Test</h2></div>")

        found = self.parser.find_all()
        self.assertEqual("[<div><h2 class=\"test\">Test</h2></div>, <h2 class=\"test\">Test</h2>]", str(found))

        params = {'class': 'test'}
        found = self.parser.find_all(params=params)
        self.assertEqual("[<h2 class=\"test\">Test</h2>]", str(found))

        self.parser.analyze("<div><h2 class='test'>Test</h2><h1 class='test'>Test2</h1></div>")
        params = {'class': 'test'}
        found = self.parser.find_all(params=params)
        self.assertEqual("[<h2 class=\"test\">Test</h2>, <h1 class=\"test\">Test2</h1>]", str(found))

        self.parser.analyze("")
        params = {'class': 'test'}
        found = self.parser.find_all(params=params)
        self.assertFalse(found)


if __name__ == '__main__':
    unittest.main()
