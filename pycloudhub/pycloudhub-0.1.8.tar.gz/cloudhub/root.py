"""
Implementation of the "starting point" or "root" of the CloudHub API hierarchy.
"""
from cloudhub.application import CloudHubApplication
from cloudhub.notification import CloudHubNotification
from cloudhub.common import CloudHubApi


class CloudHub(CloudHubApi):
    """
    Encapsulates the interactions with the CloudHub Application API at the top level, i.e. a good point for
    starting interactions with the API and "drilling down" by navigating API hierarchy.
    """
    def __create_application(self, application_name, app_info=None):
        return CloudHubApplication(
            self.user_name,
            self.password,
            application_name,
            self.api_base_url,
            app_info
        )

    @property
    def applications(self):
        # app_info_list = self._load_list('/v2/applications', 'Unable to retrieve list of applications')
        # return [self.__create_application(app_info.domain, app_info) for app_info in app_info_list]
        return self._load_list('/v2/applications', 'Unable to retrieve list of applications')

    @property
    def notifications(self):
        return CloudHubNotification(
            self.user_name,
            self.password,
            self.api_base_url
        )

    def application(self, application_name):
        return self.__create_application(application_name)

