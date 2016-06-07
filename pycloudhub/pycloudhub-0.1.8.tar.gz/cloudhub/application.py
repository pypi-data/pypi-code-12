"""
Implements the CloudHub API functionality related to a single application.
"""
import json
import time

from datetime import date, datetime, timedelta
from bigpy import DotDict

from cloudhub.common import ensure_not_blank, CloudHubApiError, CloudHubApi, datetime_to_cloudhub_format


class ApplicationDeploymentError(CloudHubApiError):
    """
    An exception thrown in case of an issue with deploying CloudHub application.
    """
    pass


class ApplicationBase(CloudHubApi):
    """
    Base class for the APIs dealing with the functionality specific to a single application
    """
    def __init__(self, user_name, password, application_name, api_base_url=None, cached_app_info=None):
        super(ApplicationBase, self).__init__(user_name, password, api_base_url)
        self.application_name = ensure_not_blank(application_name, 'Application name must not be blank')
        self._cached_app_info = cached_app_info

    def __load_app_info(self):
        error_message = 'Unable to retrieve information for application [{0}]'.format(self.application_name)
        return self._load_single(error_message=error_message)

    @property
    def app_info(self):
        if not self._cached_app_info:
            self._cached_app_info = self.__load_app_info()
        return self._cached_app_info


class SearchParameter(object):
    """
    Represents CloudHub transactions search parameter.
    """
    def __init__(self, name, value, operator):
        self.name = ensure_not_blank(name, 'The search parameter name must not be blank')
        self.value = ensure_not_blank(value, 'The search parameter value must not be blank')
        self.operator = ensure_not_blank(operator, 'The search parameter operator must not be blank')

    def to_dict(self):
        return DotDict({
            'name': self.name,
            'value': self.value,
            'operator': self.operator
        })

    @staticmethod
    def transaction_id(value, operator):
        return SearchParameter('transactionId', value, operator)

    @staticmethod
    def flow_name(value, operator):
        return SearchParameter('flowName', value, operator)

    @staticmethod
    def exception_message(value, operator):
        return SearchParameter('exceptionMessage', value, operator)

    @staticmethod
    def processing_time(value, operator):
        return SearchParameter('processingTime', value, operator)


class LogSearchCriteria(object):
    """
    A data structure used to construct the search criteria when querying application logs.
    """

    def __init__(self, **kwargs):
        self.deployment_id = None
        self.instance_id = None
        self.tenant_id = None
        self.start_time_utc = None
        self.end_time_utc = None
        self.text = None
        self.priority = None
        self.logger_name = None
        self.thread_name = None
        self.limit = None
        self.limit_msg_len = None
        self.descending = None
        self.upper_id = None
        self.lower_id = None
        for key in self.__dict__.keys():
            setattr(self, key, self.__value_or_none(key, kwargs))

    @staticmethod
    def __value_or_none(key, d):
        return d[key] if key in d else None

    @staticmethod
    def __time_to_java_timestamp(dt):
        return int(time.mktime(dt.timetuple()) * 1000)

    def to_dict(self):
        temp_dict = {}
        if self.deployment_id:
            temp_dict['deploymentId'] = self.deployment_id
        if self.instance_id:
            temp_dict['instanceId'] = self.instance_id
        if self.tenant_id:
            temp_dict['tenantId'] = self.tenant_id
        if self.start_time_utc:
            temp_dict['startTime'] = self.__time_to_java_timestamp(self.start_time_utc)
        if self.end_time_utc:
            temp_dict['endTime'] = self.__time_to_java_timestamp(self.end_time_utc)
        if self.text:
            temp_dict['text'] = self.text
        if self.priority:
            temp_dict['priority'] = self.priority
        if self.logger_name:
            temp_dict['loggerName'] = self.logger_name
        if self.thread_name:
            temp_dict['threadName'] = self.thread_name
        if self.limit:
            temp_dict['limit'] = int(self.limit)
        if self.limit_msg_len:
            temp_dict['limitMsgLen'] = int(self.limit_msg_len)
        if self.descending:
            temp_dict['descending'] = bool(self.descending)
        if self.upper_id:
            temp_dict['upperId'] = self.upper_id
        if self.lower_id:
            temp_dict['lowerId'] = self.lower_id

        return temp_dict


class CloudHubApplicationTracker(ApplicationBase):

    @property
    def _base_url(self):
        return '{0}/applications/{1}/tracking'.format(self.api_base_url, self.application_name)

    def transaction(self, transaction_id):
        return self._load_list(
            'transactions/{0}'.format(transaction_id),
            'Unable to retrieve transaction id [{0}]'.format(transaction_id)
        )

    def transactions(self, search_criteria, start_date_utc, end_date_utc, count, offset):
        query = DotDict()
        if search_criteria:
            query.searchParameters = [x.to_dict() for x in search_criteria]
        query.startDate = datetime_to_cloudhub_format(start_date_utc)
        query.endDate = datetime_to_cloudhub_format((end_date_utc if end_date_utc else datetime.utcnow()))

        params = {
            'count': count,
            'offset': offset,
            'total': True
        }
        response = self._post(path='transactions', data=json.dumps(query), params=params)
        if response.status_code == 200:
            return DotDict(response.json())
        else:
            self._handle_standard_errors(response, 'Transaction query failed')


class CloudHubApplicationScheduler(ApplicationBase):

    @property
    def _base_url(self):
        return '{0}/applications/{1}/schedules'.format(self.api_base_url, self.application_name)

    @property
    def schedules(self):
        return self._load_list(path=None)

    def modify(self, schedule_id, enabled, name=None, time_unit=None, period=None, cron_expression=None):
        payload = [{
            'id': schedule_id,
            'enabled': enabled,
        }]
        if name:
            payload[0]['name'] = name

        if time_unit or period or cron_expression:
            schedule = {}
            payload[0]['schedule'] = schedule
            if time_unit:
                schedule['timeUnit'] = time_unit
            if cron_expression:
                schedule['cronExpression'] = cron_expression
            if period:
                schedule['period'] = period

        response = self._put(data=json.dumps(payload))
        if response.status_code == 200:
            return [DotDict(x) for x in response.json()]
        else:
            self._handle_standard_errors(response, 'Schedule modification failed')

    def set_state(self, id_collection, enabled):
        payload = []
        for schedule_id in id_collection:
            schedule_payload = {
                'id': schedule_id,
                'enabled': enabled,
            }
            payload.append(schedule_payload)

        response = self._put(data=json.dumps(payload))
        if response.status_code == 200:
            return [DotDict(x) for x in response.json()]
        else:
            self._handle_standard_errors(response, 'Schedule modification failed')

    def enable(self, id_collection):
        self.set_state(id_collection, True)
        return True

    def disable(self, id_collection):
        self.set_state(id_collection, False)
        return True

    def enable_all(self):
        id_list = [x['id'] for x in self.schedules]
        return self.enable(id_list)

    def disable_all(self):
        id_list = [x['id'] for x in self.schedules]
        return self.disable(id_list)

    def run(self, schedule_id):
        payload = {}
        response = self._post(data=json.dumps(payload), path='{0}/run'.format(schedule_id))
        if response.status_code == 200:
            return True
        else:
            self._handle_standard_errors(response, 'Unable to run schedule')


class CloudHubApplicationV1(ApplicationBase):
    """
    Implements CloudHub application API V1.
    """
    @property
    def _base_url(self):
        return '{0}/applications/{1}'.format(self.api_base_url, self.application_name)

    @property
    def tracking(self):
        return CloudHubApplicationTracker(
            self.user_name,
            self.password,
            self.application_name,
            self.api_base_url,
            self._cached_app_info
        )

    @property
    def scheduling(self):
        return CloudHubApplicationScheduler(
            self.user_name,
            self.password,
            self.application_name,
            self.api_base_url,
            self._cached_app_info
        )


class CloudHubApplicationV2(ApplicationBase):
    """
    Implements CloudHub application API V2.
    """
    LOGGING_VERSION_1 = 'VERSION_1'
    LOGGING_VERSION_2 = 'VERSION_2'
    DESC = 'DESC'
    ASC = 'ASC'

    VALID_LOGGING_VERSIONS = {LOGGING_VERSION_1, LOGGING_VERSION_2}
    VALID_ORDER_BY_DATE = {DESC, ASC}

    DEFAULT_STATS_INTERVAL_MILLISECONDS = 900000

    @property
    def _base_url(self):
        return '{0}/v2/applications/{1}'.format(self.api_base_url, self.application_name)

    def find_deployments(self, order_by_date=None, logging_version=None):
        order_by_date = order_by_date if order_by_date else self.DESC
        if order_by_date not in self.VALID_ORDER_BY_DATE:
            raise ValueError('Invalid order of deployments: [{0}]'.format(order_by_date))
        if logging_version and (logging_version not in self.VALID_LOGGING_VERSIONS):
            raise ValueError('Invalid logging version: [{0}]'.format(logging_version))

        if not logging_version:
            logging_version = self.LOGGING_VERSION_2 if self.app_info.loggingNgEnabled else self.LOGGING_VERSION_1

        params = {
            'orderByDate': order_by_date,
            'loggingVersion': logging_version
        }
        result = self._load_single('/deployments', error_message='Unable to load deployments', params=params)
        return DotDict({
            'total_count': result.total,
            'deployment_list': result.data
        })

    def deployment_logs(self, deployment_id, limit=100, message_length=5000, tail=True):
        params = {
            'limit': limit,
            'limitMsgLen': message_length,
            'tail': tail
        }
        result = self._load_single(
                '/deployments/{0}/logs'.format(deployment_id),
                error_message='Unable to load deployment logs',
                params=params
        )
        return DotDict({
            'total_count': result.total,
            'log_entries': result.data
        })

    def instance_logs(self, instance_id, limit=100, message_length=5000, tail=True):
        params = {
            'limit': limit,
            'limitMsgLen': message_length,
            'tail': tail
        }
        result = self._load_single(
                '/instances/{0}/logs'.format(instance_id),
                error_message='Unable to load instance logs',
                params=params
        )
        return DotDict({
            'total_count': result.total,
            'log_entries': result.data
        })

    def instance_log_file(self, instance_id, target_file):
        """
        Downloads the entire log file associated with the instance id.
        :param instance_id: the id of the application instance (i.e. worker).
        :param target_file: the file or file-like object to receive the log file contents.
        """
        # headers = {'Accept': 'application/octet-stream'}
        self._stream_to_file(
            target_file=target_file,
            path='/instances/{0}/log-file'.format(instance_id),
            # headers=headers
        )

    def search_logs(self, search_criteria):
        response = self._post(data=json.dumps(search_criteria.to_dict()), path='logs')
        if response.status_code == 200:
            return [DotDict(x) for x in response.json()]
        else:
            self._handle_standard_errors(response, 'Log search failed')

    def find_dashboard_stats(
        self,
        start_date_utc=None,
        end_date_utc=None,
        interval=0,
        statistics=None,
        worker_ids=None
    ):
        """
        Retrieves statistics for an application or specific application workers.

        :param start_date_utc: the start UTC date and time to retrieve statistics. If not specified, defaults to
            end_date_utc - 24 hrs.
        :type start_date_utc: date
        :param end_date_utc: the end UTC date and time to retrieve statistics. If not specified, defaults to now.
        :type end_date_utc: date
        :param interval: the amount of time between samples in milliseconds. Defaults to
            DEFAULT_STATS_INTERVAL_MILLISECONDS (currently 15 minutes).
        :type interval: int
        :param statistics: specifies which statistics to retrieve. If not specified, this method retrieves
            all statistics.
        :param worker_ids: specifies which worker(s) to retrieve statistics for. Can be a list, in which case the query
            parameter gets specified multiple times to retrieve statistics for multiple workers. If not specified,
            statistics for all workers are retrieved.
        :return: the data structure representing statistics.
        """
        end_date_utc = end_date_utc if end_date_utc else datetime.utcnow()
        start_date_utc = start_date_utc if start_date_utc else end_date_utc - timedelta(hours=24)

        params = {
            'startDate': datetime_to_cloudhub_format(start_date_utc),
            'endDate': datetime_to_cloudhub_format(end_date_utc),
            'interval': interval if interval > 0 else self.DEFAULT_STATS_INTERVAL_MILLISECONDS
        }
        if statistics:
            params['statistics'] = statistics
        if worker_ids:
            params['workerIds'] = worker_ids

        return self._load_single(
            path='dashboardStats',
            error_message='Unable to retrieve dashboard statistics for application [{0}]'.format(self.application_name),
            params=params
        )

    def __deploy_file(self, f):
        """
        Deploy or re-deploy an application with the specified application file.

        :param f: a file or file-like object
        """
        response = self._post_files(path='files', files={'file': f})
        if response.status_code != 200:
            raise ApplicationDeploymentError(
                "Failed to deploy application [{0}]".format(self.application_name),
                response.status_code
            )

    def deploy_file(self, file_or_path):
        """
        Deploy or re-deploy an application with the specified application file.

        :param file_or_path: a file or file-like object or a path to a file
        """
        if isinstance(file_or_path, str) or isinstance(file_or_path, unicode):
            with open(file_or_path, mode='rb') as f:
                self.__deploy_file(f)
        else:
            assert isinstance(file_or_path, file)
            self.__deploy_file(file_or_path)


class CloudHubApplication(ApplicationBase):

    @property
    def __app_v1(self):
        return CloudHubApplicationV1(
            self.user_name,
            self.password,
            self.application_name,
            self.api_base_url,
            self._cached_app_info
        )

    @property
    def __app_v2(self):
        return CloudHubApplicationV2(
            self.user_name,
            self.password,
            self.application_name,
            self.api_base_url,
            self._cached_app_info
        )

    @property
    def tracking(self):
        return self.__app_v1.tracking

    @property
    def scheduling(self):
        return self.__app_v1.scheduling

    @property
    def deployments(self):
        return self.find_deployments()

    def find_deployments(self, order_by_date=None, logging_version=None):
        return self.__app_v2.find_deployments(order_by_date, logging_version)

    def deployment_logs(self, deployment_id, limit=100, message_length=5000, tail=True):
        return self.__app_v2.deployment_logs(deployment_id, limit, message_length, tail)

    def instance_logs(self, instance_id, limit=100, message_length=5000, tail=True):
        return self.__app_v2.instance_logs(instance_id, limit, message_length, tail)

    def instance_log_file(self, instance_id, target_file):
        """
        Downloads the entire log file associated with the instance id.
        :param instance_id: the id of the application instance (i.e. worker).
        :param target_file: the file or file-like object to receive the log file contents.
        """
        return self.__app_v2.instance_log_file(instance_id, target_file)

    def search_logs(self, search_criteria):
        return self.__app_v2.search_logs(search_criteria)

    def deploy_file(self, file_or_path):
        """
        Deploy or re-deploy an application with the specified application file.

        :param file_or_path: a file or file-like object or a path to a file
        """
        self.__app_v2.deploy_file(file_or_path)

    def find_dashboard_stats(
        self,
        start_date_utc=None,
        end_date_utc=None,
        interval=0,
        statistics=None,
        worker_ids=None
    ):
        """
        Retrieves statistics for an application or specific application workers.

        :param start_date_utc: the start UTC date and time to retrieve statistics. If not specified, defaults to
            end_date_utc - 24 hrs.
        :type start_date_utc: date
        :param end_date_utc: the end UTC date and time to retrieve statistics. If not specified, defaults to now.
        :type end_date_utc: date
        :param interval: the amount of time between samples in milliseconds. Defaults to
            DEFAULT_STATS_INTERVAL_MILLISECONDS (currently 15 minutes).
        :type interval: int
        :param statistics: specifies which statistics to retrieve. If not specified, this method retrieves
            all statistics.
        :param worker_ids: specifies which worker(s) to retrieve statistics for. Can be a list, in which case the query
            parameter gets specified multiple times to retrieve statistics for multiple workers. If not specified,
            statistics for all workers are retrieved.
        :return: the data structure representing statistics.
        """
        return self.__app_v2.find_dashboard_stats(start_date_utc, end_date_utc, interval, statistics, worker_ids)

    @property
    def dashboard_stats(self):
        """
        Retrieves all statistics for all application workers for the period of past 24 hours, sampled every
        DEFAULT_STATS_INTERVAL_MILLISECONDS (currently set to 15 minutes).
        :return: all statistics for all application workers for the period of past 24 hours, sampled every
            DEFAULT_STATS_INTERVAL_MILLISECONDS (currently set to 15 minutes).
        """
        return self.find_dashboard_stats()

    @property
    def app_info(self):
        return self.__app_v2.app_info
