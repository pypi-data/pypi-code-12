# -*- coding: utf-8 -*-
from .advertiser_report_cohort import AdvertiserReportCohort


class AdvertiserReportActuals(AdvertiserReportCohort):
    count_url = 'http://api.mobileapptracking.com/v2/advertiser/stats/count.json'
    find_url = 'http://api.mobileapptracking.com/v2/advertiser/stats/find.json'
