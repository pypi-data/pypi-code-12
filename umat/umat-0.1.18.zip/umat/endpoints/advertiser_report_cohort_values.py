# -*- coding: utf-8 -*-
from .advertiser_report_cohort import AdvertiserReportCohort


class AdvertiserReportCohortValues(AdvertiserReportCohort):
    # I don't like long hierarchy of properties
    count_url = 'http://api.mobileapptracking.com/v2/advertiser/stats/ltv/count.json'
    find_url = 'http://api.mobileapptracking.com/v2/advertiser/stats/ltv/find.json'
