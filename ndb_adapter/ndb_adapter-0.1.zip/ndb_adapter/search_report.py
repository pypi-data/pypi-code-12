from typing import TypeVar

from ndb_adapter.ndb_download import DownloadHelper
from ndb_adapter.ndb_download import DownloadType


def _assign_numbers(dic: dict) -> dict:
    """Private function for assign numbers values to dictionary

    :param dic: report dictionary
    :type dic: dict
    :return: report dictionary
    :rtype: dict
    """
    for k, v in dic.items():
        try:
            if '.' in v:
                dic[k] = float(v)
            else:
                dic[k] = int(v)

        except ValueError:
            pass
    return dic


class SimpleReport(object):
    """Class for simple result report"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dictionary (default value = None)
        :type report: dict
        """
        self._report = {
            'NDB ID': '',
            'PDB ID': '',
            'Classification': '',
            'Title': '',
            'PDB Release Date': '',
            'Authors': '',
            'Citation Title': '',
            'Citation Detail': '',
            'Experiment': '',
            'Resolution': 0,
            'R work': 0,
            'R free': 0
        }
        if report:
            self._report.update(report)

    @property
    def pdb_id(self) -> str:
        """Gets simple report structure PDB

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def ndb_id(self) -> str:
        """Gets simple report structure NDB ID

        :return: NDB ID
        :rtype: str
        """
        return self._report['NDB ID']

    @property
    def title(self) -> str:
        """Gets simple report structure title

        :return: title
        :rtype: str
        """
        return self._report['Title']

    @property
    def classification(self) -> str:
        """Gets simple report structure classification

        :return: classification
        :rtype: str
        """
        return self._report['Classification']

    @property
    def release_date(self) -> str:
        """Gets simple report structure release date

        :return: release date
        :rtype: str
        """
        return self._report['PDB Release Date']

    @property
    def authors(self) -> str:
        """Gets simple report structure authors

        :return: authots
        :rtype: str
        """
        return self._report['Authors']

    @property
    def citation_title(self) -> str:
        """Gets simple report structure citation title

        :return: citation title
        :rtype: str
        """
        return self._report['Citation Title']

    @property
    def citation_detail(self) -> str:
        """Gets simple report structure citation title

        :return: citation detail
        :rtype: str
        """
        return self._report['Citation Detail']

    @property
    def experimental_method(self) -> str:
        """Gets simple report structure experimental method

        :return: experimental method
        :rtype: str
        """
        return self._report['Experiment']

    @property
    def resolution(self) -> float:
        """Gets simple report structure resolution

        :return: resolution
        :rtype: float
        """
        return self._report['Resolution']

    @property
    def r_work(self) -> float:
        """Gets simple report structure r work

        :return: r work
        :rtype: float
        """
        return self._report['R work']

    @property
    def r_free(self) -> float:
        """Gets simple report structure r free

        :return: r free
        :rtype: float
        """
        return self._report['R free']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """Download PDB from ndb

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
        """Gets simple report as dict

        :return: simple report dict
        :rtype: dict
        """
        return self._report

    def __str__(self) -> str:
        return str(self._report)


class _AdvancedBaseReport(object):
    """Base class for advanced reports"""
    def __init__(self):
        """Default constructor"""
        self._report = {
            'NDB ID': ''
        }

    def _update(self, report: dict) -> None:
        """Private method to update inner report dict

        :param report: extending report dict
        :type report: dict
        :return: None
        """
        self._report.update(report)

    @staticmethod
    def report_type() -> str:
        """Advanced report type - depends of search"""
        raise NotImplementedError

    @property
    def ndb_id(self) -> str:
        """Gets advanced report structure NDB ID

        :return: NDB ID
        :rtype: str
        """
        return self._report['NDB ID']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """To download files from NDB - only works for some reports"""
        raise NotImplementedError

    def get_dict(self) -> dict:
        """Gets advanced report as dict

        :return: advanced report dict
        :rtype: dict
        """
        return self._report

    def __str__(self) -> str:
        return str(self._report)


class NDBStatusReport(_AdvancedBaseReport):
    """Class for NDB status search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict= None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'PDB ID': '',
            'Title': '',
            'NDB Release Date': '',
            'Authors': '',
            'Initial Deposition Date': ''
        })
        if report:
            self._update(report)

    @staticmethod
    def report_type() -> str:
        return 'ndbStatus'

    @property
    def pdb_id(self) -> str:
        """Gets advanced report structure PDB ID

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def title(self) -> str:
        """Gets advanced report structure title

        :return: title
        :rtype: str
        """
        return self._report['Title']

    @property
    def release_date(self) -> str:
        """Gets advanced report structure NDB release date

        :return: release date
        :rtype: str
        """
        return self._report['NDB Release Date']

    @property
    def deposition_date(self) -> str:
        """Gets advanced report structure initial deposition date

        :return: initial deposition date
        :rtype: str
        """
        return self._report['Initial Deposition Date']

    @property
    def authors(self) -> str:
        """Gets advanced report structure authors

        :return: authors
        :rtype: str
        """
        return self._report['Authors']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
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


class CellDimensionsReport(_AdvancedBaseReport):
    """Class for cell dimensions search report extending _AdvancedBaseReport"""

    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'Length A': 0,
            'Length B': 0,
            'Length C': 0,
            'Angle Alpha': 0,
            'Angle Beta': 0,
            'Angle Gamma': 0,
            'Space Group': ''
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'cellDim'

    @property
    def cell_a(self) -> float:
        """Gets advanced report structure cell a in angstroms

        :return: cell a
        :rtype: float
        """
        return self._report['Length A']

    @property
    def cell_b(self) -> float:
        """Gets advanced report structure cell b in angstroms

        :return: cell b
        :rtype: float
        """
        return self._report['Length B']

    @property
    def cell_c(self) -> float:
        """Gets advanced report structure cell c in angstroms

        :return: cell c
        :rtype: float
        """
        return self._report['Length C']

    @property
    def cell_alpha(self) -> float:
        """Gets advanced report structure cell alpha in degrees

        :return: alpha
        :rtype: float
        """
        return self._report['Angle Alpha']

    @property
    def cell_beta(self) -> float:
        """Gets advanced report structure cell beta in degrees

        :return: beta
        :rtype: float
        """
        return self._report['Angle Beta']

    @property
    def cell_gamma(self) -> float:
        """Gets advanced report structure cell gamma in degrees

        :return: gamma
        :rtype: float
        """
        return self._report['Angle Gamma']

    @property
    def space_group(self) -> str:
        """Gets advanced report structure space group

        :return: space group
        :rtype: float
        """
        return self._report['Space Group']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class CitationReport(_AdvancedBaseReport):
    """Class for citation search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'PDB ID': '',
            'Citation Title': '',
            'Citation Authors': '',
            'Journal': '',
            'Pubmed ID': '',
            'Year': 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'citation'

    @property
    def pdb_id(self) -> str:
        """Gets advanced report structure PDB ID

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def citation_title(self) -> str:
        """Gets advanced report structure citation title

        :return: citation title
        :rtype: str
        """
        return self._report['Citation Title']

    @property
    def citation_authors(self) -> str:
        """Gets advanced report structure citation authors

        :return: citation authors
        :rtype: str
        """
        return self._report['Citation Authors']

    @property
    def journal(self) -> str:
        """Gets advanced report structure Journal

        :return: Journal
        :rtype: str
        """
        return self._report['Journal']

    @property
    def pubmed_id(self) -> str:
        """Gets advanced report structure pubmed ID

        :return: PDB ID
        :rtype: str
        """
        return self._report['Pubmed ID']

    @property
    def year(self) -> int:
        """Gets advanced report structure year

        :return: year
        :rtype: int
        """
        return self._report['Year']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
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


class RefinementDataReport(_AdvancedBaseReport):
    """Class for refinement data search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'R-value_work': 0,
            'R-value_obs': 0,
            'R-value_free': 0,
            'Higher Resolution Limit': 0,
            'Lower Resolution Limit': 0,
            'Reflections Observed': 0,
            'Structure Refinement': ''
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'ref'

    @property
    def r_work(self) -> float:
        """Gets advanced report structure r work

        :return: r work
        :rtype: float
        """
        return self._report['R-value_work']

    @property
    def r_obs(self) -> float:
        """Gets advanced report structure r obs

        :return: r obs
        :rtype: float
        """
        return self._report['R-value_obs']

    @property
    def r_free(self) -> float:
        """Gets advanced report structure r free

        :return: r free
        :rtype: float
        """
        return self._report['R-value_free']

    @property
    def higher_resolution(self) -> float:
        """Gets advanced report structure higher resolution limit

        :return: higher resolution limit
        :rtype: float
        """
        return self._report['Higher Resolution Limit']

    @property
    def lower_resolution(self) -> float:
        """Gets advanced report structure lower resolution limit

        :return: lower resolution limit
        :rtype: float
        """
        return self._report['Lower Resolution Limit']

    @property
    def reflections(self) -> int:
        """Gets advanced report structure reflections observed

        :return: reflections observed
        :rtype: int
        """
        return self._report['Reflections Observed']

    @property
    def structure_ref(self) -> str:
        """Gets advanced report structure refinement

        :return: structure refinement
        :rtype: str
        """
        return self._report['Structure Refinement']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class NABackboneTorsionReport(_AdvancedBaseReport):
    """Class for refinement data search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'Model ID': '',
            'Chain ID': '',
            'Residue Num': 0,
            'Residue Name': '',
            "O3'-P-O5'-C5": 0,
            "P-O5'-C5'-C4'": 0,
            "O5'-C5'-C4'-C3'": 0,
            "C5'-C4'-C3'-O3'": 0,
            "C4'-C3'-O3'-P": 0,
            "C3'-O3'-P-O5'": 0,
            "O4'-C1'-N1-9-C2-4": 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'nabt'

    @property
    def model_id(self) -> str:
        """Gets advanced report structure model ID

        :return: model ID
        :rtype: str
        """
        return self._report['Model ID']

    @property
    def chain_id(self) -> str:
        """Gets advanced report structure chain ID

        :return: chain ID
        :rtype: str
        """
        return self._report['Chain ID']

    @property
    def residue_number(self) -> int:
        """Gets advanced report structure residue number

        :return: residue number
        :rtype: int
        """
        return self._report['Residue Num']

    @property
    def residue_name(self) -> str:
        """Gets advanced report structure residue name

        :return: residue name
        :rtype: str
        """
        return self._report['Residue Name']

    @property
    def o3_p_o5_c5(self) -> float:
        """Gets advanced report structure O3'-P-O5'-C5'

        :return: O3'-P-O5'-C5'
        :rtype: float
        """
        return self._report["O3'-P-O5'-C5'"]

    @property
    def p_o5_c5_c4(self) -> float:
        """Gets advanced report structure P-O5'-C5'-C4'

        :return: P-O5'-C5'-C4'
        :rtype: float
        """
        return self._report["P-O5'-C5'-C4'"]

    @property
    def o5_c5_c4_c3(self) -> float:
        """Gets advanced report structure O5'-C5'-C4'-C3'

        :return: O5'-C5'-C4'-C3'
        :rtype: float
        """
        return self._report["O5'-C5'-C4'-C3'"]

    @property
    def c5_c4_c3_o3(self) -> float:
        """Gets advanced report structure C5'-C4'-C3'-O3'

        :return: C5'-C4'-C3'-O3'
        :rtype: float
        """
        return self._report["C5'-C4'-C3'-O3'"]

    @property
    def c4_c3_o3_p(self) -> float:
        """Gets advanced report structure C4'-C3'-O3'-P

        :return: C4'-C3'-O3'-P
        :rtype: float
        """
        return self._report["C4'-C3'-O3'-P"]

    @property
    def c3_o3_p_o5(self) -> float:
        """Gets advanced report structure C3'-O3'-P-O5'

        :return: C3'-O3'-P-O5'
        :rtype: float
        """
        return self._report["C3'-O3'-P-O5'"]

    @property
    def o4_c1_n1_9_c2_4(self) -> float:
        """Gets advanced report structure O4'-C1'-N1-9-C2-4

        :return: O4'-C1'-N1-9-C2-4
        :rtype: float
        """
        return self._report["O4'-C1'-N1-9-C2-4"]

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class BasePairParameterReport(_AdvancedBaseReport):
    """Class for base pair parameter search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'Model Number': 0,
            'Pair Number': 0,
            'Pair Name': '',
            'Shear': 0,
            'Stretch': 0,
            'Stagger': 0,
            'Buckle': 0,
            'Propellor': 0,
            'Opening': 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'bpp'

    @property
    def model_num(self) -> int:
        """Gets advanced report structure model number

        :return: model number
        :rtype: int
        """
        return self._report['Model Number']

    @property
    def pair_num(self) -> int:
        """Gets advanced report structure pair number

        :return: pair number
        :rtype: int
        """
        return self._report['Pair Number']

    @property
    def pair_name(self) -> str:
        """Gets advanced report structure pair name

        :return: pair name
        :rtype: str
        """
        return self._report['Pair Name']

    @property
    def shear(self) -> float:
        """Gets advanced report structure shear

        :return: shear
        :rtype: float
        """
        return self._report['Shear']

    @property
    def stretch(self) -> float:
        """Gets advanced report structure stretch

        :return: stretch
        :rtype: float
        """
        return self._report['Stretch']

    @property
    def stagger(self) -> float:
        """Gets advanced report structure stagger

        :return: stagger
        :rtype: float
        """
        return self._report['Stagger']

    @property
    def buckle(self) -> float:
        """Gets advanced report structure buckle

        :return: buckle
        :rtype: float
        """
        return self._report['Buckle']

    @property
    def propellor(self) -> float:
        """Gets advanced report structure propellor

        :return: propellor
        :rtype: float
        """
        return self._report['Propellor']

    @property
    def opening(self) -> float:
        """Gets advanced report structure opening

        :return: opening
        :rtype: float
        """
        return self._report['Opening']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class BasePairStepParameterReport(_AdvancedBaseReport):
    """Class for base pair parameter search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'Model Number': 0,
            'Step Number': 0,
            'Step Name': '',
            'Shift': 0,
            'Slide': 0,
            'Rise': 0,
            'Tilt': 0,
            'Roll': 0,
            'Twist': 0,
            'X-Displacement': 0,
            'Y-Displacement': 0,
            'Helical Rise': 0,
            'Inclination': 0,
            'Tip': 0,
            'Helical Twist': 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'bpsp'

    @property
    def model_num(self) -> int:
        """Gets advanced report structure model number

        :return: model number
        :rtype: int
        """
        return self._report['Model Number']

    @property
    def step_num(self) -> int:
        """Gets advanced report structure step number

        :return: step number
        :rtype: int
        """
        return self._report['Step Number']

    @property
    def step_name(self) -> str:
        """Gets advanced report structure step name

        :return: step name
        :rtype: str
        """
        return self._report['Step Name']

    @property
    def shift(self) -> float:
        """Gets advanced report structure shift

        :return: shift
        :rtype: float
        """
        return self._report['Shift']

    @property
    def slide(self) -> float:
        """Gets advanced report structure slide

        :return: slide
        :rtype: float
        """
        return self._report['Slide']

    @property
    def rise(self) -> float:
        """Gets advanced report structure rise

        :return: rise
        :rtype: float
        """
        return self._report['Rise']

    @property
    def tilt(self) -> float:
        """Gets advanced report structure tilt

        :return: tilt
        :rtype: float
        """
        return self._report['Tilt']

    @property
    def roll(self) -> float:
        """Gets advanced report structure roll

        :return: roll
        :rtype: float
        """
        return self._report['Roll']

    @property
    def x_disp(self) -> float:
        """Gets advanced report structure x displacement

        :return: x displacement
        :rtype: float
        """
        return self._report['X-Displacement']

    @property
    def y_disp(self) -> float:
        """Gets advanced report structure y displacement

        :return: x displacement
        :rtype: float
        """
        return self._report['Y-Displacement']

    @property
    def helical_rise(self) -> float:
        """Gets advanced report structure helical rise

        :return: helical rise
        :rtype: float
        """
        return self._report['Helical Rise']

    @property
    def inclination(self) -> float:
        """Gets advanced report structure inclination

        :return: inclination
        :rtype: float
        """
        return self._report['Inclination']

    @property
    def tip(self) -> float:
        """Gets advanced report structure tip

        :return: tip
        :rtype: float
        """
        return self._report['Tip']

    @property
    def helical_twist(self) -> float:
        """Gets advanced report structure helical twist

        :return: helical twist
        :rtype: float
        """
        return self._report['Helical Twist']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class DescriptorReport(_AdvancedBaseReport):
    """Class for descriptor search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'Structure Description': '',
        })
        if report:
            self._update(report)

    @staticmethod
    def report_type() -> str:
        return 'desc'

    @property
    def description(self) -> str:
        """Gets advanced report structure description

        :return: description
        :rtype: str
        """
        return self._report['Structure Description']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class SequencesReport(_AdvancedBaseReport):
    """Class for sequences search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'NA Sequence': '',
            'Structure Description': '',
        })
        if report:
            self._update(report)

    @staticmethod
    def report_type() -> str:
        return 'naSeq'

    @property
    def sequence(self) -> str:
        """Gets advanced report structure nucleic acid sequence

        :return: sequence
        :rtype: str
        """
        return self._report['NA Sequence']

    @property
    def description(self) -> str:
        """Gets advanced report structure description

        :return: description
        :rtype: str
        """
        return self._report['Structure Description']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
        """NOT WORKS ON THIS REPORT TYPE"""
        pass


class StatisticReport(object):
    """Class for statistic search report"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        self._stats = report

    @property
    def stats(self) -> dict:
        """Gets advanced report structure statistics

        :return: statistics
        :rtype: str
        """
        return self._stats


class RNA3DBasePairRelFreqReport(_AdvancedBaseReport):
    """Class for RNA 3D Base Pair Relative Frequency Report search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'PDB ID': '',
            'Relative cWW': 0,
            'Relative tWW': 0,
            'Relative cWH': 0,
            'Relative tWH': 0,
            'Relative cWS': 0,
            'Relative tWS': 0,
            'Relative cHH': 0,
            'Relative tHH': 0,
            'Relative cHS': 0,
            'Relative tHS': 0,
            'Relative cSS': 0,
            'Relative tSS': 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'bpFreq'

    @property
    def pdb_id(self) -> str:
        """Gets advanced report structure PDB

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def cww(self) -> float:
        """Gets advanced report relative cWW

        :return: relative cWW
        :rtype: float
        """
        return self._report['Relative cWW']

    @property
    def tww(self) -> float:
        """Gets advanced report relative tWW

        :return: relative tWW
        :rtype: float
        """
        return self._report['Relative tWW']

    @property
    def cwh(self) -> float:
        """Gets advanced report relative qWH

        :return: relative qWH
        :rtype: float
        """
        return self._report['Relative cWH']

    @property
    def twh(self) -> float:
        """Gets advanced report relative tWH

        :return: relative tWH
        :rtype: float
        """
        return self._report['Relative tWH']

    @property
    def cws(self) -> float:
        """Gets advanced report relative cWS

        :return: relative cWS
        :rtype: float
        """
        return self._report['Relative cWS']

    @property
    def tws(self) -> float:
        """Gets advanced report relative tWS

        :return: relative tWS
        :rtype: float
        """
        return self._report['Relative tWS']

    @property
    def chh(self) -> float:
        """Gets advanced report relative cHH

        :return: relative cHH
        :rtype: float
        """
        return self._report['Relative cHH']

    @property
    def thh(self) -> float:
        """Gets advanced report relative tHH

        :return: relative tHH
        :rtype: float
        """
        return self._report['Relative tHH']

    @property
    def chs(self) -> float:
        """Gets advanced report relative cHS

        :return: relative cHS
        :rtype: float
        """
        return self._report['Relative cHS']

    @property
    def ths(self) -> float:
        """Gets advanced report relative tHS

        :return: relative tHS
        :rtype: float
        """
        return self._report['Relative tHS']

    @property
    def css(self) -> float:
        """Gets advanced report relative cSS

        :return: relative cSS
        :rtype: float
        """
        return self._report['Relative cSS']

    @property
    def tss(self) -> float:
        """Gets advanced report relative tSS

        :return: relative tWS
        :rtype: float
        """
        return self._report['Relative tSS']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
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


class RNA3DBasePhosphateRelFreqReport(_AdvancedBaseReport):
    """Class for RNA 3D Base Phosphate Relative Frequency Report search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'PDB ID': '',
            'Relative 1BPh': 0,
            'Relative 2BPh': 0,
            'Relative 3BPh': 0,
            'Relative 4BPh': 0,
            'Relative 5BPh': 0,
            'Relative 6BPh': 0,
            'Relative 7BPh': 0,
            'Relative 8BPh': 0,
            'Relative 9BPh': 0,
            'Relative 0BPh': 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'bphsFreq'

    @property
    def pdb_id(self) -> str:
        """Gets advanced report structure PDB

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def bph_1(self) -> float:
        """Gets advanced report relative 1BPh

        :return: relative 1BPh
        :rtype: float
        """
        return self._report['Relative 1BPh']

    @property
    def bph_2(self) -> float:
        """Gets advanced report relative 2BPh

        :return: relative 2BPh
        :rtype: float
        """
        return self._report['Relative 2BPh']

    @property
    def bph_3(self) -> float:
        """Gets advanced report relative 3BPh

        :return: relative 3BPh
        :rtype: float
        """
        return self._report['Relative 3BPh']

    @property
    def bph_4(self) -> float:
        """Gets advanced report relative 4BPh

        :return: relative 4BPh
        :rtype: float
        """
        return self._report['Relative 4BPh']

    @property
    def bph_5(self) -> float:
        """Gets advanced report relative 5BPh

        :return: relative 5BPh
        :rtype: float
        """
        return self._report['Relative 5BPh']

    @property
    def bph_6(self) -> float:
        """Gets advanced report relative 6BPh

        :return: relative 6BPh
        :rtype: float
        """
        return self._report['Relative 6BPh']

    @property
    def bph_7(self) -> float:
        """Gets advanced report relative 7BPh

        :return: relative 7BPh
        :rtype: float
        """
        return self._report['Relative 7BPh']

    @property
    def bph_8(self) -> float:
        """Gets advanced report relative 8BPh

        :return: relative 8BPh
        :rtype: float
        """
        return self._report['Relative 8BPh']

    @property
    def bph_9(self) -> float:
        """Gets advanced report relative 9BPh

        :return: relative 9BPh
        :rtype: float
        """
        return self._report['Relative 9BPh']

    @property
    def bph_0(self) -> float:
        """Gets advanced report relative 0BPh

        :return: relative 0BPh
        :rtype: float
        """
        return self._report['Relative 0BPh']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
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


class RNA3DBaseStackingRelFreqReport(_AdvancedBaseReport):
    """Class for RNA 3D Base Stacking Relative Frequency Report search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'PDB ID': '',
            'Relative s33': 0,
            'Relative s53': 0,
            'Relative s55': 0
        })
        if report:
            self._update(_assign_numbers(report))

    @staticmethod
    def report_type() -> str:
        return 'stackFreq'

    @property
    def pdb_id(self) -> str:
        """Gets advanced report structure PDB

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def s33(self) -> float:
        """Gets advanced report structure relative s33

        :return: relative s33
        :rtype: float
        """
        return self._report['Relative s33']

    @property
    def s53(self) -> float:
        """Gets advanced report structure relative s53

        :return: relative s53
        :rtype: float
        """
        return self._report['Relative s53']

    @property
    def s55(self) -> float:
        """Gets advanced report structure relative s55

        :return: relative s55
        :rtype: float
        """
        return self._report['Relative s55']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
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


class RNA3DMotifReport(_AdvancedBaseReport):
    """Class for RNA 3D Base Phosphate Relative Frequency Report search report extending _AdvancedBaseReport"""
    def __init__(self, report: dict = None):
        """Default constructor

        :param report: report dict to make report (default value = None)
        :type report: dict"""
        super().__init__()
        self._update({
            'PDB ID': '',
            'Motif ID': '',
            'Common Name': '',
            'Annotation': ''
        })
        if report:
            self._update(report)

    @staticmethod
    def report_type() -> str:
        return 'motif'

    @property
    def pdb_id(self) -> str:
        """Gets advanced report structure PDB

        :return: PDB ID
        :rtype: str
        """
        return self._report['PDB ID']

    @property
    def motif_id(self) -> str:
        """Gets advanced report structure motif ID

        :return: motif ID
        :rtype: str
        """
        return self._report['Motif ID']

    @property
    def common_name(self) -> str:
        """Gets advanced report structure common name

        :return: common name
        :rtype: str
        """
        return self._report['Common Name']

    @property
    def annotation(self) -> str:
        """Gets advanced report structure annotation

        :return: annotation
        :rtype: str
        """
        return self._report['Annotation']

    def download(self, download_type: DownloadType = DownloadType.Pdb, save: bool = False, target_dir: str = '') -> str:
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


AdvancedReport = TypeVar('AdvancedReport', NDBStatusReport, CellDimensionsReport, CitationReport, RefinementDataReport,
                         NABackboneTorsionReport, BasePairParameterReport, BasePairStepParameterReport,
                         DescriptorReport, SequencesReport, StatisticReport, RNA3DBasePairRelFreqReport,
                         RNA3DBasePhosphateRelFreqReport, RNA3DBaseStackingRelFreqReport, RNA3DMotifReport)
