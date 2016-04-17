import sys
EntryPoints = []

def lambda_entry_point(entry_point):
    meta_info = dict()
    meta_info["func"] = entry_point.__name__
    meta_info["module"] = entry_point.__module__
    meta_info["full_name"] = "%s.%s" % (meta_info["module"] , meta_info["func"])
    EntryPoints.append(meta_info)
    return entry_point

def entry_points():
    return EntryPoints
