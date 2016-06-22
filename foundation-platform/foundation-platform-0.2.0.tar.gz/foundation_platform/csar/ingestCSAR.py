#!/usr/bin/python
from __future__ import print_function
import argparse
from foundation_platform.messaging import image
import logging
import os
import platform
import socket
import sys
import wget
import zipfile

if sys.version_info >= (3,):
    import urllib.parse as urlparse
else:
    import urlparse


class ingestCSAR(object):

    def __init__(self):
        # input paramters
        self.inputCsarFile = ''
        self.inputCsarURL = ''
        self.hostAddr = socket.gethostbyname(socket.gethostname())
        self.hostName = socket.gethostname()

        # output parameters
        self.htmlDir = '/var/www/html'
        self.csarsFolder = 'csar'

        # logging
        self.logfile = 'ingestCSAR.log'
        self.loglevel = 'INFO'

        self.csarsDir = ''
        self.csarMap = {'image': 'images/',
                        'script': 'scripts/',
                        'hot': 'hot-templates/',
                        }

    def validate_args(self):
        try:
            usage = ('%(prog)s --host "This host\'s IP or FQDN" '
                     '--csar "full or relative CSAR file path" | '
                     '--url "Fully qualify destination name to access the csar package" '
                     '[optional arguments]')

            parser = argparse.ArgumentParser(
                formatter_class=argparse.RawDescriptionHelpFormatter,
                description='ingestCSAR: ingest CSAR package and load application files',
                usage=usage)
            parser.add_argument("--host",
                                dest="hostAddr", default=self.hostAddr,
                                help="This VM's IP or FQDN for web access",
                                required=False)
            parser.add_argument("--csar",
                                dest="inputCsarFile", default=self.inputCsarFile,
                                help='full or relative CSAR file path',
                                required=False)
            parser.add_argument("--url",
                                dest="inputCsarURL", default=self.inputCsarURL,
                                help='Fully qualify destination name to access the csar package',
                                required=False)
            parser.add_argument("--wwwDir",
                                dest="htmlDir", default=self.htmlDir,
                                help='www directory (/var/www/html)',
                                required=False)
            parser.add_argument("--output",
                                dest="csarsFolder", default=self.csarsFolder,
                                help='csar output folder in the www directory',
                                required=False)
            parser.add_argument("--other",
                                help='Input for any other file name / names separated by comma',
                                required=False)
            parser.add_argument("--log",
                                dest="loglevel", default=self.loglevel,
                                help="logging level (--log INFO, --log DEBUG)",
                                required=False)
            parser.add_argument("--logfile",
                                dest="logfile", default=self.logfile,
                                help="logging file [default: %(default)s]",
                                required=False)

            # Process arguments
            args = parser.parse_args()

            loglevel = args.loglevel
            numeric_level = getattr(logging, loglevel.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % loglevel)
            logfile = args.logfile

            if os.path.isfile(logfile):
                try:
                    os.remove(logfile)
                except Exception as rme:
                    logging.warning('-validate_args: ' + repr(rme) + '\n')
                    # just pass it, nothing to do
                    pass

            logging.basicConfig(filename=logfile,
                                format='%(asctime)s: %(levelname)s: %(message)s',
                                level=numeric_level)

            self.inputCsarFile = args.inputCsarFile
            self.inputCsarURL = args.inputCsarURL
            logging.info('input: csar=' + self.inputCsarFile + '  url=' + self.inputCsarURL)

            self.hostAddr = args.hostAddr
            logging.info('input: hostAddr=' + self.hostAddr)

            if self.inputCsarFile == '' and self.inputCsarURL == '' or self.hostAddr == '':
                parser.print_help()
                sys.exit(-1)

            self.htmlDir = args.htmlDir
            self.csarsFolder = args.csarsFolder
            self.csarsDir = self.htmlDir + '/' + self.csarsFolder + '/'
            logging.info('CSAR output directory: ' + self.csarsDir)
            self.createFolder(self.htmlDir, self.csarsFolder)

        except Exception as e:
            logging.critical('-validate_args: ' + repr(e) + '\n')
            raise e

    def ping(self, host):
        # Returns True if host responds to a ping request

        # Ping parameters as function of OS
        ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"

        # Ping
        return os.system("ping " + ping_str + " " + host) == 0

    def validate_inputs(self):
        downloadCsar = False
        if self.inputCsarFile != '':
            # check csar file
            if not os.path.isfile(self.inputCsarFile):
                raise ValueError("can't find CSAR zip file: " + self.inputCsarFile)
            if not zipfile.is_zipfile(self.inputCsarFile):
                raise ValueError("The " + self.inputCsarFile + " is NOT a proper zip file")
        elif self.inputCsarURL != '':
            # no csar file provided, check csar URL

            hostname = os.path.basename(urlparse.urlparse(self.inputCsarURL).hostname) or ''
            logging.info('CSAR hostname extracted: ' + hostname)
            if hostname == '':
                raise ValueError("Cannot get hostname from csar URL " + self.inputCsarURL)
            elif not self.ping(hostname):
                raise ValueError("Cannot get reach host " + hostname +
                                 " to retrieve csar package.  csar URL: " + self.inputCsarURL)
            downloadCsar = True

        if not self.ping(self.hostAddr):
            raise ValueError('ERROR: cannot ping host ' + self.hostAddr)

        return downloadCsar

    def createFolder(self, path, folderName):
        fullPath = path + "/" + folderName
        try:
            if os.path.isdir(fullPath):
                logging.info('CSAR directory ' + fullPath + ' already exist.')
                return

            logging.info("Creating " + folderName + " under " + path)
            try:
                os.makedirs(fullPath)
            except IOError:
                logging.warning("Can't create the folder " + fullPath)
        except IOError:
            logging.warning("Can't create the folder " + fullPath)
            pass

    def upload_files(self, csarDir, csarName):
        '''For the now, we'll push:

            all image file in the image directory
            all hot/env files in hot-template directory
            all script files in the scripts directory

        In the future we may need to be more selective by parsing through
            either the TOSCA.meta or an xml file to upload the selected files

        '''

        for key in self.csarMap:
            dirPath = csarDir + self.csarMap[key]
            files = os.listdir(dirPath)
            for file in files:
                logging.info('Uploading ' + key + ' file ' + file)
                fileUrl = ('http://' + self.hostAddr + '/' +
                           self.csarsFolder + '/' + csarName + '/' +
                           self.csarMap[key] + file)
                logging.info('file URL ' + fileUrl)

                if key == 'image':
                    imageName = os.path.splitext(file)[0]
                    data_set = {'url': fileUrl, 'name': imageName, 'ip': self.hostAddr}
                    logging.info('data set to push' + str(data_set))
                    image.imageHandler(data_set)

    def ingest(self):
        try:
            self.validate_args()
            if self.validate_inputs():
                # if return True it means that the file needs to be download
                os.chdir(self.csarsDir)
                self.inputCsarFile = wget.download(self.inputCsarURL)

            # create a CSAR directory for extraction
            csarName = os.path.splitext(self.inputCsarFile)[0]
            logging.info('Creating ' + csarName + ' under ' + self.csarsDir +
                         ' for CSAR extraction')
            self.createFolder(self.csarsDir, csarName)
            csarDir = self.csarsDir + csarName + '/'

            # extracting csar package
            csar = zipfile.ZipFile(self.inputCsarFile)
            csar.extractall(csarDir)

            self.upload_files(csarDir, csarName)

        except Exception as e:
            print(repr(e))
            logging.critical('-main: ' + repr(e) + '\n')
            return 0


if __name__ == '__main__':
    try:
        ingest = ingestCSAR()
        ingest.ingest()

    except Exception as e:
        logging.critical('-__main__: ' + repr(e) + '\n')
