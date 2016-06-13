import unittest
from os.path import isfile, sep
from os import getcwd, remove
from ndb_adapter.ndb_download import DownloadHelper, DownloadType


class DownloadTests(unittest.TestCase):
    def test_download(self):
        pdb_id = "5dg7"
        file = DownloadHelper.download(pdb_id)
        self.assertIsNotNone(file)

        with self.assertRaises(AttributeError):
            DownloadHelper.download("")

        path = getcwd() + sep + "pdb" + pdb_id + ".ent"
        DownloadHelper.download(pdb_id, save=True)
        self.assertTrue(isfile(path))
        remove(path)

        for download_type in filter(lambda w: w is not DownloadType.CifStructureFactors, DownloadType):
                file = DownloadHelper.download("5j0m", download_type)
                self.assertIsNotNone(file)

        file = DownloadHelper.download("5DC3", DownloadType.CifStructureFactors)
        self.assertIsNotNone(file)

    def test_download_file(self):
        url = "http://ndbserver.rutgers.edu/files/ftp/NDB/coordinates/na-chiral-correct/pdb5dg7.ent.gz"
        file = DownloadHelper.download_file(url)
        self.assertIsNotNone(file)

        with self.assertRaises(FileNotFoundError):
            url = "http://ndbserver.rutgers.edu/files/ftp/NDB/coordinates/na-chiral-correct/NotExistingOne.ent.gz"
            DownloadHelper.download_file(url)

if __name__ == '__main__':
    unittest.main()
