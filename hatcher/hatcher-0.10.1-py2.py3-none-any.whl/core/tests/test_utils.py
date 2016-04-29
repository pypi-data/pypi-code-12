import json
import os
import re
import shutil
import tempfile
import textwrap

import okonomiyaki

from okonomiyaki.file_formats import EggMetadata as OkonomiyakiEggMetadata
from okonomiyaki.file_formats._egg_info import _SPEC_DEPEND_LOCATION
from okonomiyaki.runtimes.runtime_metadata import _METADATA_ARCNAME
from okonomiyaki.versions import MetadataVersion
from zipfile2 import ZipFile

from hatcher.errors import InvalidEgg, InvalidRuntime
from hatcher.testing import unittest, make_testing_egg
from ..utils import (
    AppSorter, EggMetadata, EggNameSorter, RuntimeMetadataV0,
    RuntimeMetadataV1)


class TestEggNameSorter(unittest.TestCase):

    def test_hashing(self):
        # Given
        egg = 'egg-0.1.2.dev4-1.egg'

        # When
        sorter1 = EggNameSorter(egg)
        sorter2 = EggNameSorter(egg)

        # Then
        self.assertEqual(sorter1, sorter2)
        self.assertEqual(hash(sorter1), hash(sorter2))

    def test_cannot_compare(self):
        # Given
        left = 'egg-1.2.0-1.egg'
        right = EggNameSorter('egg-1.2.0-1.egg')

        # When/Then
        with self.assertRaises(TypeError):
            left == right

        # When/Then
        with self.assertRaises(TypeError):
            left < right

        # When/Then
        with self.assertRaises(TypeError):
            left > right

        # When/Then
        with self.assertRaises(TypeError):
            left <= right

        # When/Then
        with self.assertRaises(TypeError):
            left >= right

    def test_equality(self):
        # Given
        left = EggNameSorter('egg-1.2.0-1.egg')
        right = EggNameSorter('egg-1.2.0-1.egg')

        # When/Then
        self.assertEqual(left, right)

        # Given
        left = EggNameSorter('egg-1.2.0-1.egg')
        right = EggNameSorter('egg-1.2-1.egg')

        # When/Then
        self.assertEqual(left, right)

        # Given
        left = EggNameSorter('egg-1.2.0-1.egg')
        right = EggNameSorter('egg-1.2.0-2.egg')

        # When/Then
        self.assertNotEqual(left, right)

        # Given
        left = EggNameSorter('egg-1.1.0-1.egg')
        right = EggNameSorter('egg-1.2.0-1.egg')

        # When/Then
        self.assertNotEqual(left, right)

        # Given
        left = EggNameSorter('egg-1.1.0-1.egg')
        right = EggNameSorter('other_egg-1.1.0-1.egg')

        # When/Then
        self.assertNotEqual(left, right)

    def test_less_than(self):
        # Given
        left = EggNameSorter('egg-1.2.0-1.egg')
        right = EggNameSorter('egg-1.2.0-1.egg')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left >= right)
        self.assertFalse(left < right)
        self.assertFalse(left > right)

        # Given
        left = EggNameSorter('egg-1.2.0-1.egg')
        right = EggNameSorter('egg-1.2.0-2.egg')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = EggNameSorter('egg-1.2.0-2.egg')
        right = EggNameSorter('egg-1.2.1-1.egg')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = EggNameSorter('a-1.2.0-1.egg')
        right = EggNameSorter('b-1.2.0-1.egg')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = EggNameSorter('a-1.2.0-1.egg')
        right = EggNameSorter('b-1.1.0-1.egg')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)


class TestAppSorter(unittest.TestCase):

    def test_hashing(self):
        # Given
        name = 'mayavi'
        version = '2.3.4-1'
        python_tag = 'cp27'

        # When
        sorter1 = AppSorter(name, version, python_tag)
        sorter2 = AppSorter(name, version, python_tag)

        # Then
        self.assertEqual(sorter1, sorter2)
        self.assertEqual(hash(sorter1), hash(sorter2))

    def test_cannot_compare(self):
        # Given
        left = EggNameSorter('egg-1.2.0-1.egg')
        right = AppSorter('mayavi', '2.3.4-1', 'cp27')

        # When/Then
        with self.assertRaises(TypeError):
            left == right

        # When/Then
        with self.assertRaises(TypeError):
            left < right

        # When/Then
        with self.assertRaises(TypeError):
            left > right

        # When/Then
        with self.assertRaises(TypeError):
            left <= right

        # When/Then
        with self.assertRaises(TypeError):
            left >= right

    def test_equality(self):
        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-1', 'cp27')

        # When/Then
        self.assertEqual(left, right)

        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2-1', 'cp27')

        # When/Then
        self.assertEqual(left, right)

        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-2', 'cp27')

        # When/Then
        self.assertNotEqual(left, right)

        # Given
        left = AppSorter('app', '1.1.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-1', 'cp27')

        # When/Then
        self.assertNotEqual(left, right)

        # Given
        left = AppSorter('app', '1.1.0-1', 'cp27')
        right = AppSorter('other_app', '1.1.0-1', 'cp27')

        # When/Then
        self.assertNotEqual(left, right)

        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-1', 'cp34')

        # When/Then
        self.assertNotEqual(left, right)

    def test_less_than(self):
        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-1', 'cp27')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left >= right)
        self.assertFalse(left < right)
        self.assertFalse(left > right)

        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-2', 'cp27')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = AppSorter('app', '1.2.0-2', 'cp27')
        right = AppSorter('app', '1.2.1-1', 'cp27')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = AppSorter('a', '1.2.0-1', 'cp27')
        right = AppSorter('b', '1.2.0-1', 'cp27')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = AppSorter('a', '1.2.0-1', 'cp27')
        right = AppSorter('b', '1.1.0-1', 'cp27')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)

        # Given
        left = AppSorter('app', '1.2.0-1', 'cp27')
        right = AppSorter('app', '1.2.0-1', 'cp34')

        # When/Then
        self.assertTrue(left <= right)
        self.assertTrue(left < right)
        self.assertFalse(left >= right)
        self.assertFalse(left > right)


class TestEggMetadataValidation(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix='hatcher-')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_from_egg_unsupported_metadata_version(self):
        # Given
        name = 'bad_egg'
        version = '1.0'
        build = 1
        metadata_version = '1000.0'
        spec_depend = textwrap.dedent("""\
        metadata_version = {metadata_version!r}
        name = {name!r}
        version = {version!r}
        build = {build!r}

        arch = 'amd64'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = '2.7'
        packages = [
        ]
        """.format(name=name, version=version, build=build,
                   metadata_version=metadata_version))
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('EGG-INFO/spec/depend', spec_depend.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"Egg '{0}' uses an unsupported metadata version {1}. "
                 "Maximum supported metadata version is.*".format(
                     re.escape(os.path.basename(target)),
                     re.escape(metadata_version)))):
            EggMetadata.from_file(target)

    def test_from_egg_invalid_egg_name(self):
        # Given
        name = 'bad-egg'
        version = '1.0'
        build = 1
        metadata_version = '1.1'
        spec_depend = textwrap.dedent("""\
        metadata_version = {metadata_version!r}
        name = {name!r}
        version = {version!r}
        build = {build!r}

        arch = 'amd64'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = '2.7'
        packages = [
        ]
        """.format(name=name, version=version, build=build,
                   metadata_version=metadata_version))
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('EGG-INFO/spec/depend', spec_depend.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"Invalid egg name: '{0}'".format(
                    re.escape(os.path.basename(target))))):
            EggMetadata.from_file(target)

    def test_from_egg_missing_metadata(self):
        # Given
        name = 'bad_egg'
        version = '1.0'
        build = 1
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('file', u'contents'.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"Egg '{0}' is missing Enthought metadata and may not be "
                 "in the enpkg egg format.".format(
                     re.escape(os.path.basename(target))))):
            EggMetadata.from_file(target)

    def test_from_egg_invalid_requirement_string(self):
        # Given
        name = 'bad_egg'
        version = '1.0'
        build = 1
        metadata_version = '1.1'
        spec_depend = textwrap.dedent("""\
        metadata_version = {metadata_version!r}
        name = {name!r}
        version = {version!r}
        build = {build!r}

        arch = 'amd64'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = '2.7'
        packages = [
            'bad-1.0-1'
        ]
        """.format(name=name, version=version, build=build,
                   metadata_version=metadata_version))
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('EGG-INFO/spec/depend', spec_depend.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"Egg '{0}' has an invalid requirement string in egg "
                 "dependency list: '{1}'$".format(
                     re.escape(os.path.basename(target)),
                     re.escape('bad-1.0-1')))):
            EggMetadata.from_file(target)

    def test_from_egg_invalid_metadata_field(self):
        # Given
        name = 'bad_egg'
        version = '1.0'
        build = 1
        metadata_version = '1.2'
        spec_depend = textwrap.dedent("""\
        metadata_version = {metadata_version!r}
        name = {name!r}
        version = {version!r}
        build = {build!r}

        arch = 'amd64'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = '2.7'
        packages = [
        ]
        """.format(name=name, version=version, build=build,
                   metadata_version=metadata_version))
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('EGG-INFO/spec/depend', spec_depend.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"Egg '{0}' metadata field is invalid: "
                 "\(python_tag = <undefined>\)$".format(
                     re.escape(os.path.basename(target))))):
            EggMetadata.from_file(target)

    def test_from_egg_invalid_metadata(self):
        # Given
        if okonomiyaki.__version_info__ < (0, 15):
            r_msg = "^python_tag cannot be guessed for python = red$"
        else:
            r_msg = (
                r"^Egg 'bad_egg-1.0-1.egg' metadata field is invalid: "
                 "\(python = 'red'\)$"
            )

        name = 'bad_egg'
        version = '1.0'
        build = 1
        metadata_version = '1.1'
        spec_depend = textwrap.dedent("""\
        metadata_version = {metadata_version!r}
        name = {name!r}
        version = {version!r}
        build = {build!r}

        arch = 'amd64'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = 'red'
        packages = [
        ]
        """.format(name=name, version=version, build=build,
                   metadata_version=metadata_version))
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('EGG-INFO/spec/depend', spec_depend.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(InvalidEgg, r_msg):
            EggMetadata.from_file(target)

    def test_from_egg_parse_error(self):
        # Given
        name = 'bad_egg'
        version = '1.0'
        build = 1
        metadata_version = '1.1'
        spec_depend = textwrap.dedent("""\
        metadata_version = {metadata_version!r}
        name = {name!r}
        version = {version!r}
        build = {build!r}

        arch = 'amd64'
        platform = 'linux2'
        osdist = 'RedHat_5'
        python = 'red'
        packages = [
            non-parsable,
        ]
        """.format(name=name, version=version, build=build,
                   metadata_version=metadata_version))
        target = os.path.join(
            self.tempdir, '{0}-{1}-{2}.egg'.format(name, version, build))
        with ZipFile(target, 'w') as fh:
            fh.writestr('EGG-INFO/spec/depend', spec_depend.encode('utf-8'))

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"^Unexpected error parsing egg '{0}'.".format(
                    re.escape(os.path.basename(target))))):
            EggMetadata.from_file(target)

    def test_from_egg_not_valid_zip_file(self):
        # Given
        target = os.path.join(self.tempdir, "MKL-10.3-1.egg")
        with open(target, 'w'):
            pass

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"^Bad zip file when validating egg 'MKL-10.3-1.egg'\.$")):
            EggMetadata.from_file(target)

    def test_from_egg_strictly_supported(self):
        # Given
        higest_supported_metadata_version = (
            OkonomiyakiEggMetadata.HIGHEST_SUPPORTED_METADATA_VERSION
        )

        metadata_version = str(MetadataVersion(
                higest_supported_metadata_version.major,
                higest_supported_metadata_version.minor + 1))

        egg = make_testing_egg(
                self.tempdir,
                metadata_version=str(higest_supported_metadata_version))

        replace = re.compile(r'^metadata_version.*$')
        with ZipFile(egg.path, 'r') as fp:
            spec_depend = fp.read(_SPEC_DEPEND_LOCATION).decode()

        spec_depend = '\n'.join(
            replace.sub("metadata_version = '{0}'".format(metadata_version), l)
            for l in spec_depend.splitlines())
        spec_depend = spec_depend + '\n'

        with ZipFile(egg.path, 'w') as fp:
            fp.writestr(_SPEC_DEPEND_LOCATION, spec_depend.encode())

        # When
        with self.assertRaisesRegexp(
                InvalidEgg,
                (r"^Egg '{0}' uses an unsupported metadata version {1}. "
                 "Maximum supported metadata version is.*".format(
                     re.escape(os.path.basename(egg.path)),
                     re.escape(metadata_version)))):
            EggMetadata.from_file(egg.path)


class TestRuntimeMetadataV0Validation(unittest.TestCase):

    def test_invalid_filename(self):
        # Given
        path = '/path/to/file.runtime'

        # When/Then
        with self.assertRaisesRegexp(
                InvalidRuntime, r"Invalid filename format"):
            RuntimeMetadataV0.from_file(path)


class TestRuntimeMetadataV1Validation(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix='hatcher-')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_invalid_zip_file(self):
        # Given
        filename = 'cpython-2.7.9+1-rh5_x86_64-gnu.runtime'
        path = os.path.join(self.tempdir, filename)
        with open(path, 'w'):
            pass

        # When/Then
        with self.assertRaisesRegexp(
                InvalidRuntime,
                r"'{0}' is not an Enthought runtime package".format(
                    re.escape(filename))):
            RuntimeMetadataV1.from_file(path)

    def test_invalid_language(self):
        # Given
        language = 'whitespace'
        metadata = {'metadata_version': '1.0',
                    'implementation': language}
        filename = 'cpython-2.7.9+1-rh5_x86_64-gnu.runtime'
        path = os.path.join(self.tempdir, filename)
        with ZipFile(path, 'w') as fp:
            fp.writestr(_METADATA_ARCNAME, json.dumps(metadata).encode())

        # When/Then
        with self.assertRaisesRegexp(
                InvalidRuntime,
                r"'{0}': No support for language '{1}'".format(
                    re.escape(filename),
                    re.escape(language))):
            RuntimeMetadataV1.from_file(path)

    def test_invalid_metadata(self):
        # Given
        metadata = {'metadata_version': '1.0',
                    'implementation': 'cpython'}
        filename = 'cpython-2.7.9+1-rh5_x86_64-gnu.runtime'
        path = os.path.join(self.tempdir, filename)
        with ZipFile(path, 'w') as fp:
            fp.writestr(_METADATA_ARCNAME, json.dumps(metadata).encode())

        # When/Then
        with self.assertRaisesRegexp(
                InvalidRuntime,
                r"'{0}': Invalid metadata: \"'[^']+' is a required "
                "property\"".format(
                    re.escape(filename))):
            RuntimeMetadataV1.from_file(path)
