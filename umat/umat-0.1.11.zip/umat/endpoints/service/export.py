from time import (
    sleep,
    time
)
from .request import (
    MatRequestError,
    request
)
from .util import print_bold


class MatExportError(MatRequestError):
    pass


class Export(object):
    def __init__(self, url, params, limit, delay, timeout):
        self.url = url
        self.params = params
        self.limit = limit
        self.delay = delay
        self.timeout = timeout

    @property
    def csv_url(self):
        export_job_status_url = self._get_export_job_status_url()
        csv_url = self._wait_csv_url(export_job_status_url)
        if csv_url:
            return csv_url
        raise MatExportError('Timeout')

    def _get_export_job_status_url(self):
        params = self.params.copy()
        params['filter'] = str(self.params.filter)
        params['limit'] = self.limit
        response_json = request(self.url, params=params)
        return response_json['export_job_status_url']

    def _wait_csv_url(self, export_job_status_url):
        elapsed_time = 0
        start = time()
        while elapsed_time < self.timeout:
            csv_url = self._check_csv_url(export_job_status_url)
            if csv_url:
                if __debug__:
                    print_bold('URL received for {:.0f} seconds'.format(elapsed_time))
                return csv_url
            sleep(self.delay)
            elapsed_time = time() - start

    def _check_csv_url(self, export_job_status_url):
        response_json = request(export_job_status_url)

        if response_json['status'] == 'fail':
            raise MatExportError(
                'Export `status` is `fail`'
            )

        if response_json['status'] == 'complete':
            if response_json['percent_complete'] != 100:
                raise MatExportError(
                    'Export `percent_complete` is {}'.format(response_json['percent_complete'])
                )
            return response_json['url']

        if __debug__:
            print_bold('Context: `{}`'.format(response_json['context']))
