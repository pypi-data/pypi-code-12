import os
import csv
import json
import shutil
from tqdm import tqdm
from utils import gzopen


class Parser:

    def __init__(self, from_path, to_path, header_values, include_header):
        self.from_path = from_path
        self.to_path = to_path
        self.header_values = header_values
        self.include_header = include_header

        self.STATE_FILE_NAME = "state.json"

        csv.register_dialect('custom', delimiter=',', quoting=csv.QUOTE_MINIMAL, quotechar='"', doublequote=True)

    def parse(self):

        snapshot = self.get_snapshot()

        # Get all new and updated file paths
        lowest_dirs_sizes = self.get_current_state()

        paths_to_sync = {}
        total_size = 0
        number_of_files = 0
        for directory, size in lowest_dirs_sizes.iteritems():
            if directory in snapshot:
                if size != snapshot[directory]:
                    paths_to_sync[directory] = size
                    total_size += size
                    number_of_files += len(os.listdir(os.path.join(self.from_path, 'files', directory)))
            else:
                paths_to_sync[directory] = size
                total_size += size
                number_of_files += len(os.listdir(os.path.join(self.from_path, 'files', directory)))

        if not paths_to_sync:
            print "No new files"

        else:

            header_json = []
            header_text = ""

            first = True
            for header in self.header_values:
                if not first:
                    header_text += ','
                first = False
                if '=' not in header:
                    header_text += header
                    header_json.append(header)
                else:
                    split = header.split('=')
                    header_json.append(split[1])
                    if self.include_header:
                        header_text += split[0]

            # If converting compressed files we dont know the size after unzipping, hence use number of files instead
            if self.file_paths_contains_compressed_files(paths_to_sync.keys()):
                progress_bar = tqdm(total=number_of_files, unit='files')
                compressed = True
            else:
                progress_bar = tqdm(total=total_size, leave=True, unit='B', unit_scale=True)
                compressed = False

            # Parse files
            parsed_paths_sizes = {}
            try:
                for path in paths_to_sync.keys():
                    full_to_path = os.path.join(self.to_path, 'files', path).strip('/')
                    full_from_path = os.path.join(self.from_path, 'files', path)
                    updating = False
                    if os.path.exists(full_to_path):
                        os.rename(full_to_path, full_to_path + "_old")
                        updating = True
                    os.makedirs(full_to_path)

                    for file in os.listdir(full_from_path):
                        # Ignore hidden files
                        if not file.startswith('.'):
                             with gzopen(os.path.join(full_from_path, file)) as json_file:
                                name = chop_file_ending(file, '.gz')
                                with open(os.path.join(full_to_path, name + '.csv'), 'w+') as csv_file:
                                    csv_writer = csv.DictWriter(csv_file, header_json, dialect='custom',
                                                                    extrasaction='ignore')
                                    if self.include_header:
                                        csv_file.write(header_text + '\n')
                                    for line in json_file:
                                        parsed_json = json.loads(line)
                                        parsed_json = self.flatten_json(parsed_json)
                                        csv_writer.writerow(parsed_json)
                                        line_size = len(line)
                                        if not compressed:
                                            progress_bar.update(line_size)
                                    if compressed:
                                        progress_bar.update(1)
                    if updating:
                        shutil.rmtree(full_to_path + '_old')

                    parsed_paths_sizes[path] = paths_to_sync[path]

            except KeyboardInterrupt:
                self.handle_keyboard_interrupt(path)
                progress_bar.close()
            except Exception:
                self.handle_keyboard_interrupt(path)
                #  Add new and updated path sizes
                snapshot.update(parsed_paths_sizes)
                self.save_state(snapshot)
                progress_bar.close()
                print 'Unexpected error occured during execution:'
                raise

            # Add new and updated path sizes
            snapshot.update(parsed_paths_sizes)
            self.save_state(snapshot)
            progress_bar.close()

    def handle_keyboard_interrupt(self, current_folder):
        full_current_path = os.path.join(self.to_path, 'files', current_folder).strip('/')
        if os.path.exists(full_current_path + '_old'):
            shutil.rmtree(full_current_path)
            os.rename(full_current_path + '_old', full_current_path)
        elif os.path.exists(full_current_path):
            shutil.rmtree(full_current_path)

    def get_snapshot(self):
        if os.path.isfile(os.path.join(self.to_path, self.STATE_FILE_NAME)):
            with open(os.path.join(self.to_path, self.STATE_FILE_NAME), 'r') as state_file:
                return json.load(state_file)
        return {}

    def get_current_state(self):
        dir_with_size = {}
        first_iteration = True
        for root, dir_names, file_names in os.walk(os.path.join(self.from_path, 'files')):

            # Is snapshot and data is directly under /files
            if first_iteration and not dir_names:
                path_size = 0
                for file_name in file_names:
                    # Don't count size of hidden files
                    if not file_name.startswith('.'):
                        path_size += os.path.getsize(os.path.join(root, file_name))
                dir_with_size[''] = path_size
                return dir_with_size

            else:
                first_iteration = False
                # If no sub_directories we are at lowest level of folder structure
                if not dir_names:
                    path_size = 0
                    for file_name in file_names:
                        # Don't count size of hidden files
                        if not file_name.startswith('.'):
                            path_size += os.path.getsize(os.path.join(root, file_name))
                    # Will get last path under last files/
                    dir_with_size[root.split('files/')[-1]] = path_size

        return dir_with_size

    def save_state(self, state):
        with open(os.path.join(self.to_path, self.STATE_FILE_NAME), 'w+') as state_file:
            # for directory, size in state.iteritems():
            json.dump(state, state_file)

    def flatten_json(self,y):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '.')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '.')
                    i += 1
            else:
                out[name[:-1]] = x
                if isinstance(x, unicode):
                    out[str(name[:-1])] = x.encode('utf-8')
                else:
                    out[str(name[:-1])] = str(x)

        flatten(y)
        return out

    def file_paths_contains_compressed_files(self, paths):
        path = os.path.join(self.from_path, 'files', paths[0])
        files = os.listdir(path)
        # Dont get hidden file
        if files[0].startswith('.'):
            file = files[1]
        else:
            file = files[0]
        return file.endswith('.gz')


def chop_file_ending(file, ending):
    if file.endswith(ending):
        return file[:-len(ending)]
    return file
