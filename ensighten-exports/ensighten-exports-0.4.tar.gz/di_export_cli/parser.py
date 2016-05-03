import os
import csv
import json
import shutil
from tqdm import tqdm
import sys

class Parser:

    def __init__(self, from_path, to_path, header_values, include_header):
        self.from_path = from_path
        self.to_path = to_path
        self.header_values = header_values
        self.include_header = include_header

        self.STATE_FILE_NAME = "state.json"

        # reload(sys)
        # sys.setdefaultencoding('utf8')

        csv.register_dialect('custom', delimiter=',', quoting=csv.QUOTE_MINIMAL, quotechar='"', doublequote=True)

    def parse(self):

        unparsed_new_file_paths = []
        unparsed_changed_file_paths = []

        snapshot = self.get_snapshot()

        # Get all new and updated file paths
        lowest_dirs_sizes = self.get_current_state()

        total_size = 0
        for directory, size in lowest_dirs_sizes.iteritems():
            if directory in snapshot:
                if size != snapshot[directory]:
                    unparsed_changed_file_paths.append(directory)
                    total_size += size
            else:
                unparsed_new_file_paths.append(directory)
                total_size += size


        if not unparsed_new_file_paths and not unparsed_changed_file_paths:
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

            # Parse files
            with tqdm(total=total_size, leave=True, unit='B', unit_scale=True) as bar:
                try:
                    parsed_paths_sizes = {}
                    for path in unparsed_new_file_paths + unparsed_changed_file_paths:
                        full_to_path = os.path.join(self.to_path, 'files', path)
                        full_from_path = os.path.join(self.from_path, 'files', path)
                        updating = False
                        if os.path.exists(full_to_path):
                            os.rename(full_to_path, full_to_path + "_old")
                            updating = True
                        os.makedirs(full_to_path)

                        path_size = 0
                        for file in os.listdir(full_from_path):
                            # Ignore hidden files
                            if not file.startswith('.'):
                                with open(os.path.join(full_from_path, file), 'r') as json_file:
                                    with open(os.path.join(full_to_path, file + '.csv'), 'w+') as csv_file:
                                        csv_writer = csv.DictWriter(csv_file, header_json, dialect='custom', extrasaction='ignore')
                                        if self.include_header:
                                            csv_file.write(header_text + '\n')
                                        for line in json_file:
                                            line_size = len(line)
                                            path_size += line_size
                                            bar.update(line_size)
                                            parsed_json = json.loads(line)
                                            parsed_json = self.flatten_json(parsed_json)
                                            csv_writer.writerow(parsed_json)

                        if updating:
                            shutil.rmtree(os.path.join(self.to_path, 'files', path + '_old'))

                        parsed_paths_sizes[path] = path_size

                except KeyboardInterrupt:
                    self.handle_keyboard_interrupt(path)
                except Exception as e:
                    self.handle_keyboard_interrupt(path)
                    #  Add new and updated path sizes
                    snapshot.update(parsed_paths_sizes)
                    self.save_state(snapshot)
                    print 'Unexpected error occured during execution:'
                    raise

                #  Add new and updated path sizes
                snapshot.update(parsed_paths_sizes)
                self.save_state(snapshot)

    def handle_keyboard_interrupt(self, current_folder):
        full_current_path = os.path.join(self.to_path, 'files', current_folder)
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
        for root, dirnames, filenames in os.walk(os.path.join(self.from_path, 'files')):
            # If lowest level of folder structure
            if not dirnames:
                path_size = 0
                for file in filenames:
                    # Dont count size of hidden files
                    if not file.startswith('.'):
                        path_size += os.path.getsize(os.path.join(root, file))

                dir_with_size[root.split('files/')[1]] = path_size

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