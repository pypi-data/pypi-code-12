#! /usr/bin/env python

import atomictempfile, os, tempfile, unittest

class TestAtomicTempFile (unittest.TestCase):

  def setUp (self):
    handle, fname = tempfile.mkstemp ()
    os.fdopen (handle, "w").write ("old data")
    self.fname = fname

  def tearDown (self):
    os.remove (self.fname)

  def test_overwrite (self):
    with atomictempfile.AtomicTempFile (self.fname) as f:
      f.write ("new data")
    self.assertEqual (file (self.fname).read (), "new data")

  def test_competingr_write (self):
    with atomictempfile.AtomicTempFile (self.fname) as f:
      open (self.fname, "w").write ("different stuff")
      f.write ("new data")
    self.assertEqual (file (self.fname).read (), "new data")

if __name__ == '__main__':
  unittest.main()
