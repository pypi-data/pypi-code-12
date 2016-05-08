from ndb_adapter.enums import Polymer, ProteinFunc, ExpMethod


class SearchOptions(object):
    """Class for specific search options"""
    def __init__(self, search_type: str):
        """Default constructor

        :param search_type: search type value
        :type search_type: str
        """
        self._options = {
            'strGalType': search_type,
            'galType': 'table',
            'limit': '10',
            'start': '0',
            'polType': Polymer.All.value,
            'protFunc': ProteinFunc.All.value,
            'expMeth': ExpMethod.All.value,
            'filterTxt': ''
        }

    def _update(self, options: dict) -> None:
        """To update option dict

        :param options: options which updates dict
        :type options: dict
        :return: None
        """
        self._options.update(options)

    def set_polymer(self, polymer: Polymer= Polymer.All) -> None:
        """Sets polymer type in options

        :param polymer: polymer type (default value = Polymer.All)
        :type polymer: Polymer
        :return: None
        """
        self._options['polType'] = polymer.value

    def get_polymer(self) -> Polymer:
        """Gets polymer type options

        :return: polymer type
        :rtype: Polymer
        """
        return Polymer(self._options['polType'])

    def set_protein_func(self, protein: ProteinFunc= ProteinFunc.All) -> None:
        """Sets protein function in options

        :param protein: protein function (default value = ProteinFunc.All)
        :type protein: ProteinFunc
        :return: None
        """
        self._options['protFunc'] = protein.value

    def get_protein_func(self) -> ProteinFunc:
        """Gets protein function options

        :return: protein function
        :rtype: ProteinFunc
        """
        return ProteinFunc(self._options['protFunc'])

    def set_experimental_method(self, method: ExpMethod= ExpMethod.All) -> None:
        """Sets experimental method in options

        :param method: experimental method (default value = ExpMethod.All)
        :type method: ExpMethod
        :return: None
        """
        self._options['expMeth'] = method.value

    def get_experimental_method(self) -> ExpMethod:
        """Gets experimental method options

        :return: experimental method
        :rtype: ExpMethod
        """
        return ExpMethod(self._options['expMeth'])

    def set_filter_text(self, text: str) -> None:
        """Sets filter text in options. Use this option to narrow your results down considerably (>50% reduction)\
         using any word seen in the results page. Eg: Any author name found in the right side.

        :param text: filter text to be set
        :type text: str
        :return: None
        """
        self._options['filterTxt'] = text

    def get_filter_text(self) -> str:
        """Gets filter text options

        :return: filter text
        :rtype: str
        """
        return self._options['filterTxt']

    def get(self) -> dict:
        """Gets dictionary of options

        :return: dictionary options
        :rtype: dict
        """
        return self._options

    def __str__(self) -> str:
        return str(self._options)
