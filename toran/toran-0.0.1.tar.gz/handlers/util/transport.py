import uuid


def prepare_transport(message, query, paths, request_id, verbose):
    """
    Prepares the transport message to be fed into the exchange, modify this to JSONAPI COMPLIANT
    :param string message: message of the request
    :param {} query: query string
    :param [{}] paths: array of resources and ids
    :return:
    """

    paths_dict = {}
    for resource in paths:
        paths_dict[resource['resource']] = resource['id']

    if verbose is False:
        transport = {
            '@id': request_id,
            'meta': {
                'request': {
                    'params': query,
                    'path': paths_dict
                }
            }

        }
    else:
        transport = {
            '@id': request_id,
            'meta': {
                'request': {
                    'params': query,
                    'path': paths_dict
                },
                'message': message,
                'depth': 0
            }
        }

    return transport


def prepare_error(transport, message, error, code=None, status_code=None, request_id=None):
    error_list = []
    error_element = {
        'title': message,
        'detail': str(error)
    }

    if code is not None:
        error_element['code'] = code
    if status_code is None:
        status_code = "500"
    if request_id is not None:
            transport['@id'] = request_id

    error_list.append(error_element)
    errors = {
        'error': {
            'status': status_code,
            'errors': error_list
        }
    }

    if 'meta' in transport.keys():
        del(transport['meta'])

    result = transport.copy()
    result.update(errors)
    return result

