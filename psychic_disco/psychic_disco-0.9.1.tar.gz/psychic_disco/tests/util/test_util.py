import unittest
from psychic_disco import util
import os
import shutil


class TestUtil(unittest.TestCase):
    def test_shell(self):
        util.shell(["touch", "poop.txt"])
        self.assertTrue(os.path.exists("poop.txt"))
        os.remove("poop.txt")

    def test_cp(self):
        with open("poop_src.txt", "w") as f:
            f.write("poop")
        util.cp("poop_src.txt", "poop_dest.txt")
        self.assertTrue(os.path.exists("poop_dest.txt"))
        os.remove("poop_src.txt")
        os.remove("poop_dest.txt")

    def test_zip(self):
        shutil.rmtree("poop", True)
        os.mkdir("poop")
        with open("poop/poop_1.txt", "w") as f:
            f.write("poop1")
        with open("poop/poop_2.txt", "w") as f:
            f.write("poop2")
        util.zip("poop", "poop.zip")
        self.assertTrue(os.path.exists("poop.zip"))
        shutil.rmtree("poop", True)
        os.remove("poop.zip")

    def test_py_files_in_directory(self):
        shutil.rmtree("poop", True)
        os.mkdir("poop")
        with open("poop/poop_1.py", "w") as f:
            f.write("poop1")
        with open("poop/poop_2.py", "w") as f:
            f.write("poop2")
        with open("poop/poop_2.txt", "w") as f:
            f.write("poop2")
        py_files = []
        for py_file in util.py_files_in_directory("poop"):
            py_files.append(py_file)
        self.assertEqual(2, len(py_files))
        self.assertIn("poop/poop_2.py", py_files)
        self.assertIn("poop/poop_1.py", py_files)
        shutil.rmtree("poop", True)

if __name__ == "__main__":
    unittest.main()
