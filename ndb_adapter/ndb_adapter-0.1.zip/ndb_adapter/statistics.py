from typing import List, Dict

from ndb_adapter.search_report import StatisticReport


class Statistics(object):
    """Class for search statistics"""
    def __init__(self):
        """Default constructor"""
        self._min = {}
        self._max = {}
        self._mean = {}
        self._std_dev = {}

    @property
    def min(self) -> Dict[str, float]:
        """Gets min statistic dictionary

        :return: min statistics
        :rtype: Dict[str, float]
        """
        return self._min

    @property
    def max(self) -> Dict[str, float]:
        """Gets max statistic dictionary

        :return: max statistics
        :rtype: Dict[str, float]
        """
        return self._max

    @property
    def mean(self) -> Dict[str, float]:
        """Gets mean statistic dictionary

        :return: mean statistics
        :rtype: Dict[str, float]
        """
        return self._mean

    @property
    def std_dev(self) -> Dict[str, float]:
        """Gets standard deviation statistic dictionary

        :return: standard deviation statistics
        :rtype: Dict[str, float]
        """
        return self._std_dev

    def set_report(self, report: List[StatisticReport]) -> None:
        """Sets statistic from report

        :param report: list of statistic report
        :type report: List[StatisticReport]
        :return: None
        """
        for row in report:
            row_dict = row.stats
            try:
                if row_dict['Stat'] == 'Min':
                    for k, v in row_dict.items():
                        self._min[k] = float(v)
                elif row_dict['Stat'] == 'Max':
                    for k, v in row_dict.items():
                        self._max[k] = float(v)
                elif row_dict['Stat'] == 'Mean':
                    for k, v in row_dict.items():
                        self._mean[k] = float(v)
                elif row_dict['Stat'] == 'Standard Deviation':
                    for k, v in row_dict.items():
                        self._std_dev[k] = float(v)
            except ValueError:
                pass

    def __str__(self):
        return "Min: " + str(self._min) + "\n" \
            "Max: " + str(self._max) + "\n" \
            "Mean: " + str(self._mean) + "\n" \
            "Standard Deviation: " + str(self._std_dev)
