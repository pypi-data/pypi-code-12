import os
import unittest2 as unittest
from slc.zopescript.script import ConsoleScript

site_id = None


class TestScript(unittest.TestCase):
    def test_script(self):
        class MyScript(ConsoleScript):
            def run(self):
                global site_id
                site_id = self.portal.id
        my_script = MyScript()
        my_script(os.environ['ZOPE_CONF'], os.environ['RUN_AS'].split(':')[0])
        global site_id
        self.assertEqual(site_id, 'Plone')
