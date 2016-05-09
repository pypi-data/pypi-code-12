from typing import List, Dict

from ndb_adapter.ndb_download import DownloadHelper
from ndb_adapter.ndb_download import DownloadType


class SummaryResult(object):
    """Class for summary results"""
    def __init__(self):
        """Default constructor"""
        self._report = {
            'PDB ID': '',
            'NDB ID': '',
            'Title': '',
            'Space Group': '',
            'Refinement': '',
            'Experimental Information': '',
            'Molecular Description': '',
            'Protein Sequence': {},
            'Primary Citation': {
                'Journal': '',
                'Authors': '',
                'pp': '',
                'Year': '',
                'Pubmed Id': '',
                'Title': ''
            },
            'Cell Constants': {
                'a': '',
                'b': '',
                'c': '',
                'alpha': '',
                'beta': '',
                'gamma': ''
            },
            'Nucleic Acid Sequence': {}
        }

    @property
    def pdb_id(self) -> str:
        """Gets summary result structure PDB ID

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def ndb_id(self) -> str:
        """Gets summary result structure NDB ID

        :return: NDB ID
        :rtype: str
        """
        return self._report['NDB ID']

    @property
    def title(self) -> str:
        """Gets summary result structure title

        :return: title
        :rtype: str
        """
        return self._report['Title']

    @property
    def space_group(self) -> str:
        """Gets summary result structure space group

        :return: space group
        :rtype: str
        """
        return self._report['Space Group']

    @property
    def refinement(self) -> str:
        """Gets summary result structure refinement

        :return: refinement
        :rtype: str
        """
        return self._report['Refinement']

    @property
    def experimental_method(self) -> str:
        """Gets summary result structure experimental method

        :return: experimental method
        :rtype: str
        """
        return self._report['Experimental Information']

    @property
    def description(self) -> str:
        """Gets summary result structure description

        :return: description
        :rtype: str
        """
        return self._report['Molecular Description']

    @property
    def citation_journal(self) -> str:
        """Gets summary result structure primary citation journal

        :return: primary citation journal
        :rtype: str
        """
        return self._report['Primary Citation']['Journal']

    @property
    def citation_authors(self) -> str:
        """Gets summary result structure primary citation authors

        :return: primary citation authors
        :rtype: str
        """
        return self._report['Primary Citation']['Authors']

    @property
    def citation_pages(self) -> str:
        """Gets summary result structure pages in primary citation

        :return: primary citation pages
        :rtype: str
        """
        return self._report['Primary Citation']['pp']

    @property
    def citation_year(self) -> str:
        """Gets summary result structure primary citation year

        :return: primary citation year
        :rtype: str
        """
        return self._report['Primary Citation']['Year']

    @property
    def citation_pubmed_id(self) -> str:
        """Gets summary result structure primary citation Pubmed ID

        :return: primary citation Pubmend ID
        :rtype: str
        """
        return self._report['Primary Citation']['Pubmed Id']

    @property
    def citation_title(self) -> str:
        """Gets summary result structure primary citation title

        :return: primary citation title
        :rtype: str
        """
        return self._report['Primary Citation']['Title']

    @property
    def cell_constants(self) -> Dict[str, float]:
        """Gets summary result structure cell constants as dict[str, float]

        :return: structure cell constants
        :rtype: Dict[str, float]
        """
        return self._report['Cell Constants']

    @property
    def cell_a(self) -> float:
        """Gets summary result structure cell a angstroms value

        :return: structure cell a angstroms
        :rtype: float
        """
        return self._report['Cell Constants']['a']

    @property
    def cell_b(self) -> float:
        """Gets summary result structure cell b angstroms value

        :return: structure cell b angstroms
        :rtype: float
        """
        return self._report['Cell Constants']['b']

    @property
    def cell_c(self) -> float:
        """Gets structure cell c angstroms value of summary result

        :return: structure cell a angstroms
        :rtype: float
        """
        return self._report['Cell Constants']['c']

    @property
    def cell_alpha(self) -> float:
        """Gets summary result structure cell alpha

        :return: structure cell alpha degrees
        :rtype: Dict[str, float]
        """
        return self._report['Cell Constants']['alpha']

    @property
    def cell_beta(self) -> float:
        """Gets summary result structure cell beta

        :return: structure cell beta degrees
        :rtype: float
        """
        return self._report['Cell Constants']['beta']

    @property
    def cell_gamma(self) -> float:
        """Gets summary result structure cell gamma

        :return: structure cell gamma degrees
        :rtype: float
        """
        return self._report['Cell Constants']['gamma']

    @property
    def protein_seq(self) -> List[str]:
        """Gets summary result structure protein sequences

        :return: structure protein sequences
        :rtype: List[str]
        """
        return list(self._report['Protein Sequence'].values())

    @property
    def protein_seq_with_names(self) -> List[Dict[str, str]]:
        """Gets summary result structure protein sequences with names

        :return: structure protein sequences with names
        :rtype: List[Dict[str, str]]
        """
        return list(self._report['Protein Sequence'].items())

    @property
    def nucleic_acid_seq(self) -> List[str]:
        """Gets summary result structure nucleic acid sequences

        :return: structure nucleic acid sequences
        :rtype: List[str]
        """
        return list(self._report['Nucleic Acid Sequence'].values())

    @property
    def nucleic_acid_seq_with_names(self) -> List[Dict[str, str]]:
        """Gets summary result structure nucleic acid sequences with names

        :return: structure nucleic acid sequences with names
        :rtype: List[Dict[str, str]]
        """
        return list(self._report['Nucleic Acid Sequence'].items())

    def update(self, report: dict) -> None:
        """Update internal report

        :param report: extending report
        :type report: dict
        :return: None
        """
        self._report.update(report)

    def download(self, download_type: DownloadType=DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """Download PDB from NDB

        :param download_type: file download type (default value is DownloadType.PDB)
        :type download_type: DownloadType
        :param target_dir: where to save file (default value is current dir)
        :type target_dir: str
        :param save: tells if file should be saved or not (default value = False)
        :type save: bool
        :return: string or None
        :rtype: str
        """
        id_structure = self.pdb_id
        if not self.pdb_id:
            print("No pdb_id trying ndb_id")
            id_structure = self.ndb_id

        return DownloadHelper.download(id_structure, download_type, save, target_dir)

    def get_dict(self) -> dict:
        """Gets internal report dict

        :return: report as dictionary
        :rtype: dict
        """
        return self._report

    def __str__(self) -> str:
        return str(self._report)
