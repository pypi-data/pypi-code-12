from __future__ import absolute_import

import os
import requests
import threading
import logging
import hashlib
from bs4 import BeautifulSoup
from Queue import Queue

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

logger = logging.getLogger(__name__)

class PypiModuleSync(threading.Thread):

    def __init__(self, pypi_mirror_url, mirror_root, queue, verify=True, timeout=None):
        super(PypiModuleSync, self).__init__()
        self.daemon = True
        self.pypi_mirror_url = pypi_mirror_url
        self.mirror_root = mirror_root
        self.simple_directory = os.path.join(self.mirror_root, 'simple')
        #self.package_root = package_root
        self.session = requests.Session()
        self.queue = queue
        self.verify = verify
        self.timeout = timeout

    def download_package(self, current_url, current_dir, package):
        package_dir_ref = os.path.dirname(package)
        package_name = os.path.basename(package)
        package_location, package_md5sum = package_name.split('#')
        package_md5sum = package_md5sum.strip('md5=')
        package_dir = os.path.join(current_dir, package_dir_ref) 
        if not os.path.isdir(package_dir):
            os.makedirs(package_dir)
        #package_url = '{}/{}/{}'.format(current_url, package_dir_ref, package_location)
        package_url = urljoin(current_url + '/', package_dir_ref)
        package_url = '{}/{}'.format(package_url, package_location)
        logger.debug('Downloading %s', package_url)
        package_directory = os.path.join(current_dir, package_dir_ref)
        if not os.path.isdir(package_directory):
            os.makedirs(package_directory)
        package_file = os.path.join(package_directory, package_location)
        if os.path.exists(package_file):
            if md5sum(package_file) == package_md5sum:
                logger.info("File %s already exists", package_name)
                return
        logger.info("Syncing: %s", package_name)
        r = self.session.get(package_url, stream=True, verify=self.verify, timeout=self.timeout)
        if r.ok:
            with open(package_file, 'w') as fh:
                for chunk in r.iter_content(1024):
                    fh.write(chunk)

    def get_module(self, module_name):
        href_url = '{}/{}'.format(self.pypi_mirror_url, module_name)
        r = self.session.get(href_url, verify=self.verify, timeout=self.timeout)
        package_html = r.text
        module_simple_dir = os.path.join(self.simple_directory, module_name)
        if not os.path.isdir(module_simple_dir):
            os.makedirs(module_simple_dir)
        module_simple_file = os.path.join(module_simple_dir, 'index.html')
        with open(module_simple_file, 'w') as fh: 
            fh.write(package_html)
        package_soup = BeautifulSoup(package_html)
        for href in package_soup.find_all('a'):
            try:
                self.download_package(href_url, module_simple_dir, href.get('href'))
            except:
                logger.exception('Failed to download %s', module_name)

    def run(self):
        while True:
            module_name = self.queue.get()
            try:
                self.get_module(module_name)
            except:
                logger.exception('Failed to get %s', module_name)
            self.queue.task_done()

class PypiMirror(object):

    def __init__(self, mirror_root, pypi_mirror_url='http://pypi.python.org/simple', workers=3, verify=True, timeout=None):
        self.pypi_mirror_url = pypi_mirror_url
        self.mirror_root = mirror_root
        self.session = requests.Session()
        self.queue = Queue()
        self.workers = workers
        self.verify = verify
        self.timeout = timeout

    def get_simple_listing(self):
        r = self.session.get(self.pypi_mirror_url, verify=self.verify, timeout=self.timeout)
        simple_listing = r.text
        self.simple_directory = os.path.join(self.mirror_root, 'simple')
        if not os.path.isdir(self.simple_directory):
            os.makedirs(self.simple_directory)
        simple_file = os.path.join(self.simple_directory, 'index.html')
        with open(simple_file, 'w') as fh:
            fh.write(simple_listing)
        for worker in xrange(0, self.workers):
            t = PypiModuleSync(self.pypi_mirror_url, self.mirror_root, self.queue, verify=self.verify, timeout=self.timeout)
            t.start()
        self.parse_simple_listing(simple_listing)
        self.queue.join()

    def parse_simple_listing(self, simple_html):
        for line in simple_html.split('\n'):
            soup = BeautifulSoup(line)
            ahref = soup.a
            if ahref:
                module_name = ahref.get('href')
                self.queue.put(module_name)
                continue
