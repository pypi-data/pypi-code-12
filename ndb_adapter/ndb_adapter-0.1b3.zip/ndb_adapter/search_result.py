from typing import List

from ndb_adapter.search_report import *
from ndb_adapter.statistics import Statistics


class SearchResult(object):
    """Base class for search result"""
    def __init__(self):
        """Default constructor"""
        self._count = 0
        self._report = []

    def get_count(self) -> int:
        """Gets search results count

        :return: search results count
        :rtype: int
        """
        return self._count

    def get_report(self) -> list:
        """Gets search results report

        :return: list of search results reports
        :rtype: list
        """
        return self._report

    def set_count(self, count: int) -> None:
        """Sets result count

        :param count: value to set as count
        :type count: int
        :return: None
        """
        self._count = count

    def set_report(self, report: list) -> None:
        """Sets result report list

        :param report: list to be set as report
        :type report: list
        :return: None
        """
        self._report = report

    report = property(get_report, set_report, doc="Gets result report")
    """Search report property gets report list"""
    count = property(get_count, set_count, doc="Gets result count")
    """Search count property gets report count"""

    def __str__(self):
        return "Count: " + str(self._count) + ", Report:" + str([str(x) for x in self._report])


class SimpleResult(SearchResult):
    """Class for simple search result"""
    def __init__(self):
        """Default constructor"""
        super().__init__()

    def get_report(self) -> List[SimpleReport]:
        """Gets search results report list

        :return: list of simple search reports
        :rtype: List[SimpleReport]
        """
        return self._report

    def download(self, download_type: DownloadType = DownloadType.Pdb,
                 save: bool = False, target_dir: str = '') -> List[str]:
        """Download PDB files from NDB

        :param download_type: files download type (default value is DownloadType.PDB)
        :type download_type: DownloadType
        :param target_dir: where to save file (default value is current dir)
        :type target_dir: str
        :param save: tells if files should be saved or not (default value = False)
        :type save: bool
        :return: list of strings or None
        :rtype: List[str]
        """
        files = []
        for rep in self.get_report():
            file = ''
            try:
                file = rep.download(download_type, save, target_dir)
            except FileNotFoundError:
                print("No file with pdb_id: " + rep.pdb_id)
                pass
            except AttributeError:
                print("Structure has not pdb_id and ndb_id in report")
                pass

            files.append(file)

        return files


class AdvancedResult(SearchResult):
    """Class for advanced search result"""
    def __init__(self):
        """Default constructor"""
        super().__init__()
        self._statistics = Statistics()

    def get_report(self) -> List[AdvancedReport]:
        """Gets advanced search results report list. You should annotate return type depending on ReportType.

        :return: list of advanced search reports
        :rtype: List[AdvancedReport]
        """
        return self._report

    def download(self, download_type: DownloadType = DownloadType.Pdb,
                 save: bool = False, target_dir: str = '') -> List[str]:
        """Download PDB files from NDB

        :param download_type: files download type (default value is DownloadType.PDB)
        :type download_type: DownloadType
        :param target_dir: where to save file (default value is current dir)
        :type target_dir: str
        :param save: tells if files should be saved or not (default value = False)
        :type save: bool
        :return: list of strings or None
        :rtype: List[str]
        """
        try:
            files = []
            for rep in self._report:
                file = ''
                try:
                    file = rep.download(download_type, save, target_dir)
                except FileNotFoundError:
                    print("No file with id: " + rep.pdb_id)
                    pass
                except AttributeError:
                    print("Structure has not pdb_id in report")
                    pass
                files.append(file)

            return files
        except (NotImplementedError, KeyError):
            print("This report type doesn't support download")

        return []

    def get_statistics(self) -> Statistics:
        """Get statistics of advanced search

        :return: statistics of advanced search
        :rtype Statistics
        """
        return self._statistics

    def set_statistics(self, report: list) -> None:
        """Sets statistic

        :param report: report list to be parse as statistic
        :type report: list
        :return: None
        """
        self._statistics.set_report(report)

    statistics = property(get_statistics, set_statistics, doc="Statistics of advanced search")
    """Statistic report property gets report statistic"""

    def __str__(self):
        return "Count: " + str(self._count) + ", Report:" + str([str(x) for x in self._report]) + \
            "Statistics: " + str(self._statistics)
