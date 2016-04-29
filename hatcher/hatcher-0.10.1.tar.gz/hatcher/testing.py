from copy import deepcopy
import hashlib
import json
import os
import sys
import zipfile2


if sys.version_info < (2, 7):
    import unittest2 as unittest  # noqa
else:
    import unittest  # noqa

from okonomiyaki.runtimes.runtime_metadata import (
    PythonRuntimeMetadataV1, _METADATA_ARCNAME)
from okonomiyaki.versions import MetadataVersion

from hatcher.core.utils import EggMetadata
from hatcher.tests import DUMMY_EGG


RUNTIME_CPYTHON_2_7_10_RH5_X86_64_METADATA = {
    'metadata_version': u'1.0',
    'implementation': u'cpython',
    'version': u'2.7.10+1',
    'language_version': u'2.7.10',
    'platform': u'rh5-x86_64',
    'abi': u'gnu',
    'build_revision': u'2.1.0-dev570',
    'executable': u'${prefix}/bin/python',
    'paths': (u'${prefix}/bin',),
    'post_install': (u'${executable}', u'${prefix}/lib/python2.7/custom_tools/fix-scripts.py'),  # noqa
    'scriptsdir': u'${prefix}/bin',
    'site_packages': u'${prefix}/lib/python2.7/site-packages',
    'python_tag': u'cp27',
}


def python_tag_from_metadata(metadata):
    if 'python_tag' in metadata:
        return metadata['python_tag']
    else:
        python = metadata['python']
        if python is None:
            return None
        else:
            return 'cp{0}'.format(''.join(python.split('.')))


NotGiven = object()


def legacy_index_entry_from_egg_metadata(
        metadata, available=True, python=NotGiven):
    metadata = deepcopy(metadata)
    metadata['full_version'] = '{version}-{build}'.format(
        version=metadata['version'], build=metadata['build'])
    if python is not NotGiven:
        metadata['python'] = python
    if 'python_tag' not in metadata:
        if metadata['python'] is None:
            tag = None
        else:
            tag = 'cp{0}{1}'.format(*metadata['python'].split('.'))
        metadata['python_tag'] = tag
    metadata['available'] = available
    metadata['mtime'] = round(metadata['mtime'])
    metadata['type'] = 'egg'
    metadata.pop('platform')
    metadata.pop('sha256')
    if 'product' not in metadata:
        metadata['product'] = None
    return metadata


def make_testing_egg_metadata(**kwargs):
    """Create metadata suitable for brood testing.

    Parameters
    ----------
    name : str
        The name of the package (e.g. "numpy").
    version : str
        The version of the package (e.g. "1.8.0").
    build : int
        The build number of the package (e.g. 2).
    md5 : str
        The md5sum of the package.
    sha256 : str
        The sha256 of the package.
    mtime : float
        The modification time of the file.
    packages : list of str
        The dependicies of the package.
    size : int
        The size of the resulting file.
    platform : str
        The platform for which the package has been built.
    python : str
        [Legacy] The version of python for which the package is built.
        This is mutually exclusive with the ``python_tag`` parameter.
    python_tag : str
        The Python runtime implmentation tag (PEP425).
    abi_tag : str
        The ABI tag (PEP425).

    """
    valid_keys = set(('name', 'version', 'build', 'md5', 'sha256', 'mtime',
                      'packages', 'size', 'platform', 'product', 'python',
                      'python_tag', 'abi_tag', 'metadata_version'))
    unexpected_args = dict((key, value) for key, value in kwargs.items()
                           if key not in valid_keys)
    if unexpected_args != {}:
        raise RuntimeError(
            'Unexpected keyword arguments: {0!r}'.format(unexpected_args))

    if 'python_tag' in kwargs and 'python' in kwargs:
        raise RuntimeError(
            'python_tag and python arguments are not compatible.')

    md5 = kwargs.pop('md5', None)
    sha256 = kwargs.pop('sha256', None)

    testing_st = os.stat(__file__)
    metadata = {
        "name": "dummy",
        "version": "1.0.1",
        "build": 1,
        "mtime": round(testing_st.st_mtime),
        "packages": [],
        "python": "2.7",
        "size": testing_st.st_size,
        "platform": "rh5-64",
    }
    if 'python_tag' in kwargs:
        metadata.pop('python')
    metadata.update(kwargs)

    metadata_json = json.dumps(metadata).encode('utf-8')
    if md5 is None:
        md5 = hashlib.md5(metadata_json).hexdigest()
    if sha256 is None:
        sha256 = hashlib.sha256(metadata_json).hexdigest()

    metadata['md5'] = md5
    metadata['sha256'] = sha256

    return metadata


class TestingEgg(object):
    """Dumb container to package up the path to a generated testing egg with
    its metadata, and actual md5 and sha256.

    """

    def __init__(self, path, filename, md5, sha256, metadata):
        self.path = path
        self.filename = filename
        self.md5 = md5
        self.sha256 = sha256
        self.metadata = metadata

    def __getattr__(self, name):
        if name in self.metadata:
            return self.metadata[name]
        raise AttributeError(name)

    @property
    def index_entry(self):
        return legacy_index_entry_from_egg_metadata(self.metadata)

    @property
    def packages(self):
        return self.metadata['packages'][:]

    @property
    def python(self):
        python = self.metadata.get('python', NotGiven)
        if python is NotGiven:
            raise AttributeError('python')
        return python

    @property
    def python_tag(self):
        python_tag = self.metadata.get('python_tag', NotGiven)
        if python_tag is not NotGiven:
            return python_tag
        try:
            return python_tag_from_metadata(self.metadata)
        except KeyError:
            raise AttributeError('python_tag')

    @property
    def key(self):
        return self.filename

    @property
    def full_version(self):
        return '{0}-{1}'.format(self.version, self.build)

    @property
    def egg_basename(self):
        return self.filename.split('-')[0]

    def __eq__(self, other):
        if not isinstance(other, TestingEgg):
            return NotImplemented
        return self.metadata == other.metadata

    def __ne__(self, other):
        return not (self == other)


def build_egg(metadata, content, dest_dir):
    from okonomiyaki.file_formats import (
        Dependencies, EggBuilder, EggMetadata as OkonomiyakiEggMetadata,
        PackageInfo, Requirement)
    from okonomiyaki.platforms import EPDPlatform
    from okonomiyaki.versions import EnpkgVersion

    dependencies = Dependencies(
        (Requirement.from_spec_string(package)
         for package in metadata.get('packages', [])),
    )

    python_tag = python_tag_from_metadata(metadata)
    abi_tag = metadata.get('abi_tag', NotGiven)
    platform = EPDPlatform.from_epd_string(metadata['platform'])
    version = EnpkgVersion.from_upstream_and_build(metadata['version'],
                                                   metadata['build'])

    pkg_info = PackageInfo("1.1", metadata['name'], str(version.upstream))

    metadata_version_str = metadata.get("metadata_version")
    if metadata_version_str:
        metadata_version = MetadataVersion.from_string(metadata_version_str)
    else:
        metadata_version = EggMetadata.MAX_METADATA_VERSION

    dummy_metadata = OkonomiyakiEggMetadata.from_egg(DUMMY_EGG)
    metadata = OkonomiyakiEggMetadata.from_egg_metadata(
        dummy_metadata,
        raw_name=metadata['name'],
        version=version,
        platform=platform,
        python=(python_tag if python_tag is not NotGiven else None),
        abi_tag=(abi_tag if abi_tag is not NotGiven else None),
        dependencies=dependencies,
        pkg_info=pkg_info,
        summary="",
        metadata_version=metadata_version,
    )
    with EggBuilder(metadata, cwd=dest_dir) as builder:
        builder.add_iterator(content.items())
    return builder.path


def make_testing_egg(dest_dir, egg_basename=None, **kwargs):
    """Create a testing egg file.

    Paramaters
    ----------
    dest_dir : str
        The name of the directory where the egg will be created.

    In addition to the above, this accepts all parameters of
    :function:`.make_testing_egg_metadata`.

    Returns
    -------
    testing_egg : TestingEgg
        A container containing the path to the egg file and its
        metadata.

    """
    from hatcher.core.utils import compute_md5, compute_sha256
    metadata = make_testing_egg_metadata(**kwargs)
    egg_path = build_egg(metadata, {}, dest_dir)

    if egg_basename is not None:
        dirname = os.path.dirname(egg_path)
        basename = os.path.basename(egg_path)
        _, rest = basename.split('-', 1)
        new_basename = '{0}-{1}'.format(egg_basename, rest)
        new_path = os.path.join(dirname, new_basename)
        os.rename(egg_path, new_path)
        egg_path = new_path

    st = os.stat(egg_path)
    md5 = compute_md5(egg_path)
    sha256 = compute_sha256(egg_path)
    metadata['md5'] = md5
    metadata['sha256'] = sha256
    metadata['size'] = st.st_size
    metadata['mtime'] = round(st.st_mtime)
    filename = os.path.basename(egg_path)
    return TestingEgg(egg_path, filename, md5, sha256, metadata)


def runtime_from_metadata(tempdir, metadata_dict):
    metadata = PythonRuntimeMetadataV1._from_json_dict(metadata_dict)
    path = os.path.join(tempdir, metadata.filename)
    with zipfile2.ZipFile(path, 'w') as zp:
        metadata_str = json.dumps(metadata_dict)
        zp.writestr(_METADATA_ARCNAME, metadata_str.encode('utf-8'))
    return path
