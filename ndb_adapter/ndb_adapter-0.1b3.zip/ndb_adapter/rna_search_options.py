from ndb_adapter.enums import RnaType, RnaStructures, ResolutionCutoff
from ndb_adapter.search_options import SearchOptions


class RnaSearchOptions(SearchOptions):
    """Class for rna search options"""
    def __init__(self):
        """Default constructor"""
        super().__init__('rna')
        self._update({'rnaFunc': '',
                      'seqType': RnaStructures.All.value,
                      'nrResVal': ResolutionCutoff.All.value})

    def set_rna_type(self, rna_type: RnaType= RnaType.All) -> None:
        """Sets rna type in options

        :param rna_type: rna type (default value = RnaType.All)
        :type rna_type: RnaType
        :return: None
        """
        self._update({'rnaFunc': rna_type.value})

    def get_rna_type(self) -> RnaType:
        """Gets rna type options

        :return: rna type
        :rtype: RnaType
        """
        return RnaType(self._options['rnaFunc'])

    def set_non_redundant_list(self, structures: RnaStructures = RnaStructures.All,
                               resolution: ResolutionCutoff = ResolutionCutoff.All) -> None:
        """Sets non redundant list in options. More info: http://ndbserver.rutgers.edu/ndbmodule/ndb-help.html#nrl

        :param structures: rna structures type (default value = RnaStructures.All)
        :type structures: RnaStructures
        :param resolution: resolution cutoff (default value = ResolutionCutoff.All)
        :type resolution: ResolutionCutoff
        :return: None
        """
        self._update({'seqType': structures.value,
                      'nrResVal': resolution.value})

    def get_non_redundant_list(self) -> (RnaStructures, ResolutionCutoff):
        """Gets non redundant list options

        :return: non redundant list
        :rtype: (RnaStructures, ResolutionCutoff)
        """
        return RnaStructures(self._options['seqType']), ResolutionCutoff(self._options['nrResVal'])
