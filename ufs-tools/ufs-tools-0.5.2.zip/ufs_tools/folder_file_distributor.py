import os
from ufs_tools.folder_file_processor import FolderFileProcessor


class FolderFileDistributor(FolderFileProcessor):
    def __init__(self, files_folder, distribute_cmd):
        super(FolderFileDistributor, self).__init__(files_folder)
        self.distribute_cmd = distribute_cmd

    def process_file(self, full_path):
        os.system("%s %s" % (self.distribute_cmd, full_path))

