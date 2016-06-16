# -*- coding: utf-8 -*-
from .advertiser_report_cohort import AdvertiserReportCohort
from .service.mat_data_parser import parse_actuals


class AdvertiserCampaigns(AdvertiserReportCohort):
    count_url = 'https://api.mobileapptracking.com/v2/advertiser/publishers/sub/campaigns/count.json'
    find_url = 'https://api.mobileapptracking.com/v2/advertiser/publishers/sub/campaigns/find.json'

    def get_dataframe(self, include_days=False):
        mat_data = self.collector.collect()
        if mat_data:
            return parse_actuals(mat_data)
