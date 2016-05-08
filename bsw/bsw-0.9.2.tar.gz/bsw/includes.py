"""bsw include handling functions"""

include_cache = {}


def get_include(path):
    """Get include page contents (cached)"""
    if path not in include_cache:
        full_path = os.path.join("templates", "includes", path)

        with open(full_path, "r") as include_file:
            include_file_data = include_file.read()

        include_cache[path] = include_file_data

    return include_cache[path]
