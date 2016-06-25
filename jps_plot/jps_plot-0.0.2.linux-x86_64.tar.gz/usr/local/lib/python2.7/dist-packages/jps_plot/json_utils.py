import json
import numbers


def extract_data_by_text(json_data, text_for_extraction=''):
    py_data = json.loads(json_data)
    if text_for_extraction != '':
        for elm in text_for_extraction.split('.'):
            py_data = py_data[elm]
    if isinstance(py_data, numbers.Number):
        return [[text_for_extraction, py_data]]
    return decompose_to_flat_list(py_data, text_for_extraction)


def decompose_to_flat_list(dictionary_data, parent_string=''):
    results = []
    for key, val in dictionary_data.items():
        if parent_string == '':
            label = key
        else:
            label = '{0}.{1}'.format(parent_string, key)
        if isinstance(val, numbers.Number):
            results.append([label, val])
        else:
            results.extend(decompose_to_flat_list(val, label))
    return results


def decompose_json_to_list(json_data, prefix=''):
    '''
    Example:
    >>> decompose_json_to_list('{"vel": {"linear": {"x": 0.1, "y": 0.0}, "rotation_theta": 0.5}, "pos": {"x": 0.1, "y": -0.1}}')
    "['vel.linear.x', 0.1], ['vel.linear.y', 0.0], [vel.rotation_theta, 0.5],
    [pos.x, 0.1], [pos.y, -0.1]"
    '''
    py_data = json.loads(json_data)
    return decompose_to_flat_list(py_data, prefix)
        

if __name__ == '__main__':
    j = '{"vel": {"linear": {"x": 0.1, "y": 0.0}, "rotation_theta": 0.5}, "pos": {"x": 0.1, "y": -0.1}}'
    print(extract_data_by_text(j))
    print(extract_data_by_text(j, 'vel'))
    print(extract_data_by_text(j, 'vel.linear'))
    print(extract_data_by_text(j, 'vel.linear.x'))
    print(extract_data_by_text(j, 'pos'))

    j2 = '{"vel": [0.1, -0.5]}'
    print(extract_data_by_text(j2))
    print(extract_data_by_text(j2, 'vel'))
