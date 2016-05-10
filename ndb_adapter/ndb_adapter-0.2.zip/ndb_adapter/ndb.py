import requests

import ndb_adapter.report_parser as parser
from ndb_adapter.advanced_search_options import AdvancedSearchOptions
from ndb_adapter.dna_search_options import DnaSearchOptions
from ndb_adapter.ndb_base import NDBBase
from ndb_adapter.ndb_download import DownloadHelper, DownloadType
from ndb_adapter.rna_search_options import RnaSearchOptions
from ndb_adapter.search_result import SimpleResult, AdvancedResult
from ndb_adapter.summary_result import SummaryResult


class NDB(NDBBase):
    """Main class for search in NDB - all methods are static"""
    @staticmethod
    def advanced_search(options: AdvancedSearchOptions= None) -> AdvancedResult:
        """Advanced search in NDB, if in options "stats= True" returns also statistics - works only in some \
        search types. Default search "type= ReportType.NDBStatus". Depending on ReportType you can annotate return \
        type i.e. "result.report() # ReportType.NDBStatus".

        :param options: options for advanced search (default value = None) - clear AdvancedSearchOptions()
        :type options: AdvancedSearchOptions
        :return: search result { count -> int, report -> List[AdvancedReport], statistics -> Statistics }
        :rtype: AdvancedResult
        """
        if not options:
            options = AdvancedSearchOptions()

        with requests.session() as session:
            text_stats = ""
            if options.get_statistics():
                resp = session.post(NDBBase._advancedUrl, data=options.get(stats=True))
                text_stats = resp.text

            resp = session.post(NDBBase._advancedUrl, data=options.get())
            text = resp.text
            report = parser.parse_advanced_search_report(text, text_stats, options.get_report_type())
            return report

    @staticmethod
    def dna_search(options: DnaSearchOptions= None) -> SimpleResult:
        """Dna only search in NDB.

        :param options: options for dna search (default value = None) - clear DnaSearchOptions()
        :type options: DnaSearchOptions
        :return: search simple result { count -> int, report -> List[SimpleReport] }
        :rtype: SimpleResult
        """
        if not options:
            options = DnaSearchOptions()

        with requests.session() as session:
            resp = session.post(NDBBase._dnaUrl, data=options.get())
            text = resp.text
            report = parser.parse_search_report(text)
            return report

    @staticmethod
    def rna_search(options: RnaSearchOptions= None) -> SimpleResult:
        """Rna only search in NDB.

        :param options: options for rna search (default value = None) - clear RnaSearchOptions()
        :type options: RnaSearchOptions
        :return: search simple result { count -> int, report -> List[SimpleReport] }
        :rtype: SimpleResult
        """
        if not options:
            options = RnaSearchOptions()

        with requests.session() as session:
            resp = session.post(NDBBase._rnaUrl, data=options.get())
            text = resp.text
            report = parser.parse_search_report(text)
            return report

    @staticmethod
    def summary(structure_id: str) -> SummaryResult:
        """Summary search in NDb

        :param structure_id: structure NDB ID or PDB ID e.g. 4Z6C
        :type structure_id: str
        :return: search summary result
        :rtype: SummaryResult
        """
        params = {
            'searchTarget': structure_id
        }

        with requests.session() as session:
            resp = session.post(NDBBase._summaryUrl, data=params)
            text = resp.text
            report = parser.parse_summary(text)
            return report

    @staticmethod
    def download(structure_id: str, download_type: DownloadType=DownloadType.Pdb,
                 save: bool=False, target_dir: str='') -> str:
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
        """
        return DownloadHelper.download(structure_id, download_type, save, target_dir)
