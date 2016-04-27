# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : USGSDownload
Description          : Landsat Data download from earth explorer
Date                 : April, 2016
copyright            : (C) 2016 by Lucas Lamounier
email                : lucasls.oas@gmail.com
****************************************************************************/

Basic usage
****************************************************************************

    scene = SceneInfo('LC82280612016108LGN00')
    usgs = USGSDownload(scene, USER, PASSWORD)
    usgs.download(bands=['BQA', 4, 5, 6], download_dir=/home/user/landsat)

"""

import logging
import re
import requests
import sys
import tarfile
import time
import urllib
import urllib.error
import urllib.request
from math import floor
from os.path import join, expanduser, exists, getsize
from os import makedirs, remove, listdir

logger = logging.getLogger(__name__)

DOWNLOAD_DIR = join(expanduser('~'), 'landsat')


# Class base sceneInfo
class SceneInfo:
    """Extract information about scene from sceneName"""

    def __init__(self, sceneName):
        self.name = sceneName
        self.validate_name()
        self.path = sceneName[3:6]
        self.row = sceneName[6:9]
        self.prefix = sceneName[0:3]

    def validate_name(self):
        if len(self.name) != 21:
            raise WrongSceneNameError(self.name)

    def __repr__(self):
        return "Scene %s" % self.name


class USGSDownload:
    __satellitesMap = {
        'LT5': 'L5',
        'LE7': 'L7',
        'LC8': 'L8',
    }

    __remote_file_ext = '.tgz'

    def __init__(self, sceneInfo, user, password):
        if not isinstance(sceneInfo, SceneInfo):
            raise TypeError('sceneInfo must be instance of SceneInfo')

        self.sceneInfo = sceneInfo
        self.validate_sceneInfo()
        self.user = user
        self.password = password
        self.options_satellite = self.verify_type_product(self.__satellitesMap[sceneInfo.prefix])
        self.url = "http://earthexplorer.usgs.gov/download/%s/%s/STANDARD/EE" % (self.options_satellite['id_satelite'],
                                                                                 sceneInfo.name)
        if not self.remote_file_exists(self.url):
            raise RemoteFileDoesntExist('%s is not available on USGS Storage' % self.sceneInfo.name)

        if not user and not password or not user or not password:
            raise CredentialsUsgsError('Missing user and password !')

        print('\n', self.__repr__())
        logger.debug(self.__repr__())

    def validate_sceneInfo(self):
        """Check scene name and whether remote file exists. Raises
        WrongSceneNameError if the scene name is wrong.
        """
        if self.sceneInfo.prefix not in self.__satellitesMap:
            raise WrongSceneNameError('USGS Downloader: Prefix of %s (%s) is invalid'
                                      % (self.sceneInfo.name, self.sceneInfo.prefix))

    def remote_file_exists(self, url):
        """Check whether the remote file exists on Storage"""
        return requests.head(url).headers['Location'].find('error') == -1

    def verify_type_product(self, satellite):
        """Gets satellite id """
        if satellite == 'L5':
            id_satellite = '3119'
            stations = ['GLC', 'ASA', 'KIR', 'MOR', 'KHC', 'PAC', 'KIS', 'CHM', 'LGS', 'MGR', 'COA', 'MPS']
        elif satellite == 'L7':
            id_satellite = '3373'
            stations = ['EDC', 'SGS', 'AGS', 'ASN', 'SG1']
        elif satellite == 'L8':
            id_satellite = '4923'
            stations = ['LGN']
        else:
            raise ProductInvalidError('Type product invalid. the permitted types are: L5, L7, L8. ')
        typ_product = dict(id_satelite=id_satellite, stations=stations)
        return typ_product

    def get_remote_file_size(self, url):
        """Gets the filesize of a remote file """
        try:
            req = urllib.request.urlopen(url)
            return int(req.getheader('Content-Length').strip())
        except urllib.error.HTTPError as error:
            logger.error('Error retrieving size of the remote file %s' % error)
            print('Error retrieving size of the remote file %s' % error)
            self.connect_earthexplorer()
            self.get_remote_file_size(url)

    def download(self, bands=None, download_dir=None, metadata=False):
        """Download remote .tar.bz file."""
        if not download_dir:
            download_dir = DOWNLOAD_DIR

        if bands is None:
            bands = list(range(1, 12)) + ['BQA']
        else:
            self.validate_bands(bands)

        pattern = re.compile('^[^\s]+_(.+)\.tiff?', re.I)
        band_list = ['B%i' % (i,) if isinstance(i, int) else i for i in bands]
        image_list = []

        # Connect Earth explore
        self.connect_earthexplorer()

        # tgz name
        tgzname = self.sceneInfo.name + '.tgz'
        dest_dir = check_create_folder(join(download_dir, self.sceneInfo.name))

        # Download File
        downloaded = self.download_file(self.url, dest_dir, tgzname)

        # Log
        logger.debug('Status downloaded %s' % downloaded)
        print('\n Status downloaded %s' % downloaded)

        if downloaded['sucess']:

            # Log
            print('\n Downloaded sucess')
            logger.debug('Downloaded sucess of scene: %s' % self.sceneInfo.name)

            try:

                tar = tarfile.open(downloaded['file_path'], 'r')
                folder_path = join(download_dir, self.sceneInfo.name)
                tar.extractall(folder_path)
                remove(downloaded['file_path'])
                images_path = listdir(folder_path)

                for image_path in images_path:
                    matched = pattern.match(image_path)
                    file_path = join(folder_path, image_path)
                    if matched and matched.group(1) in band_list:
                        image_list.append([file_path, getsize(file_path)])
                    elif matched:
                        remove(file_path)
            except tarfile.ReadError as error:
                print('\nError when extracting files. %s' % error)
                logger.error('Error when extracting files. %s' % error)
            return image_list
        else:
            logger.debug('Info downloaded: %s' % downloaded)
            print('\n Info downloaded: %s' % downloaded)
            return downloaded

    @staticmethod
    def validate_bands(bands):
        """Validate bands parameter."""
        if not isinstance(bands, list):
            raise TypeError('Parameter bands must be a "list"')
        valid_bands = list(range(1, 12)) + ['BQA']
        for band in bands:
            if band not in valid_bands:
                raise InvalidBandError('%s is not a valid band' % band)

    def connect_earthexplorer(self):
        """   Connection to Earth explorer without proxy  """
        logger.info("Establishing connection to Earthexplorer")
        print("\n Establishing connection to Earthexplorer")
        try:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
            urllib.request.install_opener(opener)
            params = urllib.parse.urlencode(dict(username=self.user, password=self.password))
            params = params.encode('utf-8')
            f = opener.open("https://ers.cr.usgs.gov/login", params)
            data = f.read().decode('utf-8')
            f.close()
            if data.find(
                    'You must sign in as a registered user to download data or place orders for USGS EROS products') > 0:
                print("\n Authentification failed")
                logger.error("Authentification failed")
                raise AutenticationUSGSFailed('Authentification USGS failed')
            print('User %s connected with USGS' % self.user)
            logger.debug('User %s connected with USGS' % self.user)
            return
        except Exception as e:
            print('\nError when trying to connect USGS: %s' % e)
            raise logger.error('Error when trying to connect USGS: %s' % e)

    def download_file(self, url, download_dir, sceneName):
        """ Downloads large files in pieces   """
        try:
            # Log
            logger.info('\nStarting download..')
            print('\n Starting download..\n')

            # Request
            req = urllib.request.urlopen(url)

            try:
                if req.info().get_content_type() == 'text/html':
                    logger.error("error : the file format is html")
                    lines = req.read()
                    if lines.find('Download Not Found') > 0:
                        raise TypeError('Download USGS not found for scene: %s' % self.sceneInfo.name)
                    else:
                        print(lines)
                        print(sys.exit(-1))
            except Exception as e:
                logger.error('Erro in USGS download for scene %s error: %s' % (self.sceneInfo.name, e))
                raise CredentialsUsgsError('User or Password invalid ! ')

            total_size = int(req.getheader('Content-Length').strip())

            if total_size < 50000:
                logger.error("Error: The file is too small to be a Landsat Image for scene %s" % self.sceneInfo.name)
                raise SmallLandsatImageError("Error: The file is too small to be a Landsat Image")

            total_size_fmt = sizeof_fmt(total_size)
            downloaded = 0
            CHUNK = 1024 * 1024 * 8
            with open(download_dir + '/' + sceneName, 'wb') as fp:
                start = time.clock()
                logger.debug('Downloading {0} ({1}):'.format(self.sceneInfo.name, total_size_fmt))
                print('Downloading {0} ({1}):'.format(self.sceneInfo.name, total_size_fmt))
                while True:
                    chunk = req.read(CHUNK)
                    downloaded += len(chunk)
                    done = int(50 * downloaded / total_size)
                    print('\r[{1}{2}]{0:3.0f}% {3}ps'.format(floor((float(downloaded) / total_size) * 100), '-' * done,
                                                             ' ' * (50 - done), sizeof_fmt((downloaded //
                                                                                          (time.clock() - start)) / 8)))
                    if not chunk:
                        logger.debug('Download {0} completed({1}):'.format(self.sceneInfo.name, total_size_fmt))
                        break
                    fp.write(chunk)
        except urllib.error.HTTPError as e:
            if e.code == 500:
                logger.error("File doesn't exist")
                print("\n File doesn't exist: %s " % e)
                raise RemoteFileDoesntExist("File doesn't exist")
            elif e.code == 403:
                # Log celery
                logger.error("HTTP Error:", e.code, url)
                logger.debug('\n trying to download it again scene: %s' % self.sceneInfo.name)
                # Log shell
                print("\n HTTP Error:", e.code, url)
                print('\n trying to download it again scene: %s' % self.sceneInfo.name)
                self.connect_earthexplorer()
                self.download_file(url, download_dir, sceneName)
            else:
                logger.error("HTTP Error:", e)
                print("HTTP Error:", e.code, url)
                raise e
        except urllib.error.URLError as e:
            print("URL Error:", e.reason, url)
            logger.error("URL Error: %s in %s" % (e, url))
            raise e
        except ConnectionResetError as e:
            print('Error ConnectionResetError: %s' % e)
            logger.error('Error ConnectionResetError: %s' % e)
            print('\n trying to download it again scene: %s' % self.sceneInfo.name)
            logger.debug('trying to download it again scene: %s' % self.sceneInfo.name)
            self.download_file(url, download_dir, sceneName)
        except urllib.error.HTTPError as e:
            print('\n HttpError: %s' % e)
            print('\n trying to download it again scene: %s' % self.sceneInfo.name)
            logger.error('HttpError: %s' % e)
            logger.debug('trying to download it again scene: %s' % self.sceneInfo.name)
            self.download_file(url, download_dir, sceneName)
        except Exception as error:
            logger.error('Error unknown %s in download %s at scene: %s' % (error, url, self.sceneInfo.name))
            print('Error unknown %s in download % at scene: %s' % (error, url, self.sceneInfo.name))
            logger.debug('trying to download it again scene: %s' % self.sceneInfo.name)
            self.download_file(url, download_dir, sceneName)

        percent = floor((float(downloaded) / total_size) * 100) or 0
        if percent != 100:
            logger.debug('trying to download it again scene: %s' % self.sceneInfo.name)
            logger.error('Download interrupted in %s%%, trying to download it again scene: %s' % (
                percent, self.sceneInfo.name))
            print('\n Download interrupted in %s%%, trying to download it again scene: %s' % (
                percent, self.sceneInfo.name))
            self.download_file(url, download_dir, sceneName)

        path_item = download_dir + '/' + sceneName
        info = {'total_size': total_size_fmt, 'scene': self.sceneInfo.name,
                'sucess': verify_sucess(total_size, path_item), 'file_path': path_item}
        return info

    def __repr__(self):
        return "USGS Downloader (%s)" % self.sceneInfo


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def check_create_folder(folder_path):
    """Check whether a folder exists, if not the folder is created.
    Always return folder_path.
    """
    if not exists(folder_path):
        makedirs(folder_path)

    return folder_path


def verify_sucess(size_item, path_item):
    size = getsize(path_item)
    return size_item == size


class WrongSceneNameError(Exception):
    pass


class CredentialsUsgsError(Exception):
    pass


class AutenticationUSGSFailed(Exception):
    pass


class RemoteFileDoesntExist(Exception):
    pass


class SmallLandsatImageError(Exception):
    pass


class ProductInvalidError(Exception):
    pass


class InvalidBandError(Exception):
    pass