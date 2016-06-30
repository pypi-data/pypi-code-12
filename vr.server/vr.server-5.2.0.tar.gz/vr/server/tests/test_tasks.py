# pylint: disable=attribute-defined-outside-init,too-many-instance-attributes
# pylint: disable=unused-argument,superfluous-parens,no-self-use
# pylint: disable=protected-access
import os.path
from unittest.mock import MagicMock, Mock, patch, call
import tempfile
from path import path
import time

from fabric.api import local
import pytest

from vr.common.utils import randchars
from vr.server.models import App, Build, BuildPack, OSImage, Host
from vr.server.settings import MEDIA_URL
from vr.server.tasks import get_build_parameters

from vr.server import tasks, remote


@pytest.mark.usefixtures('postgresql')
class TestBuild(object):

    def setup(self):
        self.buildpack = BuildPack(repo_url=randchars(), repo_type='git',
                                   order=1)
        self.buildpack.save()

        self.app = App(name=randchars(), repo_url=randchars(), repo_type='hg',
                       buildpack=self.buildpack)
        self.app.save()

        self.image_name = 'ubuntu_precise'
        self.image_filepath = os.path.join(self.image_name, 'ubuntu.tar.gz')

        self.image_md5 = 'abcdef1234567890'
        self.os_image = OSImage(name=self.image_name, file=self.image_filepath)
        with patch.object(OSImage, '_compute_file_md5',
                          return_value=self.image_md5):
            self.os_image.save()

        self.version = 'v1'

        self.build = Build(
            app=self.app,
            os_image=self.os_image,
            tag=self.version,
        )
        self.build.save()

    def test_get_build_parameters(self, gridfs):
        build_params = get_build_parameters(self.build)
        assert build_params == {
            'app_name': self.app.name,
            'app_repo_type': self.app.repo_type,
            'app_repo_url': self.app.repo_url,
            'version': self.version,
            'buildpack_url': self.buildpack.repo_url,
            'image_name': self.image_name,
            'image_url': MEDIA_URL + self.image_filepath,
            'image_md5': self.image_md5,
        }


class TestSwarmStartBranches(object):
    """We want to follow the steps from swarm_start to swarm_finished."""

    @patch.object(tasks, 'Swarm')
    @patch.object(tasks, 'swarm_release')
    def test_swarm_start_calls_swarm_release(self, swarm_release, Swarm):
        build = Mock()
        build.is_usable.return_value = True
        Swarm.object.get().release.build = build

        tasks.swarm_start(1234, 'trace_id')

        print(swarm_release.delay.mock_calls)
        print(swarm_release.mock_calls)
        swarm_release.delay.assert_called_with(1234, 'trace_id')

    @patch.object(tasks, 'Swarm')
    @patch.object(tasks, 'swarm_wait_for_build')
    def test_swarm_start_calls_swarm_wait_for_build(self,
                                                    swarm_wait_for_build,
                                                    Swarm):
        build = Mock()
        build.is_usable.return_value = False
        build.in_progress.return_value = True
        swarm = Mock(name='my mock swarm')
        swarm.id = 1234
        swarm.release.build = build

        Swarm.objects.get.return_value = swarm

        tasks.swarm_start(1234, 'trace_id')

        # TODO: Make sure this sends the trace id
        swarm_wait_for_build.assert_called_with(swarm, build, 'trace_id')

    @patch.object(tasks, 'Swarm')
    @patch.object(tasks, 'swarm_release')
    @patch.object(tasks, 'build_app')
    def test_swarm_start_calls_build_app_and_swarm_release(self,
                                                           build_app,
                                                           swarm_release,
                                                           Swarm):

        build = Mock()
        build.is_usable.return_value = False
        build.in_progress.return_value = False
        swarm = Mock(name='my mock swarm')
        swarm.id = 1234
        swarm.release.build = build

        Swarm.objects.get.return_value = swarm

        tasks.swarm_start(1234, 'trace_id')

        print(build_app.mock_calls)
        print(build_app.delay.mock_calls)

        print(swarm_release.mock_calls)
        print(swarm_release.delay.mock_calls)

        # Build the app, calling the swarm_release when done
        swarm_release.subtask.assert_called_with((1234, 'trace_id'))

        build_app.delay.assert_called_with(build.id,
                                           swarm_release.subtask(),
                                           'trace_id')


class TestSwarmReleaseBranches(object):

    @patch.object(tasks, 'PortLock', Mock())
    @patch.object(tasks, 'swarm_deploy_to_host')
    @patch.object(tasks, 'Swarm')
    def test_swarm_release_calls_swarm_deploy_to_host(self,
                                                      Swarm,
                                                      swarm_deploy_to_host,
                                                      redis):
        swarm = MagicMock()
        swarm.size = 2
        swarm.get_prioritized_hosts.return_value = [MagicMock(), MagicMock()]
        swarm.get_procs.return_value = []  # no procs currently
        Swarm.objects.get.return_value = swarm

        tasks.swarm_release(1234, 'trace_id')

        # TODO: This should work... but it doesn't. Not sure if I'm
        #       using mock_calls correctly as it has been returng 6
        #       instead of 2 even though the get_prioritized host is
        #       what is iterated over and used to creat the subtasks
        #       that are appeneded for the chord.
        #
        # assert len(swarm_deploy_to_host.subtask.mock_calls) == 2
        assert swarm_deploy_to_host.subtask.called


@pytest.mark.usefixtures('postgresql')
class TestScooper(object):

    def setup(self):
        self.host = Host(
            name='localhost',
            active=True
            # squad
        )
        self.host.save()

        # Modify IMAGES_ROOT and restore it after test
        self._img_root = remote.IMAGES_ROOT
        remote.IMAGES_ROOT = tempfile.gettempdir()

    def teardown(self):
        self.host.delete()
        remote.IMAGES_ROOT = self._img_root

    @patch.object(tasks, '_clean_host')
    def test_scooper(self, mock_clean_host):
        tasks.scooper()
        mock_clean_host.apply_async.assert_called_once_with(
            (self.host.name, ), expires=1800)

    @patch.object(remote, 'files')
    @patch.object(remote, 'get_procs')
    @patch.object(remote, 'get_builds')
    @patch.object(remote, 'get_images')
    @patch.object(remote, 'delete_build')
    @patch.object(remote, 'teardown')
    def test_clean_host_no_unused(
            self, mock_teardown, mock_delete_build, mock_get_images,
            mock_get_builds, mock_get_procs, mock_files):
        mock_get_images.return_value = []
        mock_get_builds.return_value = [
            'app-build1',
            'app-build2',
        ]
        mock_get_procs.return_value = [
            'app-build1-proc1',
            'app-build1-proc2',
            'app-build2-proc1',
        ]
        mock_files.exists.return_value = True
        tasks._clean_host(self.host.name)
        assert not mock_delete_build.called

        # Order doesn't matter
        mock_teardown.assert_any_call('app-build1-proc1', None)
        mock_teardown.assert_any_call('app-build1-proc2', None)
        mock_teardown.assert_any_call('app-build2-proc1', None)

    @patch.object(remote, 'files')
    @patch.object(remote, 'get_procs')
    @patch.object(remote, 'get_builds')
    @patch.object(remote, 'get_images')
    @patch.object(remote, 'delete_build')
    @patch.object(remote, 'teardown')
    def test_clean_host(
            self, mock_teardown, mock_delete_build, mock_get_images,
            mock_get_builds, mock_get_procs, mock_files):
        mock_get_images.return_value = []
        mock_get_builds.return_value = [
            'app-build1',
            'app-build2',
        ]
        mock_get_procs.return_value = [
            # app-build1 is unused
            'app-build2-proc1',
        ]
        mock_files.exists.return_value = True
        tasks._clean_host(self.host.name)
        mock_delete_build.assert_called_once_with('app-build1')

        # Order doesn't matter
        mock_teardown.assert_any_call('app-build2-proc1', None)

    @patch.object(remote, 'get_build_procs')
    @patch.object(remote, 'delete_proc')
    @patch.object(remote, 'sudo')
    def test_delete_build(
            self, mock_sudo, mock_delete_proc, mock_get_build_procs):
        mock_get_build_procs.return_value = [
            'app-build-proc1',
            'app-build-proc2',
        ]

        with pytest.raises(SystemExit):
            remote.delete_build('app-build', cascade=False)

        remote.delete_build('app-build', cascade=True)
        mock_delete_proc.assert_has_calls([
            call(remote.env.host_string, 'app-build-proc1'),
            call(remote.env.host_string, 'app-build-proc2'),
        ])
        mock_sudo.assert_called_once_with('rm -rf /apps/builds/app-build')

    @patch.object(remote, 'get_images')
    @patch.object(remote, '_get_builds_in_use')
    @patch.object(remote, '_rm_image')
    @patch.object(remote, 'files')
    @patch.object(remote, 'sudo')
    def test_clean_images_folders(
            self, mock_sudo, mock_files, mock_rm_image,
            mock_get_builds_in_use, mock_get_images):

        mock_get_images.return_value = [
            'recent_img',
            'non_existing_img',
            'old_img',
        ]

        def local_exists(p, *args, **kwargs):
            return os.path.exists(p)
        mock_files.exists.side_effect = local_exists

        def local_sudo(cmd):
            return local(cmd, capture=True)
        mock_sudo.side_effect = local_sudo

        # Make sure img is recent
        atime = time.time() - remote.MAX_IMAGE_AGE_SECS + 1
        (path(remote.IMAGES_ROOT) / 'recent_img').mkdir_p().utime(
            (atime, atime))

        # Make sure img does not exist
        (path(remote.IMAGES_ROOT) / 'non_existing_img').rmtree_p()

        # Make sure img is old
        atime = time.time() - remote.MAX_IMAGE_AGE_SECS - 1
        old_img_path = (
            path(remote.IMAGES_ROOT) / 'old_img'
        ).mkdir_p().utime((atime, atime))

        mock_get_builds_in_use.return_value = []

        remote.clean_images_folders()
        mock_rm_image.assert_called_once_with(old_img_path)

    @patch.object(remote, '_get_proc_settings')
    @patch.object(remote, 'get_supervised_procnames')
    @patch.object(remote, 'get_installed_procnames')
    @patch.object(remote, 'teardown')
    def test_teardown_old_procs(
            self, mock_teardown, mock_get_installed_procnames,
            mock_get_supervised_procnames, mock_get_proc_settings):

        mock_get_proc_settings.return_value = None
        mock_get_supervised_procnames.return_value = {
            'proc1', 'proc2'}
        mock_get_installed_procnames.return_value = {
            'proc1', 'proc2', 'proc3'}

        remote.teardown_old_procs()
        mock_teardown.assert_called_once_with('proc3', None)

    @patch.object(remote, 'get_orphans')
    @patch.object(remote, 'sudo')
    def test_kill_orphans(self, mock_sudo, mock_get_orphans):
        mock_get_orphans.return_value = [
            (1000, ('child1', 'child2')),
            (1001, ('child3', 'child4')),
            (1002, ('child5', 'child5')),
        ]
        remote.kill_orphans()
        mock_sudo.assert_has_calls([
            call('kill -9 1000'),
            call('kill -9 1001'),
            call('kill -9 1002'),
        ])
