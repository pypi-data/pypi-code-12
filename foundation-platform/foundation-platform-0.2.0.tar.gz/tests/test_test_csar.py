from foundation_platform.csar import csar
import os
import shutil
import unittest2 as unittest


class TestCsar(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCsar, self).__init__(*args, **kwargs)
        # Per out standards, all temporary test data goes in tests/tmp/test_file_name
        # We're assuming here that we're running in the project's root directory.
        self.__base_dir = os.path.join(os.getcwd(), 'tests')
        self.__test_base = os.path.join(self.__base_dir, 'tmp', 'test_csar')
        self.__csar_output_dir = os.path.join(self.__test_base, 'csar_output')
        self.__csar_input_dir = os.path.join(self.__test_base, 'csar_input')
        self.__csar_load_dir = os.path.join(self.__test_base, 'csar_load')
        self.__author = "Test Author"
        self.__images = []
        self.__hots = []
        self.__scripts = []
        self.__upload_url = 'http://horizon-vtelco2.cic-nfv.com'

    def setUp(self):
        # Create the directories we'll need and populate them with our sample data.
        os.makedirs(self.__csar_output_dir)
        shutil.copytree(os.path.join(self.__base_dir, 'data'),
                        self.__csar_input_dir)
        [self.__images.append(f)
         for f in os.listdir(self.__csar_input_dir) if f.endswith('.qcow2')]
        [self.__hots.append(f)
         for f in os.listdir(self.__csar_input_dir) if f.endswith('.yaml')]
        [self.__scripts.append(f)
         for f in os.listdir(self.__csar_input_dir) if f.endswith('.env')]

    def tearDown(self):
        # Delete all the files in the directory before nuking the directory.
        shutil.rmtree(self.__csar_input_dir, ignore_errors=True)
        shutil.rmtree(self.__csar_output_dir, ignore_errors=True)
        shutil.rmtree(self.__test_base, ignore_errors=True)

    def __create_test_csar(self, input_dir=None, output_dir=None, name="myname", author=None):
        """Set up a CSAR for testing

        :param input_dir: input directory for the CSAR
        :type input_dir: str
        :param output_dir: output directory for the CSAR
        :type output_dir: str
        :param name: name of the CSAR (default: "myname")
        :type name: str
        :param author: author of the CSAR
        :type author: str
        :return: csar
        :rtype Csar:

        """

        if not input_dir:
            input_dir = self.__csar_input_dir
        if not output_dir:
            output_dir = self.__csar_output_dir
        if not author:
            author = self.__author
        return csar.Csar(name=name, input_dir=input_dir, output_dir=output_dir, author=author)

    def __read_test_csar(self, file_name):
        return csar.Csar(input_file=file_name, output_dir=self.__csar_load_dir)

    def test_required_create_params_create_output(self):
        # Passes if we can create a CSAR and have it create a test directory for us
        __test_dir = os.path.join(self.__test_base, "test")
        try:
            self.__create_test_csar(output_dir=__test_dir)
            self.assertTrue(os.path.exists(__test_dir), "didn't crate directory")
        except csar.CsarBadInput as e:
            self.fail("couldn't initialize csar and create output directory: " + str(e))

    def test_required_create_params_existing_output(self):
        # Passes if we can create a CSAR with the default output directory.
        try:
            self.__create_test_csar()
        except csar.CsarBadInput as e:
            self.fail("couldn't initialize csar with existing output directory " + str(e))

    def test_set_new_author(self):
        # Passes if we can set a new author for the CSAR
        try:
            __my_csar = self.__create_test_csar()
            __my_csar.set_author("foo")
            self.assertEqual(__my_csar.author, 'foo', 'failed to set author')
        except csar.CsarBadInput as e:
            self.fail("couldn't initialize csar " + str(e))

    def test_set_new_name(self):
        # Passes if we can change the name of a CSAR
        try:
            __my_csar = self.__create_test_csar()
            __new_name = "New Name"
            __my_csar.set_name(__new_name)
            self.assertEqual(__my_csar.csar_name, __new_name, "couldn't change csar name")
        except csar.CsarBadInput as e:
            self.fail("couldn't initialize csar " + str(e))

    def test_required_create_param_values(self):
        # Passes if we can create a CSAR with the values we provide.
        __my_csar = self.__create_test_csar()
        self.assertEqual(__my_csar.csar_name, "myname", "name not set")
        self.assertEqual(__my_csar.input_directory, self.__csar_input_dir, "input dir not set")
        self.assertEqual(__my_csar.output_directory, self.__csar_output_dir, "output dir not set")

    def test_add_images(self):
        # Passes if we can add image files to the CSAR
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_image(f) for f in self.__images]
        except csar.CsarBadInput as e:
            self.fail("couldn't add images to the CSAR - " + str(e))

    def test_add_scripts(self):
        # Passes if we can add scripts to the CSAR
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_script(f) for f in self.__scripts]
        except csar.CsarBadInput as e:
            self.fail("couldn't add scripts to the CSAR - " + str(e))

    def test_add_hots(self):
        # Passes if we can add hot templates to the CSAR
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_hot_template(f) for f in self.__hots]
        except csar.CsarBadInput as e:
            self.fail("couldn't add hot templates to the CSAR - " + str(e))

    def test_create_image_dir(self):
        # Passes if an image directory is created when we create a CSAR with an image
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_image(f) for f in self.__images]
            __dir_path = os.path.join(__my_csar.output_directory,
                                      csar.CsarSection.Images.value)
            __csar_file = os.path.join(self.__test_base, __my_csar.csar_name)
            __my_csar.create(__csar_file)
            self.assertTrue(os.path.isdir(__dir_path), "image directory not created")
            for f in self.__images:
                self.assertTrue(os.path.isfile(os.path.join(__dir_path, f)),
                                "image not copied: " + f)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_create_script_dir(self):
        # Passes if a script directory is created when we create a CSAR with a script
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_script(f) for f in self.__scripts]
            __dir_path = os.path.join(__my_csar.output_directory,
                                      csar.CsarSection.Scripts.value)
            __my_csar.create(os.path.join(self.__test_base, __my_csar.csar_name))
            self.assertTrue(os.path.isdir(__dir_path), "script directory not created")
            for f in self.__scripts:
                self.assertTrue(os.path.isfile(os.path.join(__dir_path, f)),
                                "script not copied: " + f)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_create_hot_dir(self):
        # Passes if a hot template directory is created when we create a CSAR with a hot template
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_hot_template(f) for f in self.__hots]
            __dir_path = os.path.join(__my_csar.output_directory,
                                      csar.CsarSection.Hots.value)
            __my_csar.create(os.path.join(self.__test_base, __my_csar.csar_name))
            self.assertTrue(os.path.isdir(__dir_path), "hot directory not created")
            for f in self.__hots:
                self.assertTrue(os.path.isfile(os.path.join(__dir_path, f)),
                                "not not copied: " + f)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_create_metadata_dir(self):
        # Passes if metadata directories are created when we create a CSAR
        try:
            __my_csar = self.__create_test_csar()
            __csar_file = os.path.join(self.__test_base, __my_csar.csar_name)
            __my_csar.create(__csar_file)
            # noinspection PyTypeChecker
            for f in csar.CsarMetadataSections:
                self.assertTrue(os.path.isdir(os.path.join(self.__csar_output_dir, f.value)),
                                f.name + " directory not created")
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_ingest_simple_content_validity(self):
        # Passes if the metadata directories contain valid content when we create a CSAR
        try:
            __my_output_csar = self.__create_test_csar()
            __csar_file = os.path.join(self.__test_base, __my_output_csar.csar_name)
            __my_output_csar.create(__csar_file, cleanup=False)
            __my_input_csar = self.__read_test_csar(__csar_file + ".zip")
            __my_input_csar.ingest()
            self.assertEqual(__my_input_csar.author, self.__author,
                             'incorrect author - expected ' + self.__author + ' got ' +
                             __my_input_csar.author)
            self.assertEqual(__my_input_csar.version, '1.0',
                             'incorrect csar version - expected 1.0, got ' +
                             __my_input_csar.version)
            self.assertEqual(__my_input_csar.tosca_meta_file_version, '1.0',
                             'incorrect TOSCA version - expected 1.0, got ' +
                             __my_input_csar.tosca_meta_file_version)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_create_csar_file(self):
        # Passes if we end up with a zip'ed CSAR file
        try:
            __my_csar = self.__create_test_csar()
            __csar_file = self.__test_base + "/" + __my_csar.csar_name
            __my_csar.create(__csar_file)
            self.assertTrue(os.path.isfile(__csar_file + ".zip"), "no csar file created")
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_ingest_csar_with_hot(self):
        # Passes if we can ingest a CSAR with HOT files
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_hot_template(f) for f in self.__hots]
            __csar_name = os.path.join(self.__test_base, __my_csar.csar_name)
            __my_csar.create(__csar_name, cleanup=True)
            __my_input_csar = self.__read_test_csar(__csar_name + ".zip")
            __my_input_csar.ingest()
            for f in self.__hots:
                self.assertTrue(f in __my_input_csar.hot_templates,
                                'missing hot template from csar: ' + f)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_ingest_csar_with_image(self):
        # Passes if we can ingest a CSAR with images
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_image(f) for f in self.__images]
            __csar_name = os.path.join(self.__test_base, __my_csar.csar_name)
            __my_csar.create(__csar_name, cleanup=True)
            __my_input_csar = self.__read_test_csar(__csar_name + ".zip")
            __my_input_csar.ingest()
            for f in self.__images:
                self.assertTrue(f in __my_input_csar.images,
                                'missing image from csar: ' + f)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_ingest_csar_with_script(self):
        # Passes if we can ingest a CSAR with scripts
        # self.assertTrue(False, "not yet implemented")
        try:
            __my_csar = self.__create_test_csar()
            [__my_csar.add_script(f) for f in self.__scripts]
            __csar_name = os.path.join(self.__test_base, __my_csar.csar_name)
            __my_csar.create(__csar_name, cleanup=True)
            __my_input_csar = self.__read_test_csar(__csar_name + ".zip")
            __my_input_csar.ingest()
            for f in self.__scripts:
                self.assertTrue(f in __my_input_csar.scripts,
                                'missing script from csar: ' + f)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail("csar create failed - " + str(e))

    def test_set_upload_url(self):
        # Passes if we can specify teh upload URL
        try:
            __my_csar = self.__create_test_csar()
            __my_csar.set_upload_url(self.__upload_url)
            self.assertEqual(__my_csar.upload_url, self.__upload_url,
                             "failed to set upload url - got " + __my_csar.upload_url)
        except (csar.CsarBadInput, csar.CsarBadValue) as e:
            self.fail('csar create failed - ' + str(e))


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCsar)
    suite()


if __name__ == '__main__':
    main()
