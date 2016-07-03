# coding=utf-8


def morph(schema, data):
    result = {}

    for key, paths in schema.items():
        if isinstance(paths, dict):
            result[key] = morph(paths, data)
            continue

        elif isinstance(paths, str):
            paths = [paths]

        for path in paths:
            value = extract(data, path)

            if value:
                result[key] = value
                break

    return result


def morph_many(schema, data):
    """Morph data list.

    :param schema: result JSON schema.
    :type schema: dict.
    :param data: JSON data.
    :type data: list.
    :results: result data.
    :rtype: list.
    """
    results = []

    for item in data:
        results.append(morph(schema, item))

    return results


def extract(data, path):
    """Extract value by path.

    :param data: JSON data.
    :type data: dict or list.
    :param path: path for search value.
    :type path: str.
    :result: found value or None.
    :rtype: type.
    """
    for key in path.split('.'):
        if isinstance(data, list):
            if key.isdigit():
                try:
                    data = data[int(key)]
                    continue
                except IndexError:
                    return None

            results = []
            last_path = path.split(key)[-1]
            key = ('.'.join((key, last_path.lstrip('.')))).strip('.')

            for item in data:
                result = extract(item, key)

                if isinstance(result, list):
                    results.extend(result)
                elif result:
                    results.append(result)

            return results

        try:
            data = data[key]
        except KeyError:
            return None

    return data
