import zipfile
import os
from ch_solutions.util.logger import get_logger


class Zip:
    def __init__(self, name, path):
        log = get_logger('ch_solutions.archive.zip')
        try:
            self.zfile = zipfile.ZipFile(path + '/' + name + '.zip', 'w')
            log.debug("Opened " + path + '/' + name + '.zip for writing.')
        except zipfile.BadZipfile as err:
            log.error("Error creating " + name + "\n" + str(err))
            raise
        except Exception as err:
            log.error("Error creating " + name + "\n" + str(err))
            raise

    def add_file_to_zip(self, target_file):
        log = get_logger('ch_solutions.archive.zip.add_file_to_zip')
        if os.path.isfile(target_file):
            log.debug("Attempting to add " + target_file + " to archive.")
            try:
                self.zfile.write(target_file)
                log.info(target_file + " added to archive")
            except zipfile.BadZipfile as err:
                log.error("error adding " + target_file + " to archive\n" + str(err))
        else:
            self.add_folder_to_zip(target_file)

    def add_folder_to_zip(self, target_folder):
        log = get_logger('ch_solutions.archive.zip.add_folder_to_zip')
        for target_file in os.listdir(target_folder):
            full_path = os.path.join(target_folder, target_file)
            if os.path.isfile(full_path):
                log.debug("Attempting to add " + full_path + " to archive.")
                try:
                    self.zfile.write(full_path)
                    log.info(full_path + " added to archive")
                except zipfile.BadZipfile as err:
                    log.error("error adding " + full_path + " to archive\n" + str(err))
            elif os.path.isdir(full_path):
                self.add_folder_to_zip(full_path)

    def close_zip(self):
        log = get_logger('ch_solutions.archive.zip.close_zip')
        log.debug('Closing Zip File.')
        self.zfile.close()
