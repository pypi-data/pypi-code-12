import os


class FolderFileProcessor(object):
    def __init__(self, files_folder=""):
        self.files_folder = files_folder

    # noinspection PyMethodMayBeStatic
    def is_process_needed(self, file_path):
        return not ("~" in file_path)

    def process_file(self, full_path):
        self.filter_item(full_path)

    def process_files(self):
        cur_path = os.getcwd()
        data_dir = os.path.join(cur_path, self.files_folder)
        for file_path in os.listdir(data_dir):
            if self.is_process_needed(file_path):
                full_path = os.path.join(data_dir, file_path)
                if os.path.isfile(full_path):
                    print "processing:", full_path
                    self.process_file(full_path)