# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

import yaml

from okonomiyaki.file_formats import EggMetadata as OkonomiyakiEggMetadata

from hatcher.errors import MissingPlatformError
from ..url_templates import URLS
from ..utils import (
    EggMetadata, RuntimeMetadataV0, compute_sha256, upload_verify)


class SinglePlatformRepository(object):
    """A representation of a Brood repository for a single platform.

    """

    def __init__(self, repository, platform, url_handler, model_registry):
        """Create a SinglePlatformRepository.

        """
        self._repository = repository
        self.name = platform
        self._url_handler = url_handler
        self._model_registry = model_registry

    def __repr__(self):
        return (
            '<{cls} organization={organization!r}, '
            'repository={repository!r}, platform={platform!r}>'.format(
                cls=type(self).__name__,
                organization=self.organization_name,
                repository=self.repository_name,
                platform=self.name,
            )
        )

    @property
    def organization_name(self):
        return self._repository.organization_name

    @property
    def repository_name(self):
        return self._repository.name

    #### Eggs #################################################################

    def list_eggs(self, python_tag):
        """Return a list of all egg filenames in a repository.

        Parameters
        ----------
        python_tag : str
            The most specific Python tag of the runtime for which egg
            compatibility is desired.  This must reference a particular
            implementation and specific ``major.minor`` Python version
            (e.g. ``pp27`` or ``cp34``), not generic Python
            compatibility or any-version (e.g. ``py27`` or ``cp3``).

        Returns
        -------
        eggs : list
            List of dictionaries in the form
            ``{'name': egg_name, 'python_tag': python_tag}``

        """
        data = self.egg_index(python_tag)
        return [{'name': egg, 'python_tag': entry['python_tag']}
                for egg, entry in data.items()]

    def egg_index(self, python_tag):
        """Return a list of all egg filenames in a repository.

        Parameters
        ----------
        python_tag : str
            The most specific Python tag of the runtime for which egg
            compatibility is desired.  This must reference a particular
            implementation and specific ``major.minor`` Python version
            (e.g. ``pp27`` or ``cp34``), not generic Python
            compatibility or any-version (e.g. ``py27`` or ``cp3``).

        """
        path = URLS.v0.indices.eggs.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            python_tag=python_tag,
        )
        data = self._url_handler.get_json(path)
        return data

    def egg_metadata(self, python_tag, name, version):
        """Download the metadata for an egg.

        """
        path = self._egg_url(
            URLS.v0.metadata.artefacts.eggs, python_tag, name, version)
        return self._url_handler.get_json(path)

    def _download_egg(self, python_tag, name, version, destination,
                      download_file, expected_sha256):
        if expected_sha256 is None:
            metadata = self.egg_metadata(python_tag, name, version)
            expected_sha256 = metadata['sha256']

        path = self._egg_url(
            URLS.v0.data.eggs.download, python_tag, name, version)
        return download_file(
            path, destination, expected_sha256)

    def download_egg(self, python_tag, name, version, destination,
                     expected_sha256=None):
        """Download the egg specified by ``name``, ``version``, saving the
        resulting file in the ``destination`` directory.

        Parameters
        ----------
        python_tag : str
            The Python runtime compatibility of the egg, as defined in
            the ``Python Tag`` section of PEP425.
        name : str
            The name of the egg.
        version : str
            The full version specification of the egg.

        """
        self._download_egg(
            python_tag, name, version, destination,
            self._url_handler.download_file, expected_sha256=expected_sha256)

    def iter_download_egg(self, python_tag, name, version, destination,
                          expected_sha256=None):
        """Download the egg specified by ``name``, ``version``, saving the
        resulting file in the ``destination`` directory.

        This method returns a tuple of (content_length, iterator).  The
        ``content_length`` is the total size of the download.  The
        ``iterator`` yield the size of each chunk as it is downloaded.

        Parameters
        ----------
        python_tag : str
            The Python runtime compatibility of the egg, as defined in
            the ``Python Tag`` section of PEP425.
        name : str
            The name of the egg.
        version : str
            The full version specification of the egg.

        """
        return self._download_egg(
            python_tag, name, version, destination,
            self._url_handler.iter_download, expected_sha256=expected_sha256)

    def delete_egg(self, python_tag, name, version):
        """Delete an egg to the repository.

        Parameters
        ----------
        python_tag : str
            The Python runtime compatibility of the egg, as defined in
            the ``Python Tag`` section of PEP425.
        name : str
            The name of the egg.
        version : str
            The full version specification of the egg.

        """
        path = URLS.v0.data.eggs.delete.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            name=name,
            version=version,
            python_tag=python_tag,
        )
        return self._url_handler.delete(path)

    def upload_egg(self, filename, overwrite=False, enabled=True,
                   verify=False):
        """Upload an egg to the repository.

        """
        metadata = EggMetadata.from_file(filename)
        upload_metadata = {'sha256': metadata.sha256}
        path = URLS.v0.data.eggs.upload.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
        )

        def do_upload():
            self._url_handler.upload(
                path, upload_metadata, filename, overwrite=overwrite,
                enabled=enabled)

        def get_remote_metadata(local_metadata):
            return self.egg_metadata(
                local_metadata.python_tag, local_metadata.name,
                local_metadata.full_version)

        upload_verify(
            filename, metadata, get_remote_metadata, do_upload,
            verify=verify, overwrite=overwrite)

    def reindex(self, eggs_to_enable):
        """Enable indexing of the listed eggs and re-index the repository.

        Parameters
        ----------
        eggs_to_enable : list
            List of filenames of eggs to enable.

        """
        egg_specs = [
            OkonomiyakiEggMetadata.from_egg(egg) for egg in eggs_to_enable
        ]
        eggs_to_enable = set(
            (spec.name, spec.version, spec.python_tag_string)
            for spec in egg_specs)
        data = {
            'eggs': [
                {'name': name, 'version': str(version), 'python_tag': tag}
                for name, version, tag in eggs_to_enable
            ],
        }
        url = URLS.v0.data.eggs.re_index.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
        )
        self._url_handler.post(url, data)

    def _egg_url(self, base, python_tag, name, version):
        return base.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            name=name,
            version=version,
            python_tag=python_tag,
        )

    #### Apps #################################################################

    def list_apps(self):
        """List all apps in a repository.

        """
        index = self.app_index()

        apps = [(app, '{0}-{1}'.format(version, build), python_tag)
                for python_tag, apps in index.items()
                for app, versions in apps.items()
                for version, builds in versions.items()
                for build, metadata in builds.items()]

        return apps

    def app_index(self):
        """Get the index of all apps in the current repository

        """
        index_path = (
            URLS.v0.indices.apps.format(
                organization_name=self.organization_name,
                repository_name=self.repository_name,
                platform=self.name,
            )
        )

        return self._url_handler.get_json(index_path)

    def app_metadata(self, python_tag, app_id, version):
        """Download the metadata for an app.

        """
        path = URLS.v0.metadata.artefacts.apps.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            python_tag=python_tag,
            app_id=app_id,
            version=version,
        )
        return self._url_handler.get_json(path)

    #### Runtimes #############################################################

    def list_runtimes(self):
        """List all runtimes in a repository.

        """
        index = self.runtime_index()
        filenames = set(
            bdict['filename'] for language, ldict in index.items()
            for version, vdict in ldict.items()
            for build, bdict in vdict.items()
        )
        return list(filenames)

    def runtime_index(self):
        """Get the index of all the runtimes in the current repository

        """
        # FIXME: This works by downloading and parsing the index.  We
        # probably want to expose a list_runtimes endpoint in brood.
        index_path = URLS.v0.indices.runtimes.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
        )
        return self._url_handler.get_json(index_path)

    def runtime_metadata(self, python_tag, version):
        """Fetch the metadata for a runtime.

        """
        path = self._runtime_url(
            URLS.v0.metadata.artefacts.runtimes, python_tag, version)
        return self._url_handler.get_json(path)

    def _download_runtime(self, python_tag, version, destination,
                          download_file, expected_sha256):
        if expected_sha256 is None:
            metadata = self.runtime_metadata(python_tag, version)
            expected_sha256 = metadata['sha256']

        path = self._runtime_url(
            URLS.v0.data.runtimes.download, python_tag, version)
        return download_file(path, destination, expected_sha256)

    def download_runtime(self, python_tag, version, destination,
                         expected_sha256=None):
        """Download a runtime and save it in the given directory.

        """
        self._download_runtime(
            python_tag, version, destination, self._url_handler.download_file,
            expected_sha256)

    def iter_download_runtime(self, python_tag, version, destination,
                              expected_sha256=None):
        """Download a runtime and save it in the given directory.

        This method returns a tuple of (content_length, iterator).  The
        ``content_length`` is the total size of the download.  The
        ``iterator`` yield the size of each chunk as it is downloaded.

        """
        return self._download_runtime(
            python_tag, version, destination, self._url_handler.iter_download,
            expected_sha256)

    def _runtime_url(self, base, python_tag, version):
        return base.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            python_tag=python_tag,
            version=version,
        )


class Repository(object):
    """A representation of a Brood repository.

    A repository contains artefacts for multiple platforms.  The
    ``Repository`` provides an entry-point to all platform data.

    """

    def __init__(self, organization_name, name, url_handler, model_registry):
        """Create a Repository.

        """
        self.organization_name = organization_name
        self.name = name
        self._url_handler = url_handler
        self._model_registry = model_registry

    def __repr__(self):
        return (
            '<{cls} organization={organization!r}, '
            'repository={repository!r}>'.format(
                cls=type(self).__name__,
                organization=self.organization_name,
                repository=self.name,
            )
        )

    def __str__(self):
        return '{0}/{1}'.format(self.organization_name, self.name)

    def delete(self, force=False):
        """Delete this repository from Brood.

        """
        path = URLS.v0.admin.repositories.format(
            organization_name=self.organization_name,
            repository_name=self.name,
        )
        self._url_handler.delete(path, force=force)

    def metadata(self):
        """Get the metadata for this repository.

        """
        raise NotImplementedError('Not implemented in brood.')

    def list_platforms(self):
        """Return a list of the names of all platforms supported by this
        repository.

        """
        raise NotImplementedError('Not implemented in brood.')

    def platform(self, platform_name):
        """Create and return a :class:`~.SinglePlatformRepository` to access
        artefacts.

        """
        return self._model_registry.SinglePlatformRepository(
            repository=self,
            platform=platform_name,
            url_handler=self._url_handler,
            model_registry=self._model_registry,
        )

    # FIXME: This looks strange here, but the platform is specified in
    # metadata by the filename.
    def upload_runtime(self, filename, overwrite=False, verify=False):
        """Upload a runtime.

        """
        metadata = RuntimeMetadataV0.from_file(filename)
        metadata_dict = {
            'language': metadata.language,
            'filename': metadata.filename,
            'build_system_version': metadata.build_system_version,
            'version': metadata.version,
            'file_format': metadata.file_format,
            'build': metadata.build,
            'sha256': metadata.sha256,
        }
        path = URLS.v0.data.runtimes.upload.format(
            organization_name=self.organization_name,
            repository_name=self.name,
            platform=metadata.platform,
        )

        def do_upload():
            self._url_handler.upload(
                path, metadata_dict, filename, overwrite=overwrite)

        def get_remote_metadata(local_metadata):
            platform_repo = self.platform(local_metadata.platform)
            return platform_repo.runtime_metadata(
                local_metadata.python_tag, local_metadata.full_version)

        upload_verify(
            filename, metadata, get_remote_metadata, do_upload,
            verify=verify, overwrite=overwrite)

    # FIXME: This looks strange here, but the platform is internal to
    # the metadata file.
    def upload_app(self, filename, overwrite=False):
        """Upload an app specification.

        """
        with open(filename, 'r') as fh:
            yaml_data = yaml.safe_load(fh)

        platform = yaml_data.get('platform')
        if platform is None:
            raise MissingPlatformError(
                'App yaml does not contain a platform specification')
        path = URLS.v0.data.apps.upload.format(
            organization_name=self.organization_name,
            repository_name=self.name,
            platform=platform,
        )
        metadata = {
            'sha256': compute_sha256(filename),
        }
        self._url_handler.upload(path, metadata, filename, overwrite=overwrite)
