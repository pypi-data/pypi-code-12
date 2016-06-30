
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import unittest
from lxml import etree
import os.path

from .. import ofx
from . import samples


class TestCsb2Ofx(unittest.TestCase):

    def setUp(self):

        f = samples.sample1()

        self.n_fitid = len(f.accounts) * len(f.accounts[0].transactions)
        self.csb = f
        self.ofx = ofx.convertFromCsb(self.csb)

    def test_unique_fitid(self):
        """
        fitid field has a unique constraint
        """

        xml = etree.fromstring(str(self.ofx).encode("UTF-8"))

        fitid = [node.text for node in xml.xpath("//STMTTRN/FITID")]

        self.assertEqual(len(fitid), len(set(fitid)),
                         "all FITID content must be unique within an OFX file")

    def test_v211_xsd_validation(self):
        """
        XSD
        """

        xsd_path = os.path.join(os.path.dirname(__file__),
                                "schemas",
                                "ofx2.1.1",
                                "OFX2_Protocol.xsd")

        if not os.path.exists(xsd_path):
            raise unittest.SkipTest("OFX 2.1.1 Schema not found")

        xsd = etree.XMLSchema(file=xsd_path)

        document = str(self.ofx)

        document = (document
                    .replace(
                        "<OFX>",
                        '<ofx:OFX xmlns:ofx="http://ofx.net/types/2003/04">')
                    .replace("</OFX>", "</ofx:OFX>"))

        root = etree.fromstring(document.encode("UTF-8"))

        xsd.assertValid(root)
