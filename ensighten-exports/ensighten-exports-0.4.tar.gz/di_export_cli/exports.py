from swagger.swagger_client.apis.exportresource_api import ExportresourceApi
from swagger.swagger_client.apis.templateresource_api import TemplateresourceApi
from swagger.swagger_client.rest import ApiException
import json
import os.path
import urllib3
import certifi
from tqdm import tqdm
import shutil
import math
import time
import datetime
from apiexecutor import ApiExecutor


class Exports:
    def __init__(self, config_id, path_prefix):
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
            print 'Permissions granted'
        except ApiException as e:
            print e
            if e.status == 401:
                print "Credentials provided are not valid"
            elif e.status == 403:
                print "Permission NOT granted"
            else:
                print "Unexpected error"
                raise
        except Exception as e:
            print "Unexpected error"
            raise

    # Executes the synchronization and prints progress
    def sync_files(self, new_name, changed_name):

        try:
            export = self.executor.execute_with_retry(self.export_api.get_export_using_get, self.config_id)
            template = self.executor.execute_with_retry(self.template_api.get_template_using_get, export.template_id)
        except (ApiException, urllib3.exceptions.HTTPError) as e:
            self.handle_http_exceptions(e)
            return

        try:
            if template.type == self.TEMPLATE_TYPE_SNAPSHOT:
                self.sync_snapshot()
            else:
                self.sync_incremental(export.time_unit, new_name, changed_name)
        except urllib3.exceptions.HTTPError as e:
            print "Network error occurred, storing current state and exiting. Please rerun the command."
            print e
            return
        except ApiException:
            print 'Error occured when connecting to export service, check that your credentials are valid'
            return
        except KeyboardInterrupt:
            return
        except Exception as e:
            print "Unexpected error occurred:"
            raise

    def sync_incremental(self, time_unit, new_name, changed_name):
        try:
            offset = self.get_offset()
        except ValueError:
            print "state.json is corrupted."
            return

        total_files = 0
        total_size = 0
        results = self.executor.execute_with_retry(self.export_api.get_results_using_get, self.config_id,
                                                      offset=offset)
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

        with tqdm(total=total_size, leave=True, unit='B', unit_scale=True) as bar:

            for export_result in results.results:

                file_name_counter = 0

                if export_result.file_count > 0:

                    # Results are off wih about 300 milliseconds, adding 400 to get correct date and hours.
                    start_time = export_result.instance_start_time + datetime.timedelta(milliseconds=400)

                    time_path = 'dt=' + start_time.strftime("%Y-%m-%d")
                    if is_hourly:
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
                            file_with_url = self.executor.execute_with_retry(self.export_api.get_file_using_get,
                                                                             self.config_id, export_result.id,
                                                                             export_file.id)

                            self.download_file(path, file_with_url.content_url, file_name_counter, bar)
                            file_counter += 1
                            file_name_counter += 1

                        if updating_data:
                            updated_paths.append(time_path)
                            shutil.rmtree(path + "_old")
                        else:
                            new_paths.append(time_path)

                        self.save_offset(export_result.offset)

                    except (Exception, KeyboardInterrupt) as e:
                        self.handle_exception(updating_data, path)
                        self.write_log(updated_paths, new_paths, new_name, changed_name)
                        raise e

        self.write_log(updated_paths, new_paths, new_name, changed_name)
        print str(file_counter) + " files successfully downloaded"

    def sync_snapshot(self):

        latest_results = self.executor.execute_with_retry(self.export_api.get_results_using_get, self.config_id)
        latest_result = latest_results.results[0]
        total_size = latest_result.estimated_total_size
        total_files = latest_result.file_count

        if latest_result.data_version <= self.get_latest_data_version():
            print "Local files are up to date"
            return

        print "Downloading " + str(total_files) + " files"

        with tqdm(total=total_size, leave=True, unit='B', unit_scale=True) as bar:

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
                        file_with_url = self.executor.execute_with_retry(self.export_api.get_file_using_get,
                                                                         self.config_id, latest_result.id,
                                                                         export_file.id)
                        self.download_file(path, file_with_url.content_url, file_counter, bar)
                        file_counter += 1

                    if updating_data:
                        shutil.rmtree(path + "_old")

                    self.save_data_version(latest_result.data_version)

                except (Exception, KeyboardInterrupt) as e:
                    self.handle_exception(updating_data, path)
                    raise e

        print str(file_counter) + " files successfully downloaded"

    def download_file(self, path, file_url, file_number, bar):

        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',  # Force certificate check.
            ca_certs=certifi.where(),  # Path to the Certifi bundle.
            timeout=30.0  # wait 5 seconds if internet drops
        )

        response = http.request("GET", file_url, preload_content=False)

        CHUNK = 16 * 1024

        file_path = os.path.join(path, 'data' + '-' + str(file_number))
        with open(file_path, 'w+') as file_on_disk:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                file_on_disk.write(chunk)
                bar.update(len(chunk))

    def handle_exception(self, updating_data, path):
        if updating_data:
            if os.path.exists(path + "_old"):
                shutil.rmtree(path)
                os.rename(path + "_old", path)
        elif os.path.exists(path):
            shutil.rmtree(path)

    def write_log(self, updated_paths, new_paths, new_files_log_name, changed_files_log_name):
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
                raise

        if isinstance(exception, urllib3.exceptions.HTTPError):
            print "Could not connect, check internet connection"
            print exception

    # will return 0 if no last id
    def get_offset(self):
        return self.get_stored_state("offset")

    def save_offset(self, new_state):
        with open(os.path.join(self.path_prefix, self.STATE_FILE_NAME), 'w+') as state_file:
            json.dump({'offset': new_state}, state_file)

    # will return 0 if no last id
    def get_latest_data_version(self):
        return self.get_stored_state("data_version")

    def save_data_version(self, new_state):
        with open(os.path.join(self.path_prefix, self.STATE_FILE_NAME), 'w+') as state_file:
            json.dump({'data_version': new_state}, state_file)

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
