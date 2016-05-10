from datetime import date, datetime
from typing import List, Optional

from ndb_adapter.enums import ReportType, YesNoIgnore, AndOr, DnaRnaEither, GreaterLowerEqual, DrugBinding, SpaceGroup, \
    RFactor, BasePair, BasePhosphate, BaseStack, GreaterLower, InternalLoopMotif, HairpinLoopMotif, ResolutionCutoff, \
    EnzymeFunction, RegulatoryFunction, StructuralFunction, OtherFunction, NaFeature, StrandDescription, \
    ConformationType


class AdvancedSearchOptions(object):
    """Class needed for advanced search option parameters"""

    def __init__(self, report_type: ReportType = ReportType.NDBStatus, statistics: bool = True):
        """Default constructor

        :param report_type: advanced search report type (default value = ReportType.NDBStatus)
        :type report_type: ReportType
        :param statistics: to tell if ask for statistic (default value = True)
        :type statistics: bool
        """
        self._report_type = report_type.value
        self._statistics = statistics
        self._options = {
            'search_report': report_type.value.report_type(),
        }
        self.reset()

    def reset(self) -> None:
        """Reset advanced search options to defaults

        :returns: None
        """
        self._options.update({
            'q_nasct_des': [],
            'q_prbmd_sfn': [],
            'i_prbmd_ofn': AndOr.And.value,
            'c_detal_rfc': AndOr.And.value,
            'q_detal_res': '',
            'q_biocn_lid': '',
            'q_biocn_lig': YesNoIgnore.Ignore.value,
            'c_biocn_drg': AndOr.And.value,
            'c_citat_ann': AndOr.And.value,
            'c_detal_anb': AndOr.And.value,
            'c_detal_ana': AndOr.And.value,
            'c_bph_int': AndOr.And.value,
            'c_detal_ang': AndOr.And.value,
            'c_detal_lnc': AndOr.And.value,
            'c_bph_count': '',
            'q_seqnc': '',
            'i_nasct_des': AndOr.Or.value,
            'q_biocn_hyb': YesNoIgnore.Ignore.value,
            'q_detal_grp': SpaceGroup.Empty.value,
            'c_prbmd_oth': AndOr.And.value,
            'c_bp_count': '',
            'c_etype_sfc': AndOr.And.value,
            'c_etype_nmr': AndOr.And.value,
            'q_biocn_rna': YesNoIgnore.Ignore.value,
            'c_biocn_pro': AndOr.And.value,
            'q_bph_f_op': GreaterLower.GreaterEqual.value,
            'q_bp_count': '',
            'c_nasct_ftr': AndOr.And.value,
            'q_detal_vla': '',
            'q_detal_vlb': '',
            'q_detal_vlc': '',
            'c_prbmd_reg': AndOr.And.value,
            'c_namod_bas': AndOr.And.value,
            'q_biocn_drg': YesNoIgnore.Ignore.value,
            'q_namod_sgr': YesNoIgnore.Ignore.value,
            'q_bph_f_int': BasePhosphate.Empty.value,
            'c_bs_f_count': AndOr.And.value,
            'c_bs_count': '',
            'q_etype_nra': YesNoIgnore.Ignore.value,
            'q_bph_int': BasePhosphate.Empty.value,
            'c_bp_int': AndOr.And.value,
            'q_detal_olc': GreaterLowerEqual.Equal.value,
            'q_detal_vag': '',
            'c_bs_int': AndOr.And.value,
            'q_prbmd_efn': [],
            'q_detal_vab': '',
            'q_detal_vaa': '',
            'q_detal_oab': GreaterLowerEqual.Equal.value,
            'i_prbmd_sfn': AndOr.And.value,
            'q_detal_oaa': GreaterLowerEqual.Equal.value,
            'q_bp_f_op': GreaterLower.GreaterEqual.value,
            'q_detal_oag': GreaterLowerEqual.Equal.value,
            'q_hairpin_motif': [],
            'q_bp_f_int': BasePair.Empty.value,
            'q_namod_phs': YesNoIgnore.Ignore.value,
            'c_int_motif': AndOr.And.value,
            'q_authr': '',
            'c_nr_list': AndOr.And.value,
            'c_detal_res': AndOr.And.value,
            'q_citat_ann': '',
            'c_authr': AndOr.And.value,
            'q_etype_cry': YesNoIgnore.Ignore.value,
            'c_bp_f_count': AndOr.And.value,
            'q_etype_nmr': YesNoIgnore.Ignore.value,
            'q_int_motif': [],
            'c_etype_cry': AndOr.And.value,
            'q_bph_count': '',
            'q_bp_int': BasePair.Empty.value,
            'q_nr_list': ResolutionCutoff.Empty.value,
            'c_biocn_dna': AndOr.And.value,
            'q_prbmd_rfn': [],
            'q_prbmd_enz': DnaRnaEither.Either.value,
            'i_hairpin_motif': AndOr.Or.value,
            'q_bs_int': BaseStack.Empty.value,
            'q_detal_ola': GreaterLowerEqual.Equal.value,
            'c_biocn_lnm': AndOr.And.value,
            'q_detal_olb': GreaterLowerEqual.Equal.value,
            'q_nasct_typ': ConformationType.Empty.value,
            'q_bs_op': '',
            'c_biocn_hyb': AndOr.And.value,
            'q_biocn_pro': YesNoIgnore.Ignore.value,
            'c_etype_nra': AndOr.And.value,
            'q_bs_f_int': BaseStack.Empty.value,
            'q_etype_sfc': YesNoIgnore.Ignore.value,
            'c_biocn_rna': AndOr.And.value,
            'q_prbmd_reg': DnaRnaEither.Either.value,
            'i_nasct_ftr': AndOr.And.value,
            'c_detal_grp': AndOr.And.value,
            'q_citat_rel': '',
            'c_biocn_lig': AndOr.And.value,
            'c_prbmd_enz': AndOr.And.value,
            'c_nasct_des': AndOr.And.value,
            'c_hairpin_motif': AndOr.And.value,
            'q_lnmin': '',
            'q_prbmd_str': DnaRnaEither.Either.value,
            'q_biocn_dbt': [],
            'i_prbmd_efn': AndOr.And.value,
            'q_nasct_ftr': [],
            'c_seqln': AndOr.And.value,
            'c_citat_rel': AndOr.And.value,
            'q_prbmd_ofn': [],
            'q_bs_f_op': GreaterLower.GreaterEqual.value,
            'c_namod_phs': AndOr.And.value,
            'c_prbmd_str': AndOr.And.value,
            'q_bs_count': '',
            'c_biocn_lid': AndOr.And.value,
            'q_biocn_dna': YesNoIgnore.Ignore.value,
            'c_nasct_typ': AndOr.And.value,
            'q_namod_bas': YesNoIgnore.Ignore.value,
            'c_detal_lnb': AndOr.And.value,
            'c_namod_sgr': AndOr.And.value,
            'q_prbmd_oth': DnaRnaEither.Either.value,
            'c_detal_lna': AndOr.And.value,
            'i_prbmd_rfn': AndOr.And.value,
            'q_bp_op': '',
            'i_biocn_dbt': AndOr.And.value,
            'c_seqnc': AndOr.And.value,
            'q_ndbid': '',
            'q_bp_f_count': 0.1,
            'q_bs_f_count': 0.1,
            'q_biocn_lnm': '',
            'q_bph_f_count': 0.1,
            'q_lnmax': '',
            'q_pdbid': '',
            'q_bph_op': '',
            'c_bph_f_count': AndOr.And.value,
            'i_int_motif': AndOr.Or.value,
            'q_detal_rfc': RFactor.Empty.value,
            'chkAllStructure': 'on',
            'repType': 'csv'
        })

    def set_dna(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets dna in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_biocn_dna'] = and_or.value
        self._options['q_biocn_dna'] = yes_no_ignore.value

    def get_dna(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of dna options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_biocn_dna']), YesNoIgnore(self._options['q_biocn_dna'])

    def set_rna(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets rna in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_biocn_rna'] = and_or.value
        self._options['q_biocn_rna'] = yes_no_ignore.value

    def get_rna(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of rna options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_biocn_rna']), YesNoIgnore(self._options['q_biocn_rna'])

    def set_hybrid(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets hybrid in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_biocn_hyb'] = and_or.value
        self._options['q_biocn_hyb'] = yes_no_ignore.value

    def get_hybrid(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of hybrid options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_biocn_hyb']), YesNoIgnore(self._options['q_biocn_hyb'])

    def set_protein(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets protein in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_biocn_pro'] = and_or.value
        self._options['q_biocn_pro'] = yes_no_ignore.value

    def get_protein(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of protein options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_biocn_pro']), YesNoIgnore(self._options['q_biocn_pro'])

    def set_ligand(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets ligand in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_biocn_lig'] = and_or.value
        self._options['q_biocn_lig'] = yes_no_ignore.value

    def get_ligand(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of ligand options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_biocn_lig']), YesNoIgnore(self._options['q_biocn_lig'])

    def set_ligand_id(self, and_or: AndOr = AndOr.And, ligand_id: str = '') -> None:
        """Sets ligand id in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param ligand_id: ligand ID (default value = '')
        :type ligand_id: str

        :return: None
        """
        self._options['c_biocn_lid'] = and_or.value
        self._options['q_biocn_lid'] = ligand_id

    def get_ligand_id(self) -> (AndOr, str):
        """Gets tuple of ligand id options

        :return: tuple of values
        :rtype: (AndOr, str)
        """
        return AndOr(self._options['c_biocn_lid']), self._options['q_biocn_lid']

    def set_ligand_name(self, and_or: AndOr = AndOr.And, ligand_name: str = '') -> None:
        """Sets ligand name in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param ligand_name: ligand name (default value = '')
        :type ligand_name: str

        :return: None
        """
        self._options['c_biocn_lim'] = and_or.value
        self._options['q_biocn_lim'] = ligand_name

    def get_ligand_name(self) -> (AndOr, str):
        """Gets tuple of ligand name options

        :return: tuple of values
        :rtype: (AndOr, str)
        """
        return AndOr(self._options['c_biocn_lim']), self._options['q_biocn_lim']

    def set_drug(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets drug in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_biocn_drg'] = and_or.value
        self._options['q_biocn_drg'] = yes_no_ignore.value

    def get_drug(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of drug options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_biocn_drg']), YesNoIgnore(self._options['q_biocn_drg'])

    def set_drug_binding(self, and_or: AndOr = AndOr.And, *types: List[DrugBinding]) -> None:
        """Sets drug binding in options - to get it work ensure to call set_drug()!!!

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param types: list of DrugBinding that should be in query, allowed as many as you want
        :type types: List[DrugBinding]

        :return: None
        """
        self._options['i_biocn_dbt'] = and_or.value
        self._options['q_biocn_dbt'] = [x.value for x in types] if types else []

    def get_drug_binding(self) -> (AndOr, List[DrugBinding]):
        """Gets tuple of drug binding options

        :return: tuple of values
        :rtype: (AndOr, List[DrugBinding])
        """
        return AndOr(self._options['i_biocn_dbt']), [DrugBinding(x) for x in self._options['q_biocn_dbt']]

    def set_crystal_structure(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets crystal structure in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_etype_cry'] = and_or.value
        self._options['q_etype_cry'] = yes_no_ignore.value

    def get_crystal_structure(self) -> (AndOr, YesNoIgnore):
        """Gets tuple of crystal structure options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_etype_cry']), YesNoIgnore(self._options['q_etype_cry'])

    def set_structure_factors(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets structure factor available in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_etype_sfc'] = and_or.value
        self._options['q_etype_sfc'] = yes_no_ignore.value

    def get_structure_factors(self) -> (AndOr, YesNoIgnore):
        """Gets structure factor available options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_etype_sfc']), YesNoIgnore(self._options['q_etype_sfc'])

    def set_nmr(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets nmr in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_etype_nmr'] = and_or.value
        self._options['q_etype_nmr'] = yes_no_ignore.value

    def get_nmr(self) -> (AndOr, YesNoIgnore):
        """Gets nmr options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_etype_nmr']), YesNoIgnore(self._options['q_etype_nmr'])

    def set_nmr_restraints(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets nmr restraints available in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_etype_nra'] = and_or.value
        self._options['q_etype_nra'] = yes_no_ignore.value

    def get_nmr_restraints(self) -> (AndOr, YesNoIgnore):
        """Gets nmr restraints available options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_etype_nra']), YesNoIgnore(self._options['q_etype_nra'])

    def set_space_group(self, and_or: AndOr = AndOr.And, space_group: SpaceGroup = SpaceGroup.Empty) -> None:
        """Sets space group in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param space_group: space group to choose (default value = .Ignore)
        :type space_group: SpaceGroup

        :return: None
        """
        self._options['c_detal_grp'] = and_or.value
        self._options['q_detal_grp'] = space_group.value

    def get_space_group(self) -> (AndOr, SpaceGroup):
        """Gets space group options

        :return: tuple of values
        :rtype: (AndOr, SpaceGroup)
        """
        return AndOr(self._options['c_detal_grp']), SpaceGroup(self._options['q_detal_grp'])

    def set_cell_alpha(self, and_or: AndOr = AndOr.And,
                       gt_lt_eq: GreaterLowerEqual = GreaterLowerEqual.Equal,
                       value: Optional[float] = None) -> None:
        """Sets cell alpha in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param gt_lt_eq: space group to choose (default value = .Empty)
        :type gt_lt_eq: GreaterLowerEqual
        :param value: optional float alpha value (default value = None)
        :type value: Optional[float]

        :return: None
        """
        self._options['c_detal_ana'] = and_or.value
        self._options['q_detal_oaa'] = gt_lt_eq.value
        self._options['q_detal_vaa'] = value if value else ''

    def get_cell_alpha(self) -> (AndOr, GreaterLowerEqual, Optional[float]):
        """Gets cell alpha options

        :return: tuple of values
        :rtype: (AndOr, GreaterLowerEqual, Optional[float])
        """
        return AndOr(self._options['c_detal_ana']), GreaterLowerEqual(self._options['q_detal_oaa']), \
            float(self._options['q_detal_vaa']) if self._options['q_detal_vaa'] else None

    def set_cell_beta(self, and_or: AndOr = AndOr.And,
                      gt_lt_eq: GreaterLowerEqual = GreaterLowerEqual.Equal,
                      value: Optional[float] = None) -> None:
        """Sets cell beta in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param gt_lt_eq: space group to choose (default value = .Empty)
        :type gt_lt_eq: GreaterLowerEqual
        :param value: optional float beta value (default value = None)
        :type value: Optional[float]

        :return: None
        """
        self._options['c_detal_anb'] = and_or.value
        self._options['q_detal_oab'] = gt_lt_eq.value
        self._options['q_detal_vab'] = value if value else ''

    def get_cell_beta(self) -> (AndOr, GreaterLowerEqual, Optional[float]):
        """Gets cell beta options

        :return: tuple of values
        :rtype: (AndOr, GreaterLowerEqual, Optional[float])
        """
        return AndOr(self._options['c_detal_anb']), GreaterLowerEqual(self._options['q_detal_oab']), \
            float(self._options['q_detal_vab']) if self._options['q_detal_vab'] else None

    def set_cell_gamma(self, and_or: AndOr = AndOr.And,
                       gt_lt_eq: GreaterLowerEqual = GreaterLowerEqual.Equal,
                       value: Optional[float] = None) -> None:
        """Sets cell beta in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param gt_lt_eq: space group to choose (default value = .Empty)
        :type gt_lt_eq: GreaterLowerEqual
        :param value: optional float gamma value (default value = None)
        :type value: Optional[float]

        :return: None
        """
        self._options['c_detal_ang'] = and_or.value
        self._options['q_detal_oag'] = gt_lt_eq.value
        self._options['q_detal_vag'] = value if value else ''

    def get_cell_gamma(self) -> (AndOr, GreaterLowerEqual, Optional[float]):
        """Gets cell gamma options

        :return: tuple of values
        :rtype: (AndOr, GreaterLowerEqual, Optional[float])
        """
        return AndOr(self._options['c_detal_ang']), GreaterLowerEqual(self._options['q_detal_oag']), \
            float(self._options['q_detal_vag']) if self._options['q_detal_vag'] else None

    def set_cell_a(self, and_or: AndOr = AndOr.And,
                   gt_lt_eq: GreaterLowerEqual = GreaterLowerEqual.Equal,
                   value: Optional[float] = None) -> None:
        """Sets cell a angstroms in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param gt_lt_eq: space group to choose (default value = .Empty)
        :type gt_lt_eq: GreaterLowerEqual
        :param value: optional float a value in angstroms (default value = None)
        :type value: Optional[float]

        :return: None
        """
        self._options['c_detal_lna'] = and_or.value
        self._options['q_detal_ola'] = gt_lt_eq.value
        self._options['q_detal_vla'] = value if value else ''

    def get_cell_a(self) -> (AndOr, GreaterLowerEqual, Optional[float]):
        """Gets cell a options

        :return: tuple of values
        :rtype: (AndOr, GreaterLowerEqual, Optional[float])
        """
        return AndOr(self._options['c_detal_lna']), GreaterLowerEqual(self._options['q_detal_ola']), \
            float(self._options['q_detal_vla']) if self._options['q_detal_vla'] else None

    def set_cell_b(self, and_or: AndOr = AndOr.And,
                   gt_lt_eq: GreaterLowerEqual = GreaterLowerEqual.Equal,
                   value: Optional[float] = None) -> None:
        """Sets cell b angstroms in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param gt_lt_eq: space group to choose (default value = .Empty)
        :type gt_lt_eq: GreaterLowerEqual
        :param value: optional float b value in angstroms (default value = None)
        :type value: Optional[float]

        :return: None
        """
        self._options['c_detal_lnb'] = and_or.value
        self._options['q_detal_olb'] = gt_lt_eq.value
        self._options['q_detal_vlb'] = value if value else ''

    def get_cell_b(self) -> (AndOr, GreaterLowerEqual, Optional[float]):
        """Gets cell b options

        :return: tuple of values
        :rtype: (AndOr, GreaterLowerEqual, Optional[float])
        """
        return AndOr(self._options['c_detal_lnb']), GreaterLowerEqual(self._options['q_detal_olb']), \
            float(self._options['q_detal_vlb']) if self._options['q_detal_vlb'] else None

    def set_cell_c(self, and_or: AndOr = AndOr.And,
                   gt_lt_eq: GreaterLowerEqual = GreaterLowerEqual.Equal,
                   value: Optional[float] = None) -> None:
        """Sets cell c angstroms in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param gt_lt_eq: space group to choose (default value = .Empty)
        :type gt_lt_eq: GreaterLowerEqual
        :param value: optional float c value in angstroms (default value = None)
        :type value: Optional[float]

        :return: None
        """
        self._options['c_detal_lnc'] = and_or.value
        self._options['q_detal_olc'] = gt_lt_eq.value
        self._options['q_detal_vlc'] = value if value else ''

    def get_cell_c(self) -> (AndOr, GreaterLowerEqual, Optional[float]):
        """Gets cell c options

        :return: tuple of values
        :rtype: (AndOr, GreaterLowerEqual, Optional[float])
        """
        return AndOr(self._options['c_detal_lnc']), GreaterLowerEqual(self._options['q_detal_olc']), \
            float(self._options['q_detal_vlc']) if self._options['q_detal_vlc'] else None

    def set_cell_resolution(self, and_or: AndOr = AndOr.And, better_than: Optional[float] = None) -> None:
        """Sets cell resolution angstroms in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param better_than: optional float resolution value in angstroms (default value = None)
        :type better_than: Optional[float]

        :return: None
        """
        self._options['c_detal_res'] = and_or.value
        self._options['q_detal_res'] = better_than if better_than else ''

    def get_cell_resolution(self) -> (AndOr, Optional[float]):
        """Gets cell resolution options

        :return: tuple of values
        :rtype: (AndOr, Optional[float])
        """
        return AndOr(self._options['c_detal_res']), \
            float(self._options['q_detal_res']) if self._options['q_detal_res'] else None

    def set_cell_r_factor(self, and_or: AndOr = AndOr.And, r_factor: RFactor = RFactor.Empty) -> None:
        """Sets cell r factor in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param r_factor: r factor value in angstroms (default value = RFactor.Empty)
        :type r_factor: RFactor

        :return: None
        """
        self._options['c_detal_rfc'] = and_or.value
        self._options['q_detal_rfc'] = r_factor.value

    def get_cell_r_factor(self) -> (AndOr, RFactor):
        """Gets cell r factor options

        :return: tuple of values
        :rtype: (AndOr, RFactor)
        """
        return AndOr(self._options['c_detal_rfc']), RFactor(self._options['q_detal_rfc'])

    def set_ndb_id(self, ndb_id: str = '') -> None:
        """Sets NDB ID in options

        :param ndb_id: NDB ID e.g. NA2326 (default value = '')
        :type ndb_id: str

        :return: None
        """
        self._options['q_ndbid'] = ndb_id

    def get_ndb_id(self) -> str:
        """Gets NDB ID options

        :return: NDB ID
        :rtype: str
        """
        return self._options['q_ndbid']

    def set_pdb_id(self, pdb_id: str = '') -> None:
        """Sets PDB ID in options

        :param pdb_id: PDB ID e.g. 4JRC (default value = '')
        :type pdb_id: str

        :return: None
        """
        self._options['q_pdbid'] = pdb_id

    def get_pdb_id(self) -> str:
        """Gets PDB ID options

        :return: PDB ID
        :rtype: str
        """
        return self._options['q_pdbid']

    def set_author(self, and_or: AndOr = AndOr.And, author: str = '') -> None:
        """Sets authors in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param author: authors string (default value = '')
        :type author: str

        :return: None
        """
        self._options['c_authr'] = and_or.value
        self._options['q_authr'] = author

    def get_author(self) -> (AndOr, str):
        """Gets authors options

        :return: tuple of values
        :rtype: (AndOr, str)
        """
        return AndOr(self._options['c_authr']), self._options['q_authr']

    def set_publication_year(self, and_or: AndOr = AndOr.And, year: str = '') -> None:
        """Sets authors in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param year: year string (default value = '')
        :type year: str

        :return: None
        """
        self._options['c_citat_ann'] = and_or.value
        self._options['q_citat_ann'] = year

    def get_publication_year(self) -> (AndOr, str):
        """Gets year options

        :return: tuple of values
        :rtype: (AndOr, str)
        """
        return AndOr(self._options['c_citat_ann']), self._options['q_citat_ann']

    def set_released(self, and_or: AndOr = AndOr.And, since_date: Optional[date] = None) -> None:
        """Sets released since date in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param since_date: released since date (default value = None)
        :type since_date: Optional[date]

        :return: None
        """
        self._options['c_citat_rel'] = and_or.value
        self._options['q_citat_rel'] = since_date.isoformat() if since_date else ''

    def get_released(self) -> (AndOr, Optional[date]):
        """Gets released since date options

        :return: tuple of values
        :rtype: (AndOr, Optional[date])
        """
        return AndOr(self._options['c_citat_rel']), datetime.strptime(date, '%Y-$m-$d').date() \
            if self._options['q_citat_rel'] else None

    def set_base_pair(self, and_or: AndOr = AndOr.And, base_pair: BasePair = BasePair.Empty) -> None:
        """Sets RNA base pair interaction in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param base_pair: base pair interaction to set (default value = BasePair.Empty)
        :type base_pair: BasePair

        :return: None
        """
        self._options['c_bp_int'] = and_or.value
        self._options['q_bp_int'] = base_pair.value

    def get_base_pair(self) -> (AndOr, BasePair):
        """Gets RNA base pair interaction options

        :return: tuple of values
        :rtype: (AndOr, BasePair)
        """
        return AndOr(self._options['c_bp_int']), BasePair(self._options['q_bp_int'])

    def set_base_phosphate(self, and_or: AndOr = AndOr.And,
                           base_phosphate: BasePhosphate = BasePhosphate.Empty) -> None:
        """Sets RNA base phosphate interaction in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param base_phosphate: base phosphate interaction to set (default value = BasePhosphate.Empty)
        :type base_phosphate: BasePhosphate

        :return: None
        """
        self._options['c_bph_int'] = and_or.value
        self._options['q_bph_int'] = base_phosphate.value

    def get_base_phosphate(self) -> (AndOr, BasePhosphate):
        """Gets RNA base phosphate interaction options

        :return: tuple of values
        :rtype: (AndOr, BasePhosphate)
        """
        return AndOr(self._options['c_bph_int']), BasePhosphate(self._options['q_bph_int'])

    def set_base_stack(self, and_or: AndOr = AndOr.And, base_stack: BaseStack = BaseStack.Empty) -> None:
        """Sets RNA base stack interaction in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param base_stack: base stack interaction to set (default value = BaseStack.Empty)
        :type base_stack: BaseStack

        :return: None
        """
        self._options['c_bs_int'] = and_or.value
        self._options['q_bs_int'] = base_stack.value

    def get_base_stack(self) -> (AndOr, BaseStack):
        """Gets RNA base stack interaction options

        :return: tuple of values
        :rtype: (AndOr, BaseStack)
        """
        return AndOr(self._options['c_bs_int']), BaseStack(self._options['q_bs_int'])

    def set_base_pair_relative_freq(self, and_or: AndOr = AndOr.And, base_pair: BasePair = BasePair.Empty,
                                    gt_lt: GreaterLower = GreaterLower.GreaterEqual, freq: float = 0.1) -> None:
        """Sets RNA base pair relative frequency interaction in options \
        More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#relF

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param base_pair: base pair interaction to set (default value = BasePair.Empty)
        :type base_pair: BasePair
        :param gt_lt: greater lower for relative frequency (default value = GreaterLower.GreaterEqual)
        :type gt_lt: GreaterLower
        :param freq: relative frequency value (default value = 0.1)
        :type freq: float

        :return: None
        """
        self._options['c_bp_f_count'] = and_or.value
        self._options['q_bp_f_int'] = base_pair.value
        self._options['q_bp_f_op'] = gt_lt.value
        self._options['q_bp_f_count'] = freq

    def get_base_pair_relative_freq(self) -> (AndOr, BasePair, GreaterLower, float):
        """Gets RNA base pair relative frequency interaction options

        :return: tuple of values
        :rtype: (AndOr, BasePair, GreaterLower, float)
        """
        return AndOr(self._options['c_bp_f_count']), BasePair(self._options['q_bp_f_int']), \
            GreaterLower(self._options['q_bp_f_op']), self._options['q_bp_f_count']

    def set_base_phosphate_relative_freq(self, and_or: AndOr = AndOr.And,
                                         base_phosphate: BasePhosphate = BasePhosphate.Empty,
                                         gt_lt: GreaterLower = GreaterLower.GreaterEqual,
                                         freq: float = 0.1) -> None:
        """Sets RNA base phosphate relative frequency interaction in options. \
        More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#relF

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param base_phosphate: base phosphate interaction to set (default value = BasePhosphate.Empty)
        :type base_phosphate: BasePhosphate
        :param gt_lt: greater lower for relative frequency (default value = GreaterLower.GreaterEqual)
        :type gt_lt: GreaterLower
        :param freq: relative frequency value (default value = 0.1)
        :type freq: float

        :return: None
        """
        self._options['c_bph_f_count'] = and_or.value
        self._options['q_bph_f_int'] = base_phosphate.value
        self._options['q_bph_f_op'] = gt_lt.value
        self._options['q_bph_f_count'] = freq

    def get_base_phosphate_relative_freq(self) -> (AndOr, BasePhosphate, GreaterLower, float):
        """Gets RNA base phosphate relative frequency interaction options

        :return: tuple of values
        :rtype: (AndOr, BasePhosphate, GreaterLower, float)
        """
        return AndOr(self._options['c_bph_f_count']), BasePhosphate(self._options['q_bph_f_int']), \
            GreaterLower(self._options['q_bph_f_op']), self._options['q_bph_f_count']

    def set_base_stack_relative_freq(self, and_or: AndOr = AndOr.And, base_stack: BaseStack = BaseStack.Empty,
                                     gt_lt: GreaterLower = GreaterLower.GreaterEqual,
                                     freq: float = 0.1) -> None:
        """Sets RNA base stack relative frequency interaction in options. \
        More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#relF

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param base_stack: base phosphate interaction to set (default value = BaseStack.Empty)
        :type base_stack: BasePhosphate
        :param gt_lt: greater lower for relative frequency (default value = GreaterLower.GreaterEqual)
        :type gt_lt: GreaterLower
        :param freq: relative frequency value (default value = 0.1)
        :type freq: float

        :return: None
        """
        self._options['c_bs_f_count'] = and_or.value
        self._options['q_bs_f_int'] = base_stack.value
        self._options['q_bs_f_op'] = gt_lt.value
        self._options['q_bs_f_count'] = freq

    def get_base_stack_relative_freq(self) -> (AndOr, BaseStack, GreaterLower, float):
        """Gets RNA base stack relative frequency interaction options

        :return: tuple of values
        :rtype: (AndOr, BaseStack, GreaterLower, float)
        """
        return AndOr(self._options['c_bs_f_count']), BaseStack(self._options['q_bs_f_int']), \
            GreaterLower(self._options['q_bs_f_op']), self._options['q_bs_f_count']

    def set_internal_loop_motif(self, and_or: AndOr = AndOr.And, *motifs: List[InternalLoopMotif]) -> None:
        """Sets RNA internal loop motif in options. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#motif

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param motifs: list of InternalLoopMotif that should be in query, allowed as many as you want
        :type motifs: List[InternalLoopMotif]

        :return: None
        """
        self._options['c_int_motif'] = and_or.value
        self._options['q_int_motif'] = [x.value for x in motifs] if motifs else []

    def get_internal_loop_motif(self) -> (AndOr, List[InternalLoopMotif]):
        """Gets RNA internal loop motif options

        :return: tuple of values
        :rtype: (AndOr, List[InternalLoopMotif])
        """
        return AndOr(self._options['c_int_motif']), [InternalLoopMotif(x) for x in self._options['q_int_motif']]

    def set_hairpin_loop_motif(self, and_or: AndOr = AndOr.And, *motifs: List[HairpinLoopMotif]) -> None:
        """Sets RNA hairpin loop motif in options. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#motif
        
        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param motifs: list of HairpinLoopMotif that should be in query, allowed as many as you want
        :type motifs: List[HairpinLoopMotif]

        :return: None
        """
        self._options['c_hairpin_motif'] = and_or.value
        self._options['q_hairpin_motif'] = [x.value for x in motifs] if motifs else []

    def get_hairpin_loop_motif(self) -> (AndOr, List[HairpinLoopMotif]):
        """Gets RNA hairpin loop motif options

        :return: tuple of values
        :rtype: (AndOr, List[HairpinLoopMotif])
        """
        return AndOr(self._options['c_hairpin_motif']), [HairpinLoopMotif(x) for x in self._options['q_hairpin_motif']]

    def set_non_redundant_list(self, and_or: AndOr = AndOr.And,
                               resolution: ResolutionCutoff = ResolutionCutoff.Empty) -> None:
        """Sets RNA non redundant list cutoff in options. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#nrl

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param resolution: resolution value (default value = ResolutionCutoff.Empty)
        :type resolution: ResolutionCutoff

        :return: None
        """
        self._options['c_nr_list'] = and_or.value
        self._options['q_nr_list'] = resolution.value

    def get_non_redundant_list(self) -> (AndOr, ResolutionCutoff):
        """Gets RNA non redundant list cutoff options

        :return: tuple of values
        :rtype: (AndOr, ResolutionCutoff)
        """
        return AndOr(self._options['c_nr_list']), ResolutionCutoff(self._options['q_nr_list'])

    def set_na_pattern(self, and_or: AndOr = AndOr.And, pattern: str = '') -> None:
        """Sets nucleic acid sequence pattern in options.

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param pattern: pattern value (default value = '')
        :type pattern: str

        :return: None
        """
        self._options['c_seqnc'] = and_or.value
        self._options['q_seqnc'] = pattern

    def get_na_pattern(self) -> (AndOr, str):
        """Gets nucleic acid sequence pattern options

        :return: tuple of values
        :rtype: (AndOr, str)
        """
        return AndOr(self._options['c_seqnc']), self._options['q_seqnc']

    def set_oligo_seq_between(self, and_or: AndOr = AndOr.And, from_len: Optional[int] = None,
                              to_len: Optional[int] = None) -> None:
        """Sets oligonucleotide between "from_len" to "to_len" in options.

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param from_len: from oligonucleotide value (default value = None)
        :type from_len: Optional[int]
        :param to_len: to oligonucleotide value (default value = None)
        :type to_len: Optional[int]

        :return: None
        """
        self._options['c_seqln'] = and_or.value
        self._options['q_lnmin'] = from_len if from_len else ''
        self._options['q_lnmax'] = to_len if to_len else ''

    def get_oligo_seq_between(self) -> (AndOr, Optional[int], Optional[int]):
        """Gets oligonucleotide between options

        :return: tuple of values
        :rtype: (AndOr, Optional[int], Optional[int])
        """
        return AndOr(self._options['c_seqln']), \
            int(self._options['q_lnmin']) if self._options['q_lnmin'] else None, \
            int(self._options['q_lnmax']) if self._options['q_lnmax'] else None

    def set_base(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets nucleic acid modification base in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_namod_bas'] = and_or.value
        self._options['q_namod_bas'] = yes_no_ignore.value

    def get_base(self) -> (AndOr, YesNoIgnore):
        """Gets nucleic acid modification base options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_namod_bas']), YesNoIgnore(self._options['q_namod_bas'])

    def set_sugar(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets nucleic acid modification sugar in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_namod_sgr'] = and_or.value
        self._options['q_namod_sgr'] = yes_no_ignore.value

    def get_sugar(self) -> (AndOr, YesNoIgnore):
        """Gets nucleic acid modification sugar options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_namod_sgr']), YesNoIgnore(self._options['q_namod_sgr'])

    def set_phosphate(self, and_or: AndOr = AndOr.And, yes_no_ignore: YesNoIgnore = YesNoIgnore.Ignore) -> None:
        """Sets nucleic acid modification phosphate in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param yes_no_ignore: tells if it should 'be', 'not be' or 'be ignored' in query (default value = .Ignore)
        :type yes_no_ignore: YesNoIgnore

        :return: None
        """
        self._options['c_namod_phs'] = and_or.value
        self._options['q_namod_phs'] = yes_no_ignore.value

    def get_phosphate(self) -> (AndOr, YesNoIgnore):
        """Gets nucleic acid modification phosphate options

        :return: tuple of values
        :rtype: (AndOr, YesNoIgnore)
        """
        return AndOr(self._options['c_namod_phs']), YesNoIgnore(self._options['q_namod_phs'])

    def set_enzyme_binding(self, and_or: AndOr = AndOr.And, dna_rna_either: DnaRnaEither = DnaRnaEither.Either,
                           func_clause: AndOr = AndOr.And, *functions: List[EnzymeFunction]) -> None:
        """Sets enzyme bindings functions in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param dna_rna_either: tells if it should be 'dna', 'rna' or 'either' in query (default value = .Either)
        :type dna_rna_either: DnaRnaEither
        :param func_clause: connector between functions in query
        :type func_clause: AndOr
        :param functions: list of EnzymeFunction that should be in query, allowed as many as you want
        :type functions: List[EnzymeFunction]

        :return: None
        """
        self._options['c_prbmd_enz'] = and_or.value
        self._options['q_prbmd_enz'] = dna_rna_either.value
        self._options['i_prbmd_efn'] = func_clause.value
        self._options['q_prbmd_efn'] = [x.value for x in functions] if functions else []

    def get_enzyme_binding(self) -> (AndOr, DnaRnaEither, AndOr, List[EnzymeFunction]):
        """Gets enzyme bindings functions options

        :return: tuple of values
        :rtype: (AndOr, DnaRnaEither, AndOr, List[EnzymeFunction])
        """
        return AndOr(self._options['c_prbmd_enz']), DnaRnaEither(self._options['q_prbmd_enz']), \
            AndOr(self._options['i_prbmd_efn']), [EnzymeFunction(x) for x in self._options['q_prbmd_efn']]

    def set_regulatory_binding(self, and_or: AndOr = AndOr.And, dna_rna_either: DnaRnaEither = DnaRnaEither.Either,
                               func_clause: AndOr = AndOr.And, *functions: List[RegulatoryFunction]) -> None:
        """Sets regulatory bindings functions in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param dna_rna_either: tells if it should be 'dna', 'rna' or 'either' in query (default value = .Either)
        :type dna_rna_either: DnaRnaEither
        :param func_clause: connector between functions in query
        :type func_clause: AndOr
        :param functions: list of RegulatoryFunction that should be in query, allowed as many as you want
        :type functions: List[RegulatoryFunction]

        :return: None
        """
        self._options['c_prbmd_reg'] = and_or.value
        self._options['q_prbmd_reg'] = dna_rna_either.value
        self._options['i_prbmd_rfn'] = func_clause.value
        self._options['q_prbmd_rfn'] = [x.value for x in functions] if functions else []

    def get_regulatory_binding(self) -> (AndOr, DnaRnaEither, AndOr, List[RegulatoryFunction]):
        """Gets regulatory bindings functions options

        :return: tuple of values
        :rtype: (AndOr, DnaRnaEither, AndOr, List[RegulatoryFunction])
        """
        return AndOr(self._options['c_prbmd_reg']), DnaRnaEither(self._options['q_prbmd_reg']), \
            AndOr(self._options['i_prbmd_rfn']), [RegulatoryFunction(x) for x in self._options['q_prbmd_rfn']]

    def set_structural_binding(self, and_or: AndOr = AndOr.And, dna_rna_either: DnaRnaEither = DnaRnaEither.Either,
                               func_clause: AndOr = AndOr.And, *functions: List[StructuralFunction]) -> None:
        """Sets structural bindings functions in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param dna_rna_either: tells if it should be 'dna', 'rna' or 'either' in query (default value = .Either)
        :type dna_rna_either: DnaRnaEither
        :param func_clause: connector between functions in query
        :type func_clause: AndOr
        :param functions: list of StructuralFunction that should be in query, allowed as many as you want
        :type functions: List[StructuralFunction]

        :return: None
        """
        self._options['c_prbmd_str'] = and_or.value
        self._options['q_prbmd_str'] = dna_rna_either.value
        self._options['i_prbmd_sfn'] = func_clause.value
        self._options['q_prbmd_sfn'] = [x.value for x in functions] if functions else []

    def get_structural_binding(self) -> (AndOr, DnaRnaEither, AndOr, List[StructuralFunction]):
        """Gets structural bindings functions options

        :return: tuple of values
        :rtype: (AndOr, DnaRnaEither, AndOr, List[StructuralFunction])
        """
        return AndOr(self._options['c_prbmd_str']), DnaRnaEither(self._options['q_prbmd_str']), \
            AndOr(self._options['i_prbmd_sfn']), [StructuralFunction(x) for x in self._options['q_prbmd_sfn']]

    def set_other_binding(self, and_or: AndOr = AndOr.And, dna_rna_either: DnaRnaEither = DnaRnaEither.Either,
                          func_clause: AndOr = AndOr.And, *functions: List[OtherFunction]) -> None:
        """Sets other bindings functions in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param dna_rna_either: tells if it should be 'dna', 'rna' or 'either' in query (default value = .Either)
        :type dna_rna_either: DnaRnaEither
        :param func_clause: connector between functions in query
        :type func_clause: AndOr
        :param functions: list of OtherFunction that should be in query, allowed as many as you want
        :type functions: List[OtherFunction]

        :return: None
        """
        self._options['c_prbmd_oth'] = and_or.value
        self._options['q_prbmd_oth'] = dna_rna_either.value
        self._options['i_prbmd_ofn'] = func_clause.value
        self._options['q_prbmd_ofn'] = [x.value for x in functions] if functions else []

    def get_other_binding(self) -> (AndOr, DnaRnaEither, AndOr, List[OtherFunction]):
        """Gets other bindings functions options

        :return: tuple of values
        :rtype: (AndOr, DnaRnaEither, AndOr, List[OtherFunction])
        """
        return AndOr(self._options['c_prbmd_oth']), DnaRnaEither(self._options['q_prbmd_oth']), \
            AndOr(self._options['i_prbmd_ofn']), [OtherFunction(x) for x in self._options['q_prbmd_ofn']]

    def set_na_features(self, and_or: AndOr = AndOr.And, func_clause: AndOr = AndOr.And,
                        *features: List[NaFeature]) -> None:
        """Sets nucleic acid features in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param func_clause: connector between features in query
        :type func_clause: AndOr
        :param features: list of NaFeature that should be in query, allowed as many as you want
        :type features: List[NaFeature]

        :return: None
        """
        self._options['c_nasct_ftr'] = and_or.value
        self._options['i_nasct_ftr'] = func_clause.value
        self._options['q_nasct_ftr'] = [x.value for x in features] if features else []

    def get_na_features(self) -> (AndOr, AndOr, List[NaFeature]):
        """Gets nucleic acid features options

        :return: tuple of values
        :rtype: (AndOr, AndOr, List[NaFeature])
        """
        return AndOr(self._options['c_nasct_ftr']), AndOr(self._options['i_nasct_ftr']), \
            [NaFeature(x) for x in self._options['q_nasct_ftr']]

    def set_strand_desc(self, and_or: AndOr = AndOr.And, *descriptions: List[StrandDescription]) -> None:
        """Sets nucleic acid strand description in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param descriptions: list of StrandDescription that should be in query, allowed as many as you want
        :type descriptions: List[StrandDescription]

        :return: None
        """
        self._options['c_nasct_des'] = and_or.value
        self._options['q_nasct_des'] = [x.value for x in descriptions] if descriptions else []

    def get_strand_desc(self) -> (AndOr, List[StrandDescription]):
        """Gets nucleic acid strand description options

        :return: tuple of values
        :rtype: (AndOr, List[StrandDescription])
        """
        return AndOr(self._options['c_nasct_des']), [StrandDescription(x) for x in self._options['q_nasct_des']]

    def set_conformation(self, and_or: AndOr = AndOr.And,
                         conformation: ConformationType = ConformationType.Empty) -> None:
        """Sets nucleic acid conformation in options

        :param and_or: tells if it should be 'and' or 'or' in query (default value = AndOr.And)
        :type and_or: AndOr
        :param conformation: conformation value (default value = ConformationType.Empty)
        :type conformation: ConformationType

        :return: None
        """
        self._options['c_nasct_typ'] = and_or.value
        self._options['q_nasct_typ'] = conformation.value

    def get_conformation(self) -> (AndOr, ConformationType):
        """Gets nucleic acid conformation options

        :return: tuple of values
        :rtype: (AndOr, ConformationType)
        """
        return AndOr(self._options['c_nasct_typ']), ConformationType(self._options['q_nasct_typ'])

    def get_report_type(self) -> ReportType:
        """Gets report type options

        :return: report type value
        :rtype: ReportType
        """
        return ReportType(self._report_type)

    def set_statistics(self, statistics: bool = True) -> None:
        """Sets if is statistics

        :param statistics: statistics value (default value = True)
        :type statistics: bool

        :return: None
        """
        self._statistics = statistics

    def get_statistics(self) -> bool:
        """Gets advanced search if statistic

        :return: statistic true/false
        :rtype: bool
        """
        return self._statistics

    def get(self, stats: bool = False) -> dict:
        """Gets dictionary of advanced search options.

        :param stats: tells if dictionary should contain statistics
        :type stats: bool
        :return: dictionary with options
        :rtype: dict
        """
        self._options["repType"] = 'csvStat' if stats else 'csv'
        return self._options

    def __str__(self) -> str:
        return str(self._options)
