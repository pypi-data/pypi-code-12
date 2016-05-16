# -*- coding: utf-8 -*-
from .advertiser_report import AdvertiserReport
from .params.filter import Field
from .params.v2 import Params
from .service.collect import Collector
from .service.mat_data_parser import parse


class AdvertiserReportCohort(AdvertiserReport):
    def __init__(self, *args, **kwargs):
        super(AdvertiserReportCohort, self).__init__(*args, **kwargs)
        self.params = Params(self.api_key)
        self.params.filter = Field('test_profile_id').is_null()
        self.collector = Collector(self.params, self.count_url, self.find_url)

    def get_dataframe(self, include_days=False):
        mat_data = self.collector.collect()
        return parse(mat_data, include_days=include_days)
