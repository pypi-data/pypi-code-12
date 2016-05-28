import filecmp
import imp
import logging

import os
from StringIO import StringIO
from datetime import datetime
import dropbox
from dateutil.parser import parse
from dateutil.tz import tzlocal

log = logging.getLogger(__name__)


def get_dropbox_access_token(set_key_if_not_exists=True):
    config_folder = os.path.join(os.path.expanduser('~'), '.rabbit_backup')
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)

    config_file = os.path.join(config_folder, 'dropbox_config.py')

    if set_key_if_not_exists and not os.path.isfile(config_file):
        api_key = raw_input('no config file found, please input your dropbox access token:')
        f = open(config_file, 'w+')
        f.write("api_key='%s'\n" % api_key)
        f.close()

    if os.path.isfile(config_file):
        app_config = imp.load_source('', config_file)
        return app_config.api_key
    else:
        raise RuntimeError('No api key found!');


def remove_local_file(local_file):
    try:
        os.remove(local_file)
    except OSError:
        print '>>Warning: cannot delete local file: %s' % local_file
        pass


class BackupJob(object):
    def __init__(self, access_token, backup_remote_path, retention_days):
        self.rabbit_dropbox = RabbitDropbox(access_token)
        self.backup_remote_path = backup_remote_path
        self.retention_days = int(retention_days)
        self.account = self.rabbit_dropbox.get_user_info()

    def backup_and_clear_history_data(self, local_file_list):
        for local_file in local_file_list:
            if os.path.isfile(local_file):
                log.info('backing up: %s, to: %s@dropbox_%s' % (local_file, self.backup_remote_path, self.account['email']))
                self.rabbit_dropbox.upload_file(local_file, self.backup_remote_path, on_upload_verified=self.on_upload_verified)
            else:
                log.warn('local file is not existing: %s', local_file)


    def on_upload_verified(self, local_file):
        log.info('Upload job completed, clearing data')
        remove_local_file(local_file)
        log.info('local file deleted: %s' % local_file)
        self.rabbit_dropbox.clear_bak_files(self.backup_remote_path, self.retention_days)

    def list_all_files(self):
        self.rabbit_dropbox.list_files(self.backup_remote_path)


class RabbitDropbox(object):
    def __init__(self, access_token):
        self.dropbox_client = dropbox.client.DropboxClient(access_token)

    def get_user_info(self):
        return self.dropbox_client.account_info()

    def upload_file(self, path):
        self.dropbox_client.up

    def upload_file(self, local_file_path, remote_path, on_upload_progress=None, on_upload_completed=None,
                    on_upload_verified=None):
        local_file = open(local_file_path, 'rb')
        file_size = os.path.getsize(local_file_path)
        chunk_size = 4 * 1024 * 1024

        offset = 0
        upload_id = None

        first_block = local_file.read(chunk_size)
        current_block = first_block

        while True:
            # print "upload_id: " + str(upload_id) + "current block size: " + str(len(current_block))

            offset, upload_id = self.dropbox_client.upload_chunk(StringIO(current_block), chunk_size, offset, upload_id)
            upload_progress = float(offset) / float(file_size)
            log.info("Uploaded: %.4f, upload_id: %s, current_block_size: %s" % (upload_progress, upload_id, chunk_size))
            if on_upload_progress is not None:
                on_upload_progress(upload_progress)
                log.info("Uploaded: " + str(upload_progress), ", offset: " + str(offset))
            current_block = local_file.read(min(chunk_size, file_size - offset))

            if len(current_block) <= 0:
                break

        local_file_name = os.path.basename(local_file_path)
        remote_path = remote_path + '/' + local_file_name
        try:
            response = self.dropbox_client.commit_chunked_upload('auto/' + remote_path, upload_id, False)
            remote_path = response['path']
        except Exception as e:
            log.error("Exception happened when uploading: %s ",  e.message)
            raise e
        log.info("file uploaded: %s" % remote_path)

        if on_upload_completed is not None:
            on_upload_completed("File uploaded")

        if self.validate_upload(local_file_path, remote_path):
            if on_upload_verified is not None:
                log.info('Remote file has been verified: no difference found between remote file and local file!')
                on_upload_verified(local_file_path)
        else:
            log.error("Upload task failed! - validation failed!")
            raise OSError.InterruptedError('Validation failed!')

    def validate_upload(self, local_file_path, remote_path):
        log.info("Verifying remote file: %s with local file %s", remote_path, local_file_path)
        validate_file_path = local_file_path + '.validation'
        self.get_file(validate_file_path, remote_path)

        result = filecmp.cmp(local_file_path, validate_file_path)
        os.remove(validate_file_path)
        return result

    def get_file(self, local_path, remote_path):
        f, metadata = self.dropbox_client.get_file_and_metadata(remote_path)
        log.info('downloading: %s' % f)
        chunk_size = 512 * 1024
        with open(local_path, 'wb') as out:
            while True:
                chunk = f.read(chunk_size)
                if chunk:
                    out.write(chunk)
                else:
                    break
        log.info('file downloaded: %s' % f)

    def list_files(self, path):
        metadata = self.dropbox_client.metadata(path)

        for f in metadata['contents']:
            # print file['modified']
            log.info("File path: %s, modified on: %s" % (f['path'], f['modified']))

    def clear_bak_files(self, path, days_limit):
        print 'clearing :%s with retention days: %s '% (path, days_limit)
        metadata = self.dropbox_client.metadata(path)
        for f in metadata['contents']:
            date_modified = parse(f['modified'])
            file_age = (datetime.now(tzlocal()) - date_modified).days
            if days_limit and 0 < days_limit <= file_age:
                log.info('Deleting file: %s, last modified on: %s' % (f['path'], f['modified']))
                self.delete_file(f['path'])
            else:
                log.info('     > skipping: %s with age %s, last modified on: %s' % (f['path'], file_age, date_modified))

        log.info('clearing job completed.')

    def delete_file(self, path):
        self.dropbox_client.file_delete(path)
