from enum import Enum
from foundation_platform.common import error
import mimetypes
import os
import shutil
# import mmap
# import sys
# import platform
import zipfile
# import wget
# import logging
# import socket
# from foundation_platform.messaging import image


class CsarBadValue(error.Error):
    # Raised when trying to read or write a CSAR and some value isn't what we expected.
    def __init__(self, value):
        super(CsarBadValue, self).__init__('')
        self.__value = value

    def __str__(self):
        return "Bad Value:" + repr(self.__value)


class CsarBadInput(error.Error):
    # Raised when setting various parameters used in creating/loading CSARs and they have problems
    def __init__(self, value):
        super(CsarBadInput, self).__init__('')
        self.__value = value

    def __str__(self):
        return "Bad input:" + repr(self.__value)


class CsarMetadataSections(Enum):
    """
    Required TOSCA Metadata directories for a CSAR.

    Values are the names of the directories
    the metadata will be stored in.
    """

    TOSCA_Metadata = 'TOSCA-Metadata'
    Definitions = 'Definitions'


class CsarToscaMetaContent(Enum):
    """
    Names of the various sections within a TOSCA.meta file.

    Values are the strings that will
    be emitted to the metadata files.
    """

    TOSCA_Version = 'TOSCA-Meta-File-Version'
    CSAR_Version = 'CSAR-Version'
    Author = 'Created-By'
    Name = 'Name'
    Content_type = 'Content-Type'


class CsarSection(Enum):
    """
    Names of the CSAR sections we know how to deal with.

    Values of the enums will be used as
    the directory names when storing/reading content.
    """

    Scripts = 'scripts'
    Images = 'images'
    Hots = 'hot-templates'


class CsarOperations(Enum):
    Create = 'create'
    Ingest = 'ingest'
    Load = 'load'


class Csar(object):
    def __init__(self,
                 name='default_csar',
                 input_dir=None,
                 output_dir=None,
                 author="Nokia via the foundation platform",
                 version='1.0',
                 input_file=None,
                 upload_url=None):
        """
        A representation of a TOSCA CSAR.

        This object assumes it is in an environment that can be used to upload the CSAR contents
        into a cloud library.  As such, it assumes that there is a web server available to it that
        can server requests from a cloud for things like uploading files (via wget, curl, etc).
        The object relies on the messaging services provided in the foundation_platform to talk
        to the actual cloud(s).

        When unpacking the CSAR, the object will create directories in the html_dir folder so
        the user ID invoking the tool must have permissions to create directories and write files
        in that directory.

        Note: Passing "None" to a parameter preserves its current value.

        :param name: name of the CSAR (default: default_csar).
        :type name: str.
        :param input_dir: input directory to find the files when building the CSAR.
        :type input_dir: str.
        :param output_dir: directory to store files when building the CSAR.
        :type output_dir: str.
        :param author: author of the CSAR.
        :type author: str.
        :return: a CSAR object.
        :rtype: Csar.
        """

        # Information about CSARs in general
        #
        self.__name = None
        self.__author = None
        self.__input_directory = None
        self.__output_directory = None
        self.__input_file = None
        self.__tosca_meta_file_version = '1.0'
        self.__csar_version = version
        self.__upload_url = upload_url

        if name is not None:
            self.set_name(name)
        if author is not None:
            self.set_author(author)
        if input_dir is not None:
            self.set_input_dir(input_dir)
        if output_dir is not None:
            self.set_output_dir(output_dir)
        if input_file is not None:
            self.__input_file = input_file

        # These are the sections we know how to process and where we'll put those contents.
        self.__csar_map = {CsarSection.Images: 'images',
                           CsarSection.Scripts: 'scripts',
                           CsarSection.Hots: 'hot-files'}
        self.__tosca_metadata_file = 'TOSCA.meta'

        # Variables needed for creating CSARs.  The dict comprehension is just setting a bunch
        # of empty lists for the thinks we know how to handle as specified in the CSAR map
        self.__metadata_sections = {k: k.value for k in CsarMetadataSections}
        self.__provided_sections = {k: [] for k in CsarSection}
        self.__section_provided = False  # Set to True if any non-metadata section is provided

        # Custom MIME types that we use
        self.__mime_types = mimetypes.MimeTypes()
        self.__mime_types.add_type("application/octet-stream", ".qcow2", strict=True)
        self.__mime_types.add_type("text/x-python", ".py", strict=True)
        self.__mime_types.add_type("text/x-yaml", ".yaml", strict=True)

        # self.hostAddr = socket.gethostbyname(socket.gethostname())
        # self.hostName = socket.gethostname()

        # logging
        # self.logfile = ingest_log
        # self.loglevel = ingest_log_level

    @staticmethod
    def __check_file(directory, fname, read=True, write=False):
        """
        Verifies that a file exists in the specified directory and has the requested permissions.

        :param directory: directory to look in for the file.
        :type directory: str.
        :param fname: file name to check.
        :type fname: str.
        :param read: check to see if file is readable (default: True).
        :type read: bool.
        :param write: check to see if the file is writable (default: False).
        :type write: bool.
        :return: True if file exists with expected permissions, else False.
        :rtype: bool.
        """

        __full_name = directory + "/" + fname
        if read and write:
            __mode = "r+"
        elif read:
            __mode = "r"
        elif write:
            __mode = "w"
        else:
            # Can't check file for simple existence (e.g. not readable or writeable)
            return False
        try:
            __fp = open(__full_name, mode=__mode)
            __fp.close()
        except IOError:
            return False
        return True

    @staticmethod
    def __check_dir(directory, read=True, write=False):
        """
        Verify that a given directory exists with the required permissions.

        :param directory: directory to check for.
        :type directory: str.
        :param read: check for read permissions from the directory.
        :type read: bool.
        :param write: check for write permissions to the directory.
        :type write: bool.
        :return: True if directory exists with the requested permissions, else False.
        :rtype: bool.
        """

        if not directory:
            return False
        if not os.path.exists(directory):
            return False
        if read and write:
            __mode = os.R_OK | os.W_OK | os.X_OK
        elif read:
            __mode = os.R_OK | os.X_OK
        elif write:
            __mode = os.W_OK | os.X_OK
        else:
            # Can't just check for directory existence
            return False
        return os.access(directory, __mode)

    @staticmethod
    def __create_dir(directory, write=True):
        """
        Create a directory.

        Note that this will not change the permissions on an existing
        directory.  The directory will be writable by default.  Directory will always have at
        least read & execute.

        :param directory: directory to create.
        :type directory: str.
        :param write: make directory writeable (default: True).
        :type write: bool.
        :return: True if directory was created, else False (including if the dir already exists).
        :rtype: bool.
        """

        if write:
            __mode = 0o777
        else:
            __mode = 0o555
        try:
            os.makedirs(directory, __mode)
            return True
        except OSError:
            return False

    def __create_csar_dir(self, directory):
        """
        Create a directory for our CSAR in the output directory location

        :param directory: name of the directory to create.
        :type directory: str.
        """

        self.__create_dir(os.path.join(self.output_directory, directory))

    def __load_files(self, section, directory):
        """
        Load files in the specified directory into the provided sections structure for section

        :param section: section the files in the directory are for.
        :type section: CsarSection.
        :param directory: directory to load files from.
        :type directory: str.
        """

        __file_list = [f for f in os.listdir(directory)
                       if os.path.isfile(os.path.join(directory, f))]
        [self.__provided_sections[section].append(f) for f in __file_list]

    def validate(self, operation):
        """
        Verify that the CSAR has the required information to perform the requested operation

        :param operation: operation to check.
        :type operation: str (CsarOperations).
        :raises: CsarBadInput - message text describes what was wrong.
        """

        if operation == CsarOperations.Create:
            if not self.input_directory:
                raise CsarBadInput('missing input directory')
            if not self.output_directory:
                raise CsarBadInput('missing output directory')
            if not self.author:
                raise CsarBadInput('missing CSAR name')
        elif operation == CsarOperations.Ingest:
            if not self.output_directory:
                raise CsarBadInput('missing output directory')
            if not self.input_file:
                raise CsarBadInput('no input file specified')
            if not zipfile.is_zipfile(self.input_file):
                raise CsarBadInput('file name is not a valid zip file: ' + self.input_file)
        elif operation == CsarOperations.Load:
            if not self.upload_url:
                raise CsarBadInput('missing upload URL')
        else:  # Unknown operation
            raise CsarBadInput('unknown operation: ' + str(operation))

    def __get_file_mime_type(self, file_name):
        """
        Return the mime type of the provided file.

        :param file_name: file whose mime type we want to guess.
        :return: mime type of the file.
        :rtype: str.
        """

        __type, __encodeing = self.__mime_types.guess_type(file_name)
        if __type is None:
            __type = "application/octet-stream"
        return __type

    def create(self, dest_file, cleanup=False):
        """
        Create a CSAR based on the provided information.

        Warning: If the destination file is
        in the directory that is being used to sore the CSAR while it's being built (e.g. it's
        in a subdirectory under output_directory) and cleanup = True, then the zipped CSAR file
        will be deleted when the create completes (likely not what was intended).

        :param dest_file: full or relative to use for the zipped CSAR file.
        :type dest_file: str.
        :param cleanup: set to True to remove temporary files created while zipping content.
        :type cleanup: bool.
        """

        try:
            # Make sure we have all the information we need before we get started.

            self.validate(CsarOperations.Create)
        except CsarBadInput as e:
            raise e

        # Create the basic directory structure for the CSAR.  This will include the required
        # metadata directories plus a directory for each of the elements we have (e.g. images)
        # Copy any of the provided files as well
        [self.__create_csar_dir(d.value) for d in self.__metadata_sections]
        if self.has_sections:
            for section in self.__provided_sections:
                if not self.__provided_sections[section] == []:
                    self.__create_csar_dir(section.value)
                    [shutil.copy(os.path.join(self.__input_directory, source),
                                 os.path.join(self.__output_directory, section.value))
                     for source in self.__provided_sections[section]]

        # Based on the provided sections, create the metadata.
        try:
            with open(self.tosca_metadata_file, 'w') as f:
                f.write(CsarToscaMetaContent.TOSCA_Version.value + ": " +
                        self.tosca_meta_file_version + "\n")
                f.write(CsarToscaMetaContent.CSAR_Version.value + ": " + self.version + "\n")
                f.write(CsarToscaMetaContent.Author.value + ": " + self.author + "\n")
                if self.has_sections:
                    for s in self.__provided_sections:
                        if not self.__provided_sections[s] == []:
                            for sf in self.__provided_sections[s]:
                                f.write("\n")
                                f.write(CsarToscaMetaContent.Name.value + ": " + sf + "\n")
                                f.write(CsarToscaMetaContent.Content_type.value + ": " +
                                        self.__get_file_mime_type(sf) + "\n")
        except IOError as e:
            raise ("failed to create metadata files - " + str(e))

        # Create the destination file and zip everything in our output directory to it
        # Note: the paths we store in the zip file are relative to dest_file, e.g. we don't
        # store the full path of our build system in the zip file but the relative path from
        # where we're building.
        with zipfile.ZipFile(dest_file + '.zip', 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for dirname, subdir, files in os.walk(self.output_directory):
                # Add the files in this directory.
                for f in files:
                    __actual_file_name = os.path.join(dirname, f)
                    __zip_name = os.path.relpath(__actual_file_name, self.output_directory)
                    zf.write(__actual_file_name, __zip_name)
                # Add the empty subdirs - subdirs with files will be added with the files
                for s in subdir:
                    __actual_dir_name = os.path.join(dirname, s)
                    if len(os.listdir(__actual_dir_name)) == 0:
                        __zip_name = os.path.relpath(__actual_dir_name, self.output_directory)
                        zf.write(__actual_dir_name, __zip_name)

        # If we were asked to clean-up the output directory, do that now
        if cleanup:
            shutil.rmtree(self.__output_directory, ignore_errors=True)

    def ingest(self):
        """
        Ingest a CSAR from a zip file.

        Ingest will make sure that the required sections exist
        and will load any optional sections, but will not complain (or take action) when there
        are unexpected items in the file.

        :raises: CsarBadInput, CsarBadValue.
        """

        try:
            self.validate(CsarOperations.Ingest)
        except CsarBadInput as e:
            raise e

        # Unzip the file into our output directory, then walk the structure we see and update
        # our internal structures to match what we see.
        with zipfile.ZipFile(self.input_file) as zf:
            zf.extractall(path=self.output_directory)

            # Make sure we find the required sections.
            for s in self.__metadata_sections:
                if not self.__check_dir(os.path.join(self.output_directory, s.value)):
                    # Some implementation of ZipFile seem to not deal well with extracting
                    # empty directories.  Thus, if Definitions is empty, it may not extract.
                    # Work around that problem here by checking to see if Definitions was in the
                    # original zip file and, if so, don't throw an error.
                    if s == CsarMetadataSections.Definitions:
                        if CsarMetadataSections.Definitions.value in zf.namelist():
                            continue
                        else:
                            raise CsarBadValue('required directory missing from zip: ' + s.value)
                    else:
                        raise CsarBadValue('required directory missing from zip: ' + s.value)

            # Find out what optional sections we have and load up that information
        for s in self.__provided_sections:
            __file = os.path.join(self.output_directory, s.value)
            if self.__check_dir(__file):
                self.__section_provided = True
                self.__load_files(s, __file)

        # The name of the CSAR isn't stored within the CSAR so we will default it to the name
        # of the file (without .zip and without any leading path info).
        (head, tail) = os.path.split(self.input_file)
        self.set_name(tail[tail.find('.zip'):])

        # Parse the TOSCA metadata file to get the remaining information we need.
        __meta_file = {}
        with open(os.path.join(self.output_directory,
                               CsarMetadataSections.TOSCA_Metadata.value,
                               self.tosca_metadata_file)) as f:
            for __line in f:
                if len(__line.strip()) != 0:  # Skips blank lines
                    __k, __v = __line.split(':')
                    __meta_file[__k] = __v

        # Author info
        if CsarToscaMetaContent.Author.value in __meta_file:

            self.set_author(__meta_file[CsarToscaMetaContent.Author.value].strip())
        else:
            raise CsarBadValue('no author section found in CSAR: ' +
                               CsarToscaMetaContent.Author.value)
        # CSAR Version
        if CsarToscaMetaContent.CSAR_Version.value in __meta_file:
            self.set_version(__meta_file[CsarToscaMetaContent.CSAR_Version.value].strip())
        else:
            raise CsarBadValue('no CSAR version found in CSAR: ' +
                               CsarToscaMetaContent.CSAR_Version.value)

        # TOSCA Metadata version
        if CsarToscaMetaContent.TOSCA_Version.value in __meta_file:
            if __meta_file[CsarToscaMetaContent.TOSCA_Version.value].strip() != '1.0':
                raise CsarBadValue('unsupported TOSCA Version ' +
                                   CsarMetadataSections.TOSCA_Metadata.value)
        else:
            raise CsarBadValue('no TOSCA Version found: ' +
                               CsarToscaMetaContent.TOSCA_Version.value)

    def load_to_cloud(self):
        """
        Load a CSAR into a specific cloud catalog.
        """

        try:
            self.validate(CsarOperations.Load)
        except CsarBadInput as e:
            raise e

    def add_image(self, image_name):
        """
        Add an image to the list of images in the CSAR.

        File names are relative to the input
        directory provided when calling set_create_info().  File names are checked to make sure
        the file exists and can be read before being added to the list.

        :param image_name: name of the image file to add.
        :type image_name: str.
        :raises: CsarBadInput.
        """

        if not self.__check_file(self.__input_directory, image_name):
            raise CsarBadInput("can't read " +
                               os.path.join(self.__input_directory, image_name))
        self.__provided_sections[CsarSection.Images].append(image_name)
        self.__section_provided = True

    @property
    def images(self):
        """
        The list of images for the CSAR.

        :return: list of images.
        :rtype: list.
        """

        return self.__provided_sections[CsarSection.Images]

    def add_hot_template(self, hot_template_name):
        """
        Add a hot template to the list of hot templates in the CSAR.

        File names are relative
        to the input directory provided when calling set_create_info().  File names are checked
        to make sure the file exists and can be read before being added to the list.

        :param hot_template_name: name of the hot template file to add.
        :type hot_template_name: str.
        :raises: CsarBadInput.
        """

        if not self.__check_file(self.__input_directory, hot_template_name):
            raise CsarBadInput("can't read " +
                               os.path.join(self.__input_directory, hot_template_name))
        self.__provided_sections[CsarSection.Hots].append(hot_template_name)
        self.__section_provided = True

    @property
    def hot_templates(self):
        """
        The list of HOT files for the CSAR.

        :return: list of hot files.
        :rtype: list.
        """

        return self.__provided_sections[CsarSection.Hots]

    def add_script(self, script_name):
        """
        Add a script to the list of scripts in the CSAR.

        File names are relative
        to the input directory provided when calling set_create_info().  File names are checked
        to make sure the file exists and can be read before being added to the list.

        :param script_name: name of the script file to add.
        :type script_name: str.
        :raises: CsarBadInput.
        """

        if not self.__check_file(self.__input_directory, script_name):
            raise CsarBadInput("can't read " +
                               os.path.join(self.__input_directory, script_name))
        self.__provided_sections[CsarSection.Scripts].append(script_name)
        self.__section_provided = True

    @property
    def scripts(self):
        """
        The list of scripts for the CSAR.

        :return: list of scripts.
        :rtype: list.
        """

        return self.__provided_sections[CsarSection.Scripts]

    def set_input_dir(self, directory):
        """
        Set the directory to pull files from when creating the CSAR.

        :param directory: full or relative path to the directory find input files.
        :type directory: str.
        """

        if not self.__check_dir(directory):
            raise CsarBadInput("can't read " + directory)
        self.__input_directory = directory

    @property
    def input_directory(self):
        """
        The input directory to get information from when creating the CSAR.

        :return: input directory name.
        :rtype: str.
        """

        return self.__input_directory

    def set_output_dir(self, directory):
        """
        Set (and create if needed) the output directory to use when building the CSAR or ingesting.

        :param directory: full or relative path to the dirctory to use when building the CSAR.
        :type directory: str.
        """

        if not self.__check_dir(directory, write=True):
            if not self.__create_dir(directory):
                raise CsarBadInput("can't create " + directory)
        elif not self.__check_dir(directory, write=True):
            raise CsarBadInput("no write permissions to " + directory)
        self.__output_directory = directory

    @property
    def output_directory(self):
        """
        The output directory to use during CSAR building.

        This will contain the actual CSAR
        directory structure during the build and is what is put into the zip file.

        :return: output directory name.
        :rtype: str.
        """

        return self.__output_directory

    def set_input_file(self, file_name):
        """
        Set the file to read when ingesting a CSAR.

        :param file_name: CSAR file to read.
        """

        self.__input_file = file_name

    @property
    def input_file(self):
        """
        The name of the file that will be/was read when ingesting the CSAR.

        :return: input file name.
        :rtype: str.
        """

        return self.__input_file

    def set_name(self, csar_name):
        """
        Set the name for the CSAR.

        :param csar_name: name of the CSAR.
        :type csar_name: str.
        """

        self.__name = csar_name

    @property
    def csar_name(self):
        """
        The name of the CSAR.

        :return: CSAR name.
        :rtype: str.
        """

        return self.__name

    def set_author(self, author):
        """
        Set the author of the CSAR.

        :param author: CSAR author.
        :type author: str.
        """

        self.__author = author

    @property
    def author(self):
        """
        The author of this CSAR.

        :return: csar author.
        :rtype: str.
        """

        return self.__author

    def set_version(self, version):
        """
        Set the version for this CSAR.

        :param version: version number.
        :type version: str.
        """

        self.__csar_version = version

    @property
    def version(self):
        """
        The version of this CSAR.

        :return: CSAR version.
        :rtype: str.
        """

        return self.__csar_version

    def set_upload_url(self, url):
        """
        Set the upload URL for the CSAR.

        :param url: FQDN to be used when uploading the CSAR.
        :type url: str.
        """

        self.__upload_url = url

    @property
    def upload_url(self):
        """
        The URL to use when uploading the CSAR to a catalog.

        :return: upload URL.
        :rtype: str.
        """

        return self.__upload_url

    @property
    def tosca_meta_file_version(self):
        """
        The version of this CSAR as TOSCA knows it.

        :return: CSAR version.
        :rtype: str.
        """

        return self.__tosca_meta_file_version

    @property
    def tosca_metadata_file(self):
        """
        The path to the TOSCA Metadata file within the CSAR.

        :return: TOSCA Metadata file path.
        :rtype: str.
        """

        return os.path.join(self.output_directory, CsarMetadataSections.TOSCA_Metadata.value,
                            'TOSCA.meta')

    @property
    def has_sections(self):
        """
        Were any optional sections provided?

        :return: True if we have optional sections, else False.
        :rtype: bool.
        """
        return self.__section_provided
