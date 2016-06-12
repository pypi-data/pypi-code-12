import unittest
import psychic_disco
import shutil
import os

zip_file_path = '.psychic_disco/deployment-package.zip'


class TestDeploymentPackage(unittest.TestCase):
    def test_default_is_same(self):
        dp = psychic_disco.deployment_package.default()
        dp2 = psychic_disco.deployment_package.default()
        self.assertEqual(dp, dp2)

    def test_localpath(self):
        dp = psychic_disco.deployment_package.default()
        self.assertEqual(zip_file_path, dp.localpath)


class TestDeploymentPackageOperations(unittest.TestCase):
    def setUp(self):
        self.dp = psychic_disco.deployment_package.default()
        shutil.rmtree("poop", True)
        os.mkdir("poop")
        os.chdir("poop")

    def tearDown(self):
        os.chdir("..")
        shutil.rmtree("poop", True)

    def test_setup_virtualenv(self):
        with open("requirements.txt", "w") as f:
            f.write("Jinja2==2.8\npsychic_disco==0.6.0\n")
        installed_packages = self.dp.setup_virtualenv("venv")
        self.assertIn(('Jinja2', '2.8'), installed_packages)
        self.assertIn(('psychic-disco', '0.6.0'), installed_packages)

    def test_bundle(self):
        with open("poop1.py", "w") as f:
            f.write("print 'hello world'\n")
        self.dp.bundle()
        self.assertTrue(os.path.exists(zip_file_path))


if __name__ == "__main__":
    unittest.main()
