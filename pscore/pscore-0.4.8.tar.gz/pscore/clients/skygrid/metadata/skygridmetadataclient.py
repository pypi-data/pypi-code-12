from ....config.test_configuration import TestConfiguration as config
import requests
import json

STD_JSON_HEADER = {'Content-type': 'application/json', 'Accept': 'text/plain'}
TIMEOUT = 30


class SkyGridMetaDataClient:
    def __init__(self, logger):
        self.metadata_service_url = config.get_skygrid_service_url()
        self.logger = logger

    def _handle_response_status_code(self, code):
        if code != 200:
            self.logger.warn(
                "Skygrid Metadata service responded with {}, there may be data missing in your report".format(code))

    def get_test_report_uri(self, session):
        url = "{}/report/{}".format(self.metadata_service_url, session)
        return str(url)

    def get_test_run_report_uri(self, run_id):
        url = "{}/reports/{}".format(self.metadata_service_url, run_id)
        return str(url)

    def upload_test_details(self, test_details):
        url = "{}/upload/testdetails".format(self.metadata_service_url)
        response = requests.post(url, data=test_details, headers=STD_JSON_HEADER, timeout=TIMEOUT)
        self._handle_response_status_code(response.status_code)

    def upload_video(self, video):
        url = "{}/upload/video".format(self.metadata_service_url)
        response = requests.post(url, data=video, headers=STD_JSON_HEADER, timeout=TIMEOUT)
        self._handle_response_status_code(response.status_code)

    def upload_log(self, log):
        url = "{}/upload/log".format(self.metadata_service_url)
        response = requests.post(url, data=log, headers=STD_JSON_HEADER)
        self._handle_response_status_code(response.status_code)

    def upload_screenshot(self, screenshot):
        url = "{}/upload/screenshot".format(self.metadata_service_url)
        response = requests.post(url, data=screenshot, headers=STD_JSON_HEADER, timeout=TIMEOUT)
        self._handle_response_status_code(response.status_code)

    def upload_screenshots(self, screenshots):
        url = "{}/upload/screenshots".format(self.metadata_service_url)
        screenshots = json.dumps(screenshots)
        response = requests.post(url, data=screenshots, headers=STD_JSON_HEADER, timeout=TIMEOUT)
        self._handle_response_status_code(response.status_code)

