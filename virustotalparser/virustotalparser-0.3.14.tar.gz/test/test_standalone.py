from unittest import TestCase

from htmlparser import standalone


class TestStandalone(TestCase):
    def test_two_args_some_reds(self):
        args = ["testfiles/vt-some-reds.html", "testfiles/test_one.json"]
        real_element_list = standalone.main(args)
        expected_element_list = {"MIMEType": "application/x-httpd-php", "FileType": "PHP"}
        self.assertEqual(real_element_list, expected_element_list)


    def test_one_arg_some_reds(self):
        args = ["testfiles/vt-some-reds.html", "testfiles/test_two.json"]
        real_element_list = standalone.main(args)
        self.assertEqual(1,1)
