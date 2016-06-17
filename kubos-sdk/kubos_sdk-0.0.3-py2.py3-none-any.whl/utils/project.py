#!/usr/bin/python

def get_project_name():
    module_file_path = os.path.join(os.getcwd(), module_file_name)
    if os.path.isfile(module_file_path):
         with open(module_file_path, 'r') as module_file:
            data = json.load(module_file)
            name = data['name']
            return name
    else:
        return None
