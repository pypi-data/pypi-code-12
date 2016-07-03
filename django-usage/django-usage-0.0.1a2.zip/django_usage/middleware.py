# -*- coding: UTF-8 -*-
"""
    Created by Régis Eduardo Crestani <regis.crestani@gmail.com> on 21/06/2016.
"""
import threading

import multiprocessing
from django.utils import timezone

from .models import RequestRawData
from .settings import DJANGO_USAGE_SETTINGS as SETTINGS


class DjangoUsageMiddleware(object):

    @staticmethod
    def _process(request, response):
        if hasattr(request, 'started_at'):
            # get name
            if hasattr(request, 'resolver_match') and request.resolver_match is not None:
                name = request.resolver_match.url_name
            else:
                name = request.path
            timedelta = timezone.now() - request.started_at
            RequestRawData.objects.db_manager(SETTINGS['DATABASE']).create(
                name=name,
                method=request.method,
                latency=(timedelta.microseconds + timedelta.seconds * 1000000) / 1000,
                size=len(response.content),
                status=response.status_code,
                user=request.user if request.user and request.user.is_authenticated() else None
            )

    @staticmethod
    def process_request(request):
        request.started_at = timezone.now()

    def process_response(self, request, response):
        parallel_mode = SETTINGS['PARALLEL_MODE']
        if parallel_mode == 1:     # THREAD MODE
            threading.Thread(target=self._process, args=(request, response)).start()
        elif parallel_mode == 2:   # PROCESS MODE
            multiprocessing.Process(target=self._process, args=(request, response)).start()
        else:
            self._process(request, response)
        return response
