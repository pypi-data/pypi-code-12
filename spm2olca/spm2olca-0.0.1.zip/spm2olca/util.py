import uuid


def as_path(*args: list) -> str:
    strings = []
    for arg in args:
        if arg is None:
            continue
        strings.append(str(arg).lower())
    return "/".join(strings)


def make_uuid(*args: list) -> str:
    path = as_path(*args)
    return str(uuid.uuid3(uuid.NAMESPACE_OID, path))


def flow_uuid(category, sub_category, name, unit):
    return make_uuid('Flow', category, sub_category, name, unit)
