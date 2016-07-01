import tarfile
import tempfile
import urllib.parse
import urllib.request
from itertools import takewhile
from os import path, makedirs, listdir, chmod, rmdir, mkdir, remove
from platform import system
from re import sub, findall, MULTILINE
from shutil import move, copytree, copyfileobj, rmtree, make_archive
from subprocess import Popen
from sys import maxsize
from zipfile import ZipFile

import requests


class EclipseConfiguration(object):
  def __init__(self, os=None, ws=None, arch=None):
    if not os:
      os = self.__os()
    if not ws:
      ws = self.__ws(os)
    if not arch:
      arch = self.__arch()

    self.os = os
    self.ws = ws
    self.arch = arch

  @staticmethod
  def __os():
    sys = system()
    if sys == 'Darwin':
      return 'macosx'
    elif sys == 'Linux':
      return 'linux'
    elif sys == 'Windows':
      return 'win32'
    else:
      raise Exception('Unsupported OS {}'.format(system))

  @staticmethod
  def __ws(os):
    if os == 'macosx':
      return 'cocoa'
    elif os == 'linux':
      return 'gtk'
    elif os == 'win32':
      return 'win32'
    else:
      raise Exception('Unsupported Eclipse OS {}'.format(os))

  @staticmethod
  def __arch():
    is64Bits = maxsize > 2 ** 32
    if is64Bits:
      return 'x86_64'
    else:
      return 'x86'


class EclipseGenerator(object):
  def __init__(self, workingDir, destination, config=EclipseConfiguration(), repositories=None, installUnits=None,
      archive=False):
    if not installUnits:
      installUnits = []
    if not repositories:
      repositories = []

    self.workingDir = workingDir
    self.requestedDestination = destination
    if archive:
      self.tempdir = tempfile.TemporaryDirectory()
      self.destination = self.tempdir.name
    else:
      self.destination = destination
    if config.os == 'macosx':
      self.finalDestination = path.join(self.destination, 'Eclipse.app')
    else:
      self.finalDestination = self.destination
    self.config = config
    self.repositories = repositories
    self.installUnits = installUnits
    self.doArchive = archive

  def __enter__(self):
    return self

  def __exit__(self, **_):
    if self.doArchive:
      self.tempdir.cleanup()

  def generate(self, fixIni=True, addJre=False, archiveJreSeparately=False, archivePrefix='eclipse'):
    self.generate_eclipse()
    if fixIni:
      self.fix_ini()
    if self.doArchive and archiveJreSeparately and addJre:
      self.archive(archivePrefix, '')
    if addJre:
      self.add_jre()
    if self.doArchive:
      if archiveJreSeparately and addJre:
        self.archive(archivePrefix, '-jre')
      else:
        self.archive(archivePrefix, '')

  def generate_eclipse(self):
    director = self.__get_p2_director()
    args = [director]

    if len(self.repositories) != 0:
      mappedRepositories = map(self.__to_uri, self.repositories)
      args.extend(['-r {}'.format(repo) for repo in mappedRepositories]);

    args.extend(['-i {}'.format(iu) for iu in self.installUnits]);

    args.append('-tag InitialState')
    args.append('-destination {}'.format(self.finalDestination))
    args.append('-profile SDKProfile')
    args.append('-profileProperties "org.eclipse.update.install.features=true"')
    args.append('-p2.os {}'.format(self.config.os))
    args.append('-p2.ws {}'.format(self.config.ws))
    args.append('-p2.arch {}'.format(self.config.arch))
    args.append('-roaming')

    cmd = ' '.join(args)
    print(cmd)
    try:
      process = Popen(cmd, shell=True)
      process.communicate()
      if process.returncode != 0:
        raise RuntimeError("Eclipse generation failed")
    except KeyboardInterrupt:
      raise RuntimeError("Eclipse generation interrupted")

  def fix_ini(self, stackSize='16M', heapSize='1G', maxHeapSize='1G', maxPermGen='256M',
      requiredJavaVersion='1.8', server=True):
    iniLocation = self.__ini_location()

    # Python converts all line endings to '\n' when reading a file in text mode like this.
    with open(iniLocation, "r") as iniFile:
      iniText = iniFile.read()

    iniText = sub(r'--launcher\.XXMaxPermSize\n[0-9]+[gGmMkK]', '', iniText, flags=MULTILINE)
    iniText = sub(r'-install\n.+', '', iniText, flags=MULTILINE)
    iniText = sub(r'-showsplash\norg.eclipse.platform', '', iniText, flags=MULTILINE)

    launcherPattern = r'--launcher\.defaultAction\nopenFile'
    launcherMatches = len(findall(launcherPattern, iniText, flags=MULTILINE))
    if launcherMatches > 1:
      iniText = sub(launcherPattern, '', iniText, count=launcherMatches - 1, flags=MULTILINE)

    iniText = sub(r'-X(ms|ss|mx)[0-9]+[gGmMkK]', '', iniText)
    iniText = sub(r'-XX:MaxPermSize=[0-9]+[gGmMkK]', '', iniText)
    iniText = sub(r'-Dorg\.eclipse\.swt\.internal\.carbon\.smallFonts', '', iniText)
    iniText = sub(r'-XstartOnFirstThread', '', iniText)
    iniText = sub(r'-Dosgi.requiredJavaVersion=[0-9]\.[0-9]', '', iniText)
    iniText = sub(r'-server', '', iniText)

    iniText = '\n'.join([line for line in iniText.split('\n') if line.strip()]) + '\n'

    if self.config.os == 'macosx':
      iniText += '-XstartOnFirstThread\n'

    if stackSize:
      iniText += '-Xss{}\n'.format(stackSize)
    if heapSize:
      iniText += '-Xms{}\n'.format(heapSize)
    if maxHeapSize:
      iniText += '-Xmx{}\n'.format(maxHeapSize)
    if maxPermGen:
      iniText += '-XX:MaxPermSize={}\n'.format(maxPermGen)

    if requiredJavaVersion:
      iniText += '-Dosgi.requiredJavaVersion={}\n'.format(requiredJavaVersion)

    if server:
      iniText += '-server\n'

    print('Setting contents of {} to:\n{}'.format(iniLocation, iniText))
    with open(iniLocation, "w") as iniFile:
      iniFile.write(iniText)

  def add_jre(self):
    jrePath = self.__download_jre()
    targetJrePath = path.join(self.finalDestination, 'jre')
    if path.isdir(targetJrePath):
      rmtree(targetJrePath, ignore_errors=True)
    print('Copying JRE from {} to {}'.format(jrePath, targetJrePath))
    copytree(jrePath, targetJrePath, symlinks=True)

    relJreLocation = self.__jre_location()
    iniLocation = self.__ini_location()
    with open(iniLocation, 'r') as iniFile:
      iniText = iniFile.read()
    with open(iniLocation, 'w') as iniFile:
      print('Prepending VM location {} to eclipse.ini'.format(relJreLocation))
      iniText = sub(r'-vm\n.+\n', '', iniText, flags=MULTILINE)
      iniFile.write('-vm\n{}\n'.format(relJreLocation) + iniText)

  def archive(self, prefix='eclipse', postfix=''):
    name = '{}-{}-{}{}'.format(prefix, self.config.os, self.config.arch, postfix)
    print('Archiving Eclipse instance {}'.format(name))
    filename = path.join(self.requestedDestination, name)
    with tempfile.TemporaryDirectory() as tempdir:
      copytree(self.destination, path.join(tempdir, name), symlinks=True)
      if self.config.os == 'macosx' or self.config.os == 'linux':
        return make_archive(filename, format='gztar', root_dir=tempdir, base_dir=name)
      elif self.config.os == 'win32':
        return make_archive(filename, format='zip', root_dir=tempdir, base_dir=name)
      else:
        raise RuntimeError('Unsupported OS {}'.format(self.config.os))

  @staticmethod
  def __get_p2_director():
    if system() == 'Windows':
      executable = EclipseGenerator.__to_storage_location('director/director/director.bat')
    else:
      executable = EclipseGenerator.__to_storage_location('director/director/director')

    if path.isfile(executable):
      return executable

    url = 'http://eclipse.mirror.triple-it.nl/tools/buckminster/products/director_latest.zip'
    directorZipLoc = EclipseGenerator.__to_storage_location('director.zip')
    with urllib.request.urlopen(url) as response, open(directorZipLoc, 'wb') as outFile:
      print('Downloading director from {} to {}'.format(url, directorZipLoc))
      copyfileobj(response, outFile)
    with ZipFile(directorZipLoc) as zipFile:
      unpackLoc = EclipseGenerator.__to_storage_location('director')
      zipFile.extractall(path=unpackLoc)
    chmod(executable, 0o744)

    return executable

  def __to_uri(self, location):
    if location.startswith('http'):
      return location
    else:
      if not path.isabs(location):
        location = path.normpath(path.join(self.workingDir, location))
      return urllib.parse.urljoin('file:', urllib.request.pathname2url(location))

  def __download_jre(self):
    version = '8u92'
    build = 'b14'
    urlPrefix = 'http://download.oracle.com/otn-pub/java/jdk/{0}-{1}/jre-{0}-'.format(version, build)
    extension = 'tar.gz'

    if self.config.os == 'macosx':
      jreOS = 'macosx'
    elif self.config.os == 'linux':
      jreOS = 'linux'
    elif self.config.os == 'win32':
      jreOS = 'windows'
    else:
      raise RuntimeError('Unsupported JRE OS {}'.format(self.config.os))

    if self.config.arch == 'x86_64':
      jreArch = 'x64'
    elif self.config.arch == 'x86':
      jreArch = 'i586'
    else:
      raise RuntimeError('Unsupported JRE architecture {}'.format(self.config.arch))

    location = self.__to_storage_location(path.join('jre', version, build))
    makedirs(location, exist_ok=True)

    fileName = '{}-{}.{}'.format(jreOS, jreArch, extension)
    filePath = path.join(location, fileName)

    dirName = '{}-{}'.format(jreOS, jreArch)
    dirPath = path.join(location, dirName)

    if path.isdir(dirPath):
      return dirPath

    url = '{}{}'.format(urlPrefix, fileName)
    print('Downloading JRE from {}'.format(url))
    cookies = dict(gpw_e24='http%3A%2F%2Fwww.oracle.com%2F', oraclelicense='accept-securebackup-cookie')
    request = requests.get(url, cookies=cookies)
    with open(filePath, 'wb') as file:
      for chunk in request.iter_content(1024):
        file.write(chunk)

    print('Extracting JRE to {}'.format(dirPath))
    with tarfile.open(filePath, 'r') as tar:
      tar.extractall(path=dirPath)
      rootName = _common_prefix(tar.getnames())
      rootDir = path.join(dirPath, rootName)
      for name in listdir(rootDir):
        move(path.join(rootDir, name), path.join(dirPath, name))
      rmdir(rootDir)

    remove(filePath)

    return dirPath

  def __jre_location(self):
    if self.config.os == 'macosx':
      return '../../jre/Contents/Home/bin/java'
    elif self.config.os == 'linux':
      return 'jre/bin/java'
    elif self.config.os == 'win32':
      if self.config.arch == 'x86_64':
        return 'jre\\bin\\server\\jvm.dll'
      elif self.config.arch == 'x86':
        return 'jre\\bin\\client\\jvm.dll'
      else:
        raise RuntimeError('Unsupported Eclipse arch {}'.format(self.config.arch))
    else:
      raise RuntimeError('Unsupported Eclipse OS {}'.format(self.config.os))

  def __ini_location(self):
    if self.config.os == 'macosx':
      return '{}/Contents/Eclipse/eclipse.ini'.format(self.finalDestination)
    elif self.config.os == 'linux':
      return '{}/eclipse.ini'.format(self.destination)
    elif self.config.os == 'win32':
      return '{}/eclipse.ini'.format(self.destination)
    else:
      raise RuntimeError('Unsupported Eclipse OS {}'.format(self.config.os))

  @staticmethod
  def __to_storage_location(location):
    storageLocation = path.join(path.expanduser('~'), '.eclipsegen')
    if not path.isdir(storageLocation):
      mkdir(storageLocation)
    return path.join(storageLocation, location)


def _common_prefix(paths, sep='/'):
  """
  Finds the common path prefix in given list of paths.
  The os.path.commonprefix function is broken, since it finds prefixes on the character level, not the path level.
  From: http://rosettacode.org/wiki/Find_Common_Directory_Path#Python
  """
  byDirectoryLevels = zip(*[p.split(sep) for p in paths])

  def all_names_equal(name):
    return all(n == name[0] for n in name[1:])

  return sep.join(x[0] for x in takewhile(all_names_equal, byDirectoryLevels))
