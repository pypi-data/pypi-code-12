from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import unittest

import os
import sys
sys.path.append('../')

import datetime

import simplejson
from glob import glob

from whois.parser import WhoisEntry, cast_date

class TestParser(unittest.TestCase):
    def test_com_expiration(self):
        data = """
        Status: ok
        Updated Date: 14-apr-2008
        Creation Date: 14-apr-2008
        Expiration Date: 14-apr-2009
        
        >>> Last update of whois database: Sun, 31 Aug 2008 00:18:23 UTC <<<
        """
        w = WhoisEntry.load('urlowl.com', data)
        expires = w.expiration_date.strftime('%Y-%m-%d')
        self.assertEqual(expires, '2009-04-14')

    def test_cast_date(self):
        dates = ['14-apr-2008', '2008-04-14']
        for d in dates:
            r = cast_date(d).strftime('%Y-%m-%d')
            self.assertEqual(r, '2008-04-14')

    def test_com_allsamples(self):
        """
        Iterate over all of the sample/whois/*.com files, read the data,
        parse it, and compare to the expected values in sample/expected/.
        Only keys defined in keys_to_test will be tested.
        
        To generate fresh expected value dumps, see NOTE below.
        """
        keys_to_test = ['domain_name', 'expiration_date', 'updated_date',
                        'creation_date', 'status']
        fail = 0
        total = 0
        for path in glob('test/samples/whois/*.com'):
            # Parse whois data
            domain = os.path.basename(path)
            with open(path) as whois_fp:
                data = whois_fp.read()
            
            w = WhoisEntry.load(domain, data)
            results = {key: w.get(key) for key in keys_to_test}

            # NOTE: Toggle condition below to write expected results from the
            # parse results This will overwrite the existing expected results.
            # Only do this if you've manually confirmed that the parser is
            # generating correct values at its current state.
            if False:
                def date2str4json(obj):
                    if isinstance(obj, datetime.datetime):
                        return str(obj)
                    raise TypeError(
                            '{} is not JSON serializable'.format(repr(obj)))
                outfile_name = os.path.join('test/samples/expected/', domain)
                with open(outfile_name, 'w') as outfil:
                    expected_results = simplejson.dump(results, outfil,
                                                       default=date2str4json)
                continue

            # Load expected result
            with open(os.path.join('test/samples/expected/', domain)) as infil:
                expected_results = simplejson.load(infil)
            
            # Compare each key
            for key in results:
                total += 1
                result = results.get(key)
                if isinstance(result, datetime.datetime):
                    result = str(result)
                expected = expected_results.get(key)
                if expected != result:
                    print("%s \t(%s):\t %s != %s" % (domain, key, result, expected))
                    fail += 1
            
        if fail:
            self.fail("%d/%d sample whois attributes were not parsed properly!"
                      % (fail, total))


if __name__ == '__main__':
    unittest.main()
