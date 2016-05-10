import os
import zlib
from enum import Enum
from io import BytesIO

import requests

from ndb_adapter.ndb_base import NDBBase


class _Pdb(NDBBase):
    """Helper class for pdb file download

    :cvar Url: url to file ftp
    :cvar Ext: file extension
    :cvar UrlExt: url file extension
    :cvar PreName: url name prefix
    :cvar PostName: url name postfix
    """
    Url = NDBBase._chiralCorrectUrl
    Ext = ".ent"
    UrlExt = ".ent.gz"
    PreName = 'pdb'
    PostName = ''


class _PdbBioAssembly(NDBBase):
    """Helper class for pdb biological assembly file download"""
    Url = NDBBase._bioAssemblyCoordinateUrl
    Ext = ".pdb"
    UrlExt = ".pdb"
    PreName = ''
    PostName = ''


class _Cif(NDBBase):
    """Helper class for cif file download"""
    Url = NDBBase._mmCifUrl
    Ext = ".cif"
    UrlExt = ".cif.gz"
    PreName = ''
    PostName = ''


class _CifStructureFactors(_Pdb):
    """Helper class for cif structure factors file download"""
    Url = NDBBase._structureFactorsUrl
    PreName = 'r'
    PostName = 'st'


class _XmlComplete(NDBBase):
    """Helper class for Xml complete file download"""
    Url = NDBBase._xmlCompleteUrl
    Ext = ".xml"
    UrlExt = ".xml.gz"
    PreName = ''
    PostName = ''


class _XmlCoordinates(_XmlComplete):
    """Helper class for Xml coordinates file download"""
    Url = NDBBase._xmlCoordinatesUrl
    PostName = '-extatom'


class _XmlHeader(_XmlComplete):
    """Helper class for Xml header file download"""
    Url = NDBBase._xmlHeaderUrl
    PostName = '-noatom'


class DownloadType(Enum):
    """Enum for file download format

    :cvar Pdb: Asymmetric Unit coordinates (pdb format, Unix compressed(.gz))
    :cvar PdbBioAssembly: Biological Assembly coordinates
    :cvar Cif: Asymmetric Unit coordinates (cif format, Unix compressed(.gz))
    :cvar CifStructureFactors: Structure Factors (cif format)
    :cvar XmlComplete: XML | Complete with coordinates (xml format, GNU compressed(.gz))
    :cvar XmlCoordinates: XML | Coordinates only (xml format, GNU compressed(.gz))
    :cvar XmlHeader: XML | Header only (xml format, GNU compressed(.gz))
    """
    Pdb = _Pdb
    PdbBioAssembly = _PdbBioAssembly
    Cif = _Cif
    CifStructureFactors = _CifStructureFactors
    XmlComplete = _XmlComplete
    XmlCoordinates = _XmlCoordinates
    XmlHeader = _XmlHeader


class DownloadHelper(object):
    """Helper class for downloading form NDB"""
    @staticmethod
    def download(structure_id: str, download_type: DownloadType = DownloadType.Pdb,
                 save: bool = False, target_dir: str = '') -> str:
        """Download PDB from NDB

        :param download_type: file download type (default value is DownloadType.PDB)
        :type download_type: DownloadType
        :param target_dir: where to save file (default value is current dir)
        :type target_dir: str
        :param save: tells if file should be saved or not (default value = False)
        :type save: bool
        :param structure_id: structure NDB ID or PDB ID e.g. 4Z6C
        :type structure_id: str
        :return: string or None
        :rtype: str
        :raise AttributeError: when structure id is empty
        :raise FileNotFoundError: when file is not present on server
        """
        if not structure_id:
            raise AttributeError("structure id is empty")

        d_type = download_type.value
        file_name = d_type.PreName + structure_id.lower() + d_type.PostName

        if d_type is not DownloadType.PdbBioAssembly.value:
            try:
                proper_url = d_type.Url + file_name + d_type.UrlExt
                file_text = DownloadHelper._download_prepare(proper_url)
            except FileNotFoundError as error:
                if d_type is DownloadType.Pdb.value:
                    file_name = structure_id.lower() + d_type.PostName
                    proper_url = d_type.Url + file_name + d_type.UrlExt
                    file_text = DownloadHelper._download_prepare(proper_url)
                    pass
                else:
                    raise error

            if save:
                target = target_dir if target_dir else os.getcwd() + os.path.sep
                with open(target + file_name + d_type.Ext, 'w') as file:
                    file.write(file_text)

                return None
            return file_text
        else:
            results = []
            i = 1
            while True:
                try:
                    proper_url = d_type.Url + file_name + d_type.UrlExt + str(i)
                    file_text = DownloadHelper._download_prepare(proper_url, decompress=False)
                    results.append(file_text)
                    i += 1
                except FileNotFoundError:
                    break

            if save:
                i = 1
                target = target_dir if target_dir else os.getcwd() + os.path.sep
                for text in results:
                    with open(target + file_name + d_type.Ext + str(i), 'w') as file:
                        file.write(text)
                    i += 1
                return None

            return results

    @staticmethod
    def _download_prepare(url: str, decompress: bool=True) -> str:
        """To download and prepare if needed

        :param url: url to download from
        :type url: str
        :param decompress: tells if decompress (default value = True)
        :type decompress: bool
        :return: file string
        """
        try:
            file = DownloadHelper.download_file(url)
            if decompress:
                file = zlib.decompress(file.read(), 32 + zlib.MAX_WBITS)  # 32 to skip header of gz
            else:
                file = file.read()

            return file.decode("utf-8")

        except zlib.error:
            raise BufferError("File corrupted")

    @staticmethod
    def download_file(url: str) -> BytesIO:
        """Function to download file and convert to BytesIO

        :param url: file url
        :type url: str
        :return: file as BytesIO
        :rtype: BytesIO
        """
        with requests.session() as session:
            resp = session.get(url)

            if resp.status_code == 404:
                raise FileNotFoundError("No file on server")

            return BytesIO(resp.content)
        return None
