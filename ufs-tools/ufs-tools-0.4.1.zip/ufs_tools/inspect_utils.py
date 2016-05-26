import inspect


def get_inspection_frame(frame_index):
    frame = inspect.getouterframes(inspect.currentframe())
    caller_frame = frame[frame_index]
    source_file_full_path_attr_index = 1
    caller_file = caller_frame[source_file_full_path_attr_index]
    return caller_file


def get_parent_frame_file():
    frame_index = 2
    return get_inspection_frame(frame_index)


def class_enumerator(module_instance, exclude_name_list=[]):
    for name, obj in inspect.getmembers(module_instance):
        if inspect.isclass(obj):
            if name in exclude_name_list:
                continue
            yield obj