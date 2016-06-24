from __future__ import absolute_import

from django.http import HttpResponseRedirect
from django.contrib import messages

from log_analyser.apps.log_management.models import LogFileAndReportDetail
from log_analyser.apps.log_management.utils import get_temporary_report_url


def get_report(request, *args, **kwargs):
    log_report_obj_id = kwargs['log_report_obj_id']
    log_report_obj = LogFileAndReportDetail.objects.get(id=log_report_obj_id)

    if not log_report_obj.log_report_path:
        messages.error(request, 'Report Link can not be generated. Please check S3 Bruh.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponseRedirect(get_temporary_report_url(log_report_obj.log_report_path))
