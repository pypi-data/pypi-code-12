# -*- coding: utf-8 -*-
from .advertiser_report_cohort import AdvertiserReportCohort
from .service.collect import Collector
from .service.mat_data_parser import parse_actuals


class AdvertiserReportActuals(AdvertiserReportCohort):
    count_url = 'http://api.mobileapptracking.com/v2/advertiser/stats/count.json'
    find_url = 'http://api.mobileapptracking.com/v2/advertiser/stats/find.json'

    def get_dataframe(self, include_days=False):
        mat_data = self.collector.collect()
        if mat_data:
            return parse_actuals(mat_data, include_days=include_days)
