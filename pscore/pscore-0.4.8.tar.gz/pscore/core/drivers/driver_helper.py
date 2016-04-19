import os
import stat
import six
import zipfile
from os.path import expanduser
import requests

if six.PY34:
    import urllib.request
elif six.PY2:
    import urllib
else:
    raise ImportError('Correct urllib package not imported')


class DriverHelper(object):
    """Base class which has helper methods for downloading webdrivers  onto user's machines"""

    @staticmethod
    def download_destination(folder_name):
        homepath = expanduser("~")
        driver_path = os.path.join(homepath, folder_name)
        if not os.path.exists(driver_path):
            os.mkdir(driver_path)

        return driver_path

    @staticmethod
    def os_name():
        name = os.name
        if name is 'nt':
            return 'win'
        elif name is 'posix':
            return 'mac'
        else:
            raise NotImplemented("{} is not  supported yet".format(name))

    @staticmethod
    def get_download_folder(driver_folder):
        return DriverHelper.download_destination(driver_folder)

    @staticmethod
    def download_zip(url, zip_location):
        try:
            downloader = urllib.request
            downloader.urlretrieve(url, zip_location)
        except Exception as e:
            # Python 2.7.* approach
            downloader = urllib.URLopener()
            downloader.retrieve(url, zip_location)
            pass

    @staticmethod
    def zip_location(zipfoldername):
        destination = os.path.join(DriverHelper.download_destination(zipfoldername), 'download.zip')

        return destination

    @staticmethod
    def extract_zip(zipfoldername):
        if not os.path.exists(DriverHelper.zip_location(zipfoldername)):
            raise Exception('Driver zip not in expected location')

        with zipfile.ZipFile(DriverHelper.zip_location(zipfoldername), 'r') as driver_zip:
            driver_zip.extractall(
                    DriverHelper.download_destination(zipfoldername))

    @staticmethod
    def expected_file_name(driver):
        if driver == 'ie':
            return "IEDriverServer.exe"

        elif driver == 'chrome':
            if DriverHelper.os_name() is 'win':
                return 'chromedriver.exe'
            elif DriverHelper.os_name() is 'mac':
                return 'chromedriver'
            else:
                raise NotImplementedError()

    @staticmethod
    def set_exec_flag(drivername):
        """
        :param drivername:
        :return: None
        Sets the exec permission for driver for UNIX based systems
        """
        os.chmod(drivername, stat.S_IRWXU)


class IEDriverHelper(DriverHelper):
    """This class downloads the IE driver if it doesnt exist in the user's machine """
    IE_DRIVER_URL = "http://selenium-release.storage.googleapis.com/2.45/IEDriverServer_Win32_2.45.0.zip"
    DOWNLOAD_DESTINATION_FOLDER_NAME = '.iedriver'

    @staticmethod
    def get_ie_driver():
        expected_file = os.path.join(
                IEDriverHelper.get_download_folder(IEDriverHelper.DOWNLOAD_DESTINATION_FOLDER_NAME),
                IEDriverHelper.expected_file_name('ie'))
        if not os.path.exists(expected_file):
            IEDriverHelper.download_zip(IEDriverHelper.IE_DRIVER_URL,
                                        IEDriverHelper.zip_location(IEDriverHelper.DOWNLOAD_DESTINATION_FOLDER_NAME))
            IEDriverHelper.extract_zip(IEDriverHelper.DOWNLOAD_DESTINATION_FOLDER_NAME)

        return expected_file


class ChromeDriverHelper(DriverHelper):
    """This class downloads the Chrome driver if it doesnt exist in the user's machine """
    DOWNLOAD_DESTINATION_FOLDER_NAME = '.chromedriver'

    @staticmethod
    def _latest_chrome_version():
        r = requests.get('http://chromedriver.storage.googleapis.com/LATEST_RELEASE')
        return r.text.strip()

    @staticmethod
    def _download_url():
        url = 'http://chromedriver.storage.googleapis.com/{0}/chromedriver_{1}32.zip'.format(
                ChromeDriverHelper._latest_chrome_version(), DriverHelper.os_name())
        return url

    @staticmethod
    def get_chromedriver():
        expected_file = os.path.join(
                ChromeDriverHelper.download_destination(ChromeDriverHelper.DOWNLOAD_DESTINATION_FOLDER_NAME),
                ChromeDriverHelper.expected_file_name('chrome'))
        if not os.path.exists(expected_file):
            ChromeDriverHelper.download_zip(ChromeDriverHelper._download_url(), ChromeDriverHelper.zip_location(
                    ChromeDriverHelper.DOWNLOAD_DESTINATION_FOLDER_NAME))
            ChromeDriverHelper.extract_zip(ChromeDriverHelper.DOWNLOAD_DESTINATION_FOLDER_NAME)
            if ChromeDriverHelper.os_name() is 'mac':
                ChromeDriverHelper.set_exec_flag(expected_file)
                return expected_file

            return expected_file
        return expected_file
