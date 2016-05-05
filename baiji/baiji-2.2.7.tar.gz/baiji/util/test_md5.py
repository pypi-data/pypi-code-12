import unittest

class TestMD5(unittest.TestCase):
    def test_md5(self):
        import os
        import struct
        from baiji.util import tempfile
        from baiji.util.md5 import md5_for_file
        f = tempfile.NamedTemporaryFile('wb', delete=False)
        for _ in range(2**16):
            f.write(struct.pack("<I", 42))
        f.close()
        self.assertEqual(md5_for_file(f.name), "9b0cbf6ba5c0ad5606df9b9630a44db6")
        os.remove(f.name)
