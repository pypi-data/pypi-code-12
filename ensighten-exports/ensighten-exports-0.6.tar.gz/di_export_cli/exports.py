from di_export_cli.swagger.swagger_client.apis.exportresource_api import ExportresourceApi
from di_export_cli.swagger.swagger_client.apis.templateresource_api import TemplateresourceApi
from di_export_cli.swagger.swagger_client.rest import ApiException
import json
import os.path
import urllib3
from tqdm import tqdm
import shutil
import math
import urlparse
import datetime
from apiexecutor import ApiExecutor
import requests
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
import logging
from utils import setup_logger


class Exports:
    def __init__(self, config_id=None, path_prefix=None):
        self.export_api = ExportresourceApi()
        self.template_api = TemplateresourceApi()
        self.path_prefix = path_prefix
        self.config_id = config_id
        self.executor = ApiExecutor()

        # Time until we need to update file links. In seconds
        self.FILE_LINK_INVALID_TIME = 110
        self.STATE_FILE_NAME = "state.json"
        self.TEMPLATE_TYPE_SNAPSHOT = "SNAPSHOT"

    def verify(self):
        try:
            self.executor.execute_with_retry(self.export_api.get_exports_using_get)
            print 'Authentication successful'
        except ApiException as e:
            if e.status == 401:
                print "Credentials provided are not valid"
            elif e.status == 403:
                print "Authentication failed"
            else:
                print "Unexpected error"
                raise
        except Exception:
            print "Unexpected error"
            raise

    def list_exports(self):
        try:
            exports_list = self.executor.execute_with_retry(self.export_api.get_exports_using_get)
        except KeyboardInterrupt:
            return
        except:
            print "Unexpected error"
            raise

        for export in exports_list.exports:
            print export.name + '\t' + export.id

    # Executes the synchronization and prints progress
    def sync_files(self, new_name, changed_name, use_legacy_time_folders):
        setup_logger(self.path_prefix)
        logger = logging.getLogger(__name__)
        logger.info('Starting sync')
        try:
            export = self.executor.execute_with_retry(self.export_api.get_export_using_get, self.config_id)
            template = self.executor.execute_with_retry(self.template_api.get_template_using_get, export.template_id)
        except (ApiException, urllib3.exceptions.HTTPError) as e:
            logger.exception('Exception thrown')
            self.handle_http_exceptions(e)
            return
        except:
            print "Unexpected error occurred"
            logger.exception('Exception while running sync')
            return

        try:
            if template.type == self.TEMPLATE_TYPE_SNAPSHOT:
                self.sync_snapshot()
            else:
                self.sync_incremental(export.time_unit, new_name, changed_name, use_legacy_time_folders)
        except (urllib3.exceptions.HTTPError, requests.ConnectionError) as e:
            print "Network error occurred, storing current state and exiting. Please rerun the command."
            logger.exception('Exception while running sync')
        except ApiException:
            print 'Error occured when connecting to export service, check that your credentials are valid'
            logger.exception('Exception while running sync')
        except KeyboardInterrupt:
            return
        except:
            print "Unexpected error occurred"
            logger.exception('Exception while running sync')

        logger.info('Sync finished')

    def sync_incremental(self, time_unit, new_name, changed_name, use_legacy_time_folders):
        try:
            offset = self.get_offset()
        except ValueError:
            print "state.json is corrupted."
            logging.getLogger(__name__).exception('Exception while getting state')
            return

        total_files = 0
        total_size = 0
        results = self.executor.execute_with_retry(self.export_api.get_results_using_get, self.config_id, offset=offset)
        for export_result in results.results:
            total_files = total_files + export_result.file_count
            total_size = total_size + export_result.estimated_total_size

        if total_files == 0:
            print "Local files are up to date."
            return

        print "Downloading " + str(total_files) + " files"

        is_hourly = time_unit == "HOURS"

        if not changed_name:
            changed_name = 'CHANGED'
        if not new_name:
            new_name = 'NEW'

        file_counter = 0
        updated_paths = []
        new_paths = []

        with tqdm(total=total_files, leave=True, unit='file', desc='Total') as bar:

            for export_result in results.results:

                file_name_counter = 0

                if export_result.file_count > 0:

                    # Results are off wih about 300 milliseconds, adding 400 to get correct date and hours.
                    start_time = export_result.instance_start_time + datetime.timedelta(milliseconds=400)

                    time_path = 'dt=' + start_time.strftime("%Y-%m-%d")
                    if is_hourly:
                        if use_legacy_time_folders:
                            time_path = os.path.join(time_path, 'tm=' + start_time.strftime("%H") + '-00')
                        else:
                            time_path = os.path.join(time_path, 'hh=' + start_time.strftime("%H"))

                    path = os.path.join(self.path_prefix, 'files', time_path)

                    try:
                        updating_data = False

                        if os.path.exists(path):
                            updating_data = True
                            os.rename(path, path + "_old")

                        os.makedirs(path)

                        files = self.executor.execute_with_retry(self.export_api.get_files_using_get, self.config_id,
                                                                 export_result.id)

                        for export_file in files._files:

                            self.download_file(path, export_file, file_name_counter, bar, export_result)
                            bar.update(1)
                            file_counter += 1
                            file_name_counter += 1

                        if updating_data:
                            updated_paths.append(time_path)
                            shutil.rmtree(path + "_old")
                        else:
                            new_paths.append(time_path)

                        self.save_offset(export_result.offset)

                    except:
                        self.handle_exception(updating_data, path)
                        self.write_to_changed_and_new_log_file(updated_paths, new_paths, new_name, changed_name)
                        raise

        self.write_to_changed_and_new_log_file(updated_paths, new_paths, new_name, changed_name)
        print str(file_counter) + " files successfully downloaded"

    def sync_snapshot(self):

        latest_results = self.executor.execute_with_retry(self.export_api.get_results_using_get, self.config_id)
        latest_offset = latest_results.latest_offset
        latest_result = None
        for result in latest_results.results:
            if result.offset == latest_offset:
                latest_result = result
        total_size = latest_result.estimated_total_size
        total_files = latest_result.file_count

        if latest_result.offset <= self.get_offset() or latest_result.file_count == 0:
            print "Local files are up to date"
            return

        print "Downloading " + str(total_files) + " files"

        with tqdm(total=total_files, leave=True, unit='file', desc='Total') as bar:
            file_counter = 0

            if latest_result.file_count > 0:

                path = os.path.join(self.path_prefix, 'files')

                updating_data = False
                try:
                    if os.path.exists(path):
                        updating_data = True
                        os.rename(path, path + "_old")

                    os.makedirs(path)

                    files = self.executor.execute_with_retry(self.export_api.get_files_using_get, self.config_id,
                                                             latest_result.id)

                    for export_file in files._files:

                        self.download_file(path, export_file, file_counter, bar, latest_result)
                        bar.update(1)
                        file_counter += 1

                    if updating_data:
                        shutil.rmtree(path + "_old")

                    self.save_offset(latest_result.offset)

                except:
                    self.handle_exception(updating_data, path)
                    raise

                print str(file_counter) + " files successfully downloaded"

    def download_file(self, path, export_file, file_number, bar, latest_result):
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES+1):
            file_with_url = self.executor.execute_with_retry(self.export_api.get_file_using_get, self.config_id
                                                             , latest_result.id, export_file.id)
            file_url = file_with_url.content_url
            file_size = file_with_url.estimated_size

            with tqdm(total=file_size, leave=False, unit='B', unit_scale=True) as inner_bar:

                # Check if file ends with .gz, in that case, keep file ending.
                url_parts = urlparse.urlparse(file_url)
                path_parts = url_parts[2].rpartition('/')
                remote_file_name = path_parts[2]

                # zero padding of file name
                file_name = format(file_number, '06') + '_0'

                if remote_file_name.endswith('.gz'):
                    file_name += '.gz'

                file_path = os.path.join(path, file_name)
                with open(file_path, 'w+') as file_on_disk:
                    try:
                        s = requests.Session()
                        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
                        s.mount('https://', HTTPAdapter(max_retries=retries))
                        response = s.get(file_url, stream=True, timeout=(10, 300))
                        if not response.ok:
                            response.raise_for_status()
                        else:
                            for block in response.iter_content(16 * 1024):
                                file_on_disk.write(block)
                                inner_bar.update(len(block))
                    except (requests.Timeout, requests.exceptions.ChunkedEncodingError) as e:
                        logging.getLogger(__name__).exception('Retrying download file')
                        if attempt == MAX_RETRIES:
                            raise e
                        bar.write('Connection timed out, retrying last file')
                        inner_bar.close()
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        continue

                break

    def handle_exception(self, updating_data, path):
        if updating_data:
            if os.path.exists(path + "_old"):
                shutil.rmtree(path)
                os.rename(path + "_old", path)
        elif os.path.exists(path):
            shutil.rmtree(path)

    def write_to_changed_and_new_log_file(self, updated_paths, new_paths, new_files_log_name, changed_files_log_name):
        with open(os.path.join(self.path_prefix, changed_files_log_name), 'w+') as log_file:
            for path in updated_paths:
                log_file.write(path + '\n')
        with open(os.path.join(self.path_prefix, new_files_log_name), 'w+') as log_file:
            for path in new_paths:
                log_file.write(path + '\n')

    def get_info_json(self):
        data = self.get_info()
        if data is not None:
            return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def get_info_readable(self):
        data = self.get_info()

        if data is not None:
            return data['start_time'] + '  -  ' + data['end_time'] + "\nInterval: " + str(
                data['interval']) + "\nTime Unit: " + data['time_unit'] + "\nRemote data size: " + convert_size(
                data['remote_data_size']) + "\nLocal data size: " + convert_size(
                data['local_data_size']) + "\nUnsynced data size: " + convert_size(data['unsynced_data_size'])
        else:
            return ""

    def get_info(self):
        try:
            results = self.executor.execute_with_retry(self.export_api.get_results_using_get, self.config_id)
            export = self.executor.execute_with_retry(self.export_api.get_export_using_get, self.config_id)
        except (ApiException, urllib3.exceptions.HTTPError) as e:
            self.handle_http_exceptions(e)
            return
        except:
            print 'Unexpected error occurred, please rerun command'
            raise

        data = {'start_time': str(export.start_time),
                'end_time': str(export.end_time),
                'interval': export.interval,
                'time_unit': export.time_unit}

        try:
            offset = self.get_offset()
        except ValueError:
            return "state.json is not valid."

        total_size = 0
        unsynced_size = 0

        # Key: instance_start_time, Value: (data_version, estimated_total_size)
        checked_exports = {}
        for export_result in results.results:
            if checked_exports.get(export_result.instance_start_time, None) is not None:
                if export_result.data_version > checked_exports[export_result.instance_start_time][0]:
                    total_size -= checked_exports[export_result.instance_start_time][1]
                    total_size += export_result.estimated_total_size

                    if export_result.offset > offset:
                        unsynced_size -= checked_exports[export_result.instance_start_time][1]
                        unsynced_size += export_result.estimated_total_size

                    checked_exports[export_result.instance_start_time] = (export_result.data_version,
                                                                          export_result.estimated_total_size)
            else:
                checked_exports[export_result.instance_start_time] = (export_result.data_version,
                                                                      export_result.estimated_total_size)

                total_size = total_size + export_result.estimated_total_size

                if export_result.offset > offset:
                    unsynced_size += export_result.estimated_total_size

        data['remote_data_size'] = total_size
        data['unsynced_data_size'] = unsynced_size

        local_size = 0
        for root, dirs, files, in os.walk(os.path.join(self.path_prefix, 'files')):
            local_size += sum(os.path.getsize(os.path.join(root, name)) for name in files if not name.startswith('.'))

        data['local_data_size'] = local_size

        return data

    def handle_http_exceptions(self, exception):
        if isinstance(exception, ApiException):
            if exception.status == 403:
                print "API Access Denied"
            elif exception.status == 404:
                print "Export not found"
            elif exception.status == 400:
                print "Bad request, make sure to enter correct config_id"
            else:
                print "Unexpected error occurred, please rerun the command."

        if isinstance(exception, urllib3.exceptions.HTTPError):
            print "Could not connect, check internet connection"

    # will return 0 if no last id
    def get_offset(self):
        return self.get_stored_state("offset")

    def save_offset(self, new_state):
        with open(os.path.join(self.path_prefix, self.STATE_FILE_NAME), 'w+') as state_file:
            json.dump({'offset': new_state}, state_file)

    def get_stored_state(self, key):
        if os.path.isfile(os.path.join(self.path_prefix, self.STATE_FILE_NAME)):
            with open(os.path.join(self.path_prefix, self.STATE_FILE_NAME), 'r') as state_file:
                data = json.load(state_file)
                return data[key]

        return 0

def convert_size(size):
    if size == 0:
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1000)))
    p = math.pow(1000, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])
