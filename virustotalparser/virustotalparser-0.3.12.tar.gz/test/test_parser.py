from unittest import TestCase

from htmlparser.parser import Tag, Parser, Content


class TestParser(TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_short_div(self):
        data = '''
            <div id="cookies-disabled-alert" class="alert center hide"
            style="margin: 55px auto 0; width: 600px;">
            '''
        expected_element_list = [Tag(tagname="div", attributes={'id': 'cookies-disabled-alert',
                                                                'class': 'alert center hide',
                                                                'style': 'margin: 55px auto 0; width: 600px;'})]
        real_element_list = self.parser.parse(data)
        self.assertEqual(real_element_list, expected_element_list)

    def test_alert(self):
        data = '''
            <haha>
            <script type="text/javascript">
                alert( "</script>" ) ;io;a <div>
            </script>
                '''
        real_element_list = self.parser.parse(data)
        expected_element_list = [Tag('haha'),
                                 Tag('script', attributes={'type': "text/javascript"}),
                                 Content('alert( " </script> " ) ;io;a <div>'),
                                 Tag('script')]
        self.assertEqual(real_element_list, expected_element_list)

    def test_script(self):
        data = '''
            <html>
                <script type="text/javascript">
                    haha <>
                </script>
            </html>
            '''
        real_element_list = self.parser.parse(data)
        expected_element_list = [Tag('html'),
                                 Tag('script', attributes={'type': "text/javascript"}),
                                 Content('haha <>'),
                                 Tag('script'),
                                 Tag('html')]
        self.assertEqual(real_element_list, expected_element_list)

    def test_simple_script(self):
        data = '''
            <script>
                a
            </script>
            '''
        real_element_list = self.parser.parse(data)
        expected_element_list = [Tag(tagname='script'), Content('a'), Tag(tagname='script')]
        self.assertEqual(real_element_list, expected_element_list)

    def test_escape_char(self):
        data = '''
            <script>
                alert ("haha \" </script>") uha
            </script>
            '''
        real_element_list = self.parser.parse(data)
        expected_element_list = [Tag(tagname='script'), Content('alert ("haha " </script> " ) uha'), Tag(tagname='script')]
        self.assertEqual(real_element_list, expected_element_list)