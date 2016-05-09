from ndb_adapter.enums import StructuralFeatures
from ndb_adapter.search_options import SearchOptions


class DnaSearchOptions(SearchOptions):
    """Class for dna search options"""
    def __init__(self):
        """Default constructor"""
        super().__init__('dna')
        self._update({'stFeature': StructuralFeatures.All.value})

    def set_structural_features(self, feature: StructuralFeatures= StructuralFeatures.All) -> None:
        """Sets structural features in options

        :param feature: structural feature (default value = StructuralFeatures.All)
        :type feature: StructuralFeatures
        :return: None
        """
        self._update({'stFeature': feature.value})

    def get_structural_features(self) -> StructuralFeatures:
        """Gets structural features options

        :return: structural feature
        :rtype: StructuralFeatures
        """
        return StructuralFeatures(self._options['stFeature'])
