import os.path as osp

import pytest
import pandas as pd

from serenytics.helpers import SerenyticsException


class TestDataSource(object):

    @pytest.fixture(autouse=True)
    def set_test_client(self, serenytics_client, storage_data_source):
        self._client = serenytics_client
        self._data_source = storage_data_source

        # clear the data source by reloading empty data
        self._data_source.reload_data([])

    def test_reload_data(self):
        self._data_source.reload_data([
            {'year': 2015, 'quarter': 'Q1', 'sales': 120},
            {'year': 2015, 'quarter': 'Q2', 'sales': 80},
            {'year': 2015, 'quarter': 'Q4', 'sales': 25},
            {'year': 2014, 'quarter': 'Q2', 'sales': 85},
        ])

        data = self._data_source.get_data()
        assert sorted(data.columns) == ['quarter', 'sales', 'year']
        assert sorted(data.rows) == [[u'Q1', 120, 2015],
                                     [u'Q2', 80, 2015],
                                     [u'Q2', 85, 2014],
                                     [u'Q4', 25, 2015]]

    def test_reload_data_from_array(self):
        columns = ['year', 'quarter', 'sales']
        rows = [[2015, 'Q1', 120],
                [2015, 'Q2', 80],
                [2015, 'Q4', 25],
                [2014, 'Q2', 85]]

        self._data_source.reload_data_from_array(columns, rows)

        data = self._data_source.get_data()
        assert sorted(data.columns) == ['quarter', 'sales', 'year']
        assert sorted(data.rows) == [[u'Q1', 120, 2015],
                                     [u'Q2', 80, 2015],
                                     [u'Q2', 85, 2014],
                                     [u'Q4', 25, 2015]]

    def test_reload_data_from_dataframe(self):
        columns = ['year', 'quarter', 'sales']
        rows = [[2015, 'Q1', 120],
                [2015, 'Q2', 80],
                [2015, 'Q4', 25],
                [2014, 'Q2', 85]]

        df = pd.DataFrame(rows, columns=columns)
        self._data_source.reload_data_from_dataframe(df)

        data = self._data_source.get_data()
        assert sorted(data.columns) == ['quarter', 'sales', 'year']
        assert sorted(data.rows) == [[u'Q1', 120, 2015],
                                     [u'Q2', 80, 2015],
                                     [u'Q2', 85, 2014],
                                     [u'Q4', 25, 2015]]

    def test_reload_data_from_file(self):
        this_directory = osp.dirname(osp.realpath(__file__))
        self._data_source.reload_data_from_file(osp.join(this_directory, 'data', 'sales.csv'),
                                                separator=';')

        data = self._data_source.get_data()
        assert sorted(data.columns) == ['id', 'quarter', 'sales', 'year']
        assert sorted(data.rows) == [[1, u'Q1', 120, 2015],
                                     [2, u'Q2', 80, 2015],
                                     [3, u'Q2', 85, 2014],
                                     [4, u'Q4', 25, 2015]]

        # test update data
        self._data_source.update_data_from_file(osp.join(this_directory, 'data', 'sales_v2.csv'),
                                                primary_key='id')

        data = self._data_source.get_data()
        assert sorted(data.columns) == ['id', 'quarter', 'sales', 'year']
        assert sorted(data.rows) == [[1, u'Q1', 120, 2013],
                                     [2, u'Q2', 80, 2015],
                                     [3, u'Q2', 140, 2014],
                                     [4, u'Q4', 25, 2015],
                                     [5, u'Q1', 245, 2016],
                                     [6, u'Q2', 130, 2015]]

    def test_batch(self):
        self._data_source.batch(async=False, rows_to_insert=[
            {'year': 2015, 'quarter': 'Q2', 'sales': 80},
            {'year': 2015, 'quarter': 'Q4', 'sales': 25},
        ])

        data = self._data_source.get_data()
        assert sorted(data.rows) == [[u'Q2', 80, 2015],
                                     [u'Q4', 25, 2015]]

    def test_get_data_with_error(self):
        with pytest.raises(SerenyticsException) as excinfo:
            self._data_source.get_data()
        assert 'Storage source is empty' in str(excinfo.value)
