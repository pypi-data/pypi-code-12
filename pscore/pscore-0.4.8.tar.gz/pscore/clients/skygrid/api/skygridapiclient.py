from pscore.clients.skygrid.metadata.skygridmetadataclient import SkyGridMetaDataClient
from pscore.config.test_configuration import TestConfiguration as config
import requests
from ..dao.data import SGScreenShot, SGVideo
from datetime import datetime


class SkyGridApiClient(object):
    """
    Interface  to interact with Skygrid services
    """
    ACTION_SCREENSHOT = '/screenshot'
    ACTION_VIDEO_DIR = '/config'

    def __init__(self, driver):
        self.hub_url = config.get_hub_url()
        self.metadata_service_url = config.get_skygrid_service_url()
        self.metadata_client = SkyGridMetaDataClient(driver.test_context.logger)
        self.logger = driver.test_context.logger
        self.session_id = driver.session_id
        self.node_ip = driver.active_node_ip_no_port()
        self.video_output_directory = self.get_video_output_directory()

    def node_api_endpoint(self, action):
        return "{}:3000{}".format(self.node_ip, action)

    @staticmethod
    def _now():
        return str(datetime.now())

    def take_screenshot(self):
        url = self.node_api_endpoint(self.ACTION_SCREENSHOT)
        try:
            response = requests.get(url)
        except:
            raise SkygridApiClientException("Could not find {}, please check you're hitting a skygrid node".format(url))

        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError as e:
                self.report_error(e.message)
                return None
            if len(data) > 0:

                try:
                    path = data['file'][0]
                except TypeError as e:
                    self.report_error(e.message)
                    return None
                now = self._now()
                return SGScreenShot(self.session_id, path, now)
            else:
                self.report_error("Empty Json")
        else:
            self.report_error(response.status_code)

    def get_video(self):
        if self.video_output_directory is None:
            raise SkygridApiClientException("video output directory was invalid")
        path = "{}\\{}.mp4".format(self.video_output_directory, self.session_id)
        return SGVideo(self.session_id, path, self._now())

    def get_video_output_directory(self):
        config_url = self.node_api_endpoint(self.ACTION_VIDEO_DIR)
        try:
            response = requests.get(config_url)
        except:
            return None

        if response.status_code == 200:

            try:
                data = response.json()
            except ValueError as e:
                return None
            if len(data) > 0:
                try:
                    directory = data['config_runtime']['theConfigMap']['video_recording_options']['video_output_dir']
                except TypeError as e:
                    self.report_error(e.message)
                    return None
                return str(directory)
            else:
                self.report_error("Empty Json")

        else:
            self.report_error(response.status_code)

    def report_error(self, message):
        msg = "Server responded with %s " % message
        self.logger.error(msg)


class SkygridApiClientException(Exception):
    pass
