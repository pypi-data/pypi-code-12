import os
import shutil
import socketserver
import tempfile
import threading
import unittest
import http.server

from bgdata import DatasetError, Downloader, DEVELOP, LATEST


class DownloaderTest(unittest.TestCase):

    def test_singlefile(self):
        try:
            dataset_file = DOWNLOADER.get_path(
                project='test', dataset='singlefile', version='1.0', build='20150720'
            )

            self.assertFirstLine(dataset_file, "HELLO WORLD")
            print("Single file test [OK]")

        except DatasetError as e:
            raise e

    def test_latest(self):
        try:
            dataset_file = DOWNLOADER.get_path(
                project='test', dataset='singlefile', version='1.0', build=LATEST
            )

            self.assertTrue(DOWNLOADER.is_downloaded(
                project='test', dataset='singlefile', version='1.0', build='20150721'
            ))
            print("Single file test [OK]")

        except DatasetError as e:
            raise e

    def test_is_downloaded(self):
        try:

            # Check if it's downloaded
            dataset_not_downloaded = DOWNLOADER.is_downloaded(
                project='test', dataset='checkdownloaded', version='1.0', build='20150720'
            )

            # Assert not downloaded
            self.assertFalse(dataset_not_downloaded)

            # Download it
            _ = DOWNLOADER.get_path(
                project='test', dataset='checkdownloaded', version='1.0', build='20150720'
            )

            # Assert is_downloaded returns True
            self.assertTrue(DOWNLOADER.is_downloaded(
                project='test', dataset='checkdownloaded', version='1.0', build='20150720'
            ))

            print("Is downloaded test [OK]")

        except DatasetError as e:
            raise e

    def test_folder(self):
        try:
            dataset_path = DOWNLOADER.get_path(project='test', dataset='folder', version='1.0', build='20150720')
            self.assertTrue(os.path.isdir(dataset_path))
            print("Folder test [OK]")
        except DatasetError:
            pass

    def test_development(self):
        try:
            dataset_file = DOWNLOADER.get_path(project='test', dataset='singlefile', version='1.0', build=DEVELOP)
            self.assertFirstLine(dataset_file, "HELLO DEVELOPER")
            print("Development test [OK]")

        except DatasetError as e:
            raise e

    def test_dataset_not_found(self):

        try:
            dataset_file = DOWNLOADER.get_path(project='test', dataset='notfound', version='1.0', build=DEVELOP)
            self.assertTrue(False)
        except DatasetError as e:
            self.assertTrue(e.type == DatasetError.NOT_FOUND)
            print("Dataset not found test [OK]")

    def assertFirstLine(self, file, content):
        with open(file, 'rt') as fd:
            lines = fd.readlines()
            self.assertEqual(content, lines[0].strip())


#
# Create a 'remote' repository at localhost to run tests
#

SERVER_PORT = 9797
SERVER = None
SERVER_THREAD = None
DOWNLOADER = None
REPO_LOCAL = None
REPO_REMOTE = None

def setUpModule():

    print("Setup module")
    global SERVER, SERVER_THREAD, DOWNLOADER, REPO_LOCAL, REPO_REMOTE

    # Use a local folder as a 'remote' repository
    REPO_REMOTE = "http://localhost:{}".format(SERVER_PORT)

    # Create a local repository
    REPO_LOCAL = tempfile.mkdtemp()

    # Create a downloader
    DOWNLOADER = Downloader(
        local_repository=REPO_LOCAL,
        remote_repository=REPO_REMOTE
    )

    # Start a HTTP server to serve the remote repository
    os.chdir(os.path.join(os.path.dirname(__file__), 'repository'))
    socketserver.TCPServer.allow_reuse_address = True
    SERVER = socketserver.TCPServer(("", SERVER_PORT), http.server.SimpleHTTPRequestHandler)
    SERVER_THREAD = threading.Thread(target=SERVER.serve_forever)
    SERVER_THREAD.start()


def tearDownModule():

    print("Tear down module")
    global SERVER, SERVER_THREAD, DOWNLOADER, REPO_LOCAL, REPO_REMOTE

    # Stop HTTP server
    SERVER.shutdown()
    SERVER.server_close()

    # Remove temporal local repository
    shutil.rmtree(REPO_LOCAL)

    # Wait server thread to finish
    SERVER_THREAD.join()

if __name__ == '__main__':
    unittest.main()