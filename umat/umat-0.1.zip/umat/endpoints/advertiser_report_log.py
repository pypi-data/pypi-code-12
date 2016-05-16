# -*- coding: utf-8 -*-
from pandas import read_csv
from .advertiser_report import AdvertiserReport
from .params.filter import Field
from .params.v3 import Params
from .service.export import (
    Export,
    MatExportError
)
from .service.util import print_bold


class AdvertiserReportLog(AdvertiserReport):
    def __init__(self, *args, **kwargs):
        super(AdvertiserReportLog, self).__init__(*args, **kwargs)
        self.advertiser_id = self.config_parser.getint('export', 'advertiser_id')
        self.params = Params(self.api_key)
        self.params.filter = Field('test_profile_id').is_null()
        self.export_limit = self.config_parser.getint('export', 'limit')
        self.export_delay = self.config_parser.getint('export', 'delay')
        self.export_timeout = self.config_parser.getint('export', 'timeout')
        self.export = Export(
            self.export_url,
            self.params,
            self.export_limit,
            self.export_delay,
            self.export_timeout
        )

    def get_dataframe(self):
        df = read_csv(self.export.csv_url)
        df_len = len(df.index)
        if __debug__:
            print_bold('DataFrame length: {}'.format(df_len))
        if df_len >= self.export_limit:
            raise MatExportError(
                'Number of results exceeds the limit. '
                'The data are incomplete. '
                'Increase the limit parameter or request data for a lesser period.'
            )
        return df
