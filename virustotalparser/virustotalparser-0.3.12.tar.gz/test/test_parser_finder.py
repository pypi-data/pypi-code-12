from unittest import TestCase

from htmlparser.parser import Parser

from htmlparser.finder import Finder


class TestParserFinder(TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_simple_attributes(self):
        data = '''
            <div class="enum">
              <div class="floated-field-key">MIMEType</div>
              <div class="floated-field-value">application/pdf</div>
              <br style="clear:both;"/>
            </div>
            <div class="enum">
              <div class="floated-field-key">XMPToolkit</div>
              <div class="floated-field-value">XMP toolkit 2.9.1-13, framework 1.6</div>
              <br style="clear:both;"/>
            </div>
            '''
        attributes = ["XMPToolkit", "MIMEType"]
        element_list = self.parser.parse(data)
        finder = Finder(element_list)
        real_attributes_found = finder.find_attributes_from_list(attributes)
        expected_attributes_found = {"MIMEType": "application/pdf", "XMPToolkit": "XMP toolkit 2.9.1-13, framework 1.6"}
        self.assertEqual(real_attributes_found, expected_attributes_found)

    def test_antyviruses(self):
        data = '''
       <tr>
          <td class="ltr">
            Zoner
          </td>
          <td class="ltr text-green">
              <i data-toggle="tooltip" title="File not detected" class="icon-ok-sign" alt="clean"></i>
          </td>
          <td class="ltr">
            20160417
          </td>
       </tr>
       <tr>
          <td class="ltr">
            nProtect
          </td>
          <td class="ltr text-green">
              <i data-toggle="tooltip" title="File not detected" class="icon-ok-sign" alt="clean"></i>
          </td>
          <td class="ltr">
            20160415
          </td>
       </tr>
      '''
        element_list = self.parser.parse(data)
        finder = Finder(element_list)
        real_antyviruses = finder._find_antyviruses_info()
        expected_antyviruses = {'Zoner': 'File not detected', 'nProtect': 'File not detected'}
        self.assertEqual(real_antyviruses, expected_antyviruses)

    def test_first_page_info(self):
        data = '''
            <div class="row">
              <div class="span8 columns">
                <table style="margin-bottom:8px;margin-left:8px;">
                  <tbody>
                    <tr>
                      <td>SHA256:</td>
                      <td>
                        70ed0f6db9c50f9d05f3497386dba768f5efef59b6709c682bbc1951a93c47bf
                      </td>
                    </tr>
                    <tr>
                      <td>File name:</td>
                      <td>zadanie.pdf</td>
                    </tr>
                    <tr>
                      <td>Detection ratio:</td>
                      <td class=" text-green
                                  ">
                        0 / 57
                      </td>
                    </tr>
                    <tr>
                      <td>Analysis date:</td>
                      <td >
                        2016-04-17 09:21:07 UTC ( 5 days, 4 hours ago )
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
                <tr>
                      <td class="ltr">
                        Yandex
                      </td>
                      <td class="ltr text-green">
                          <i data-toggle="tooltip" title="File not detected" class="icon-ok-sign" alt="clean"></i>
                      </td>
                      <td class="ltr">
                        20160416
                      </td>
                  </tr>
                  <tr>
                      <td class="ltr">
                        Zillya
                      </td>
                      <td class="ltr text-green">
                          <i data-toggle="tooltip" title="File not detected" class="icon-ok-sign" alt="clean"></i>
                      </td>
                      <td class="ltr">
                        20160416
                      </td>
                  </tr>
            '''
        element_list = self.parser.parse(data)
        finder = Finder(element_list)
        real_info = finder.find_first_page_attributes()
        expected_info = {'SHA256': '70ed0f6db9c50f9d05f3497386dba768f5efef59b6709c682bbc1951a93c47bf',
                         'Detection ratio': '0 / 57',
                         'File name': 'zadanie.pdf',
                         'Analysis date': '2016-04-17 09:21:07 UTC ( 5 days, 4 hours ago )',
                         'Antyviruses': {'Yandex': 'File not detected', 'Zillya': 'File not detected'}}

        self.assertEqual(real_info, expected_info)
