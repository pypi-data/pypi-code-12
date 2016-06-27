import requests

_HEADER_NAME = 'User-Data'


def get_users_data(ids, endpoint_url, profiles=True):
    """
    From a list of user_ids, extracts the profile and entity data for each of them.
    :param ids: List of ids
    :param endpoint_url: URL used to fetch data.
    :param profiles: True if the ids are profiles ids. False if they are entities ids.
    :return: dict where the values will have the structure {'profile': {...}, 'entity': {...}} and the
    keys will be the profiles ids if profile=True, and {'profiles': [{...}, ...], 'entity': {...}} and the keys will
    be the entities ids if profile=False
    """
    assert isinstance(ids, list) and all(isinstance(user_id, str) for user_id in ids), \
        "Input must be of type list(str)."

    # First, we ask for the profiles.
    ids = list(set(ids))  # We remove any duplicates
    r = requests.get(endpoint_url, params={'id': ids})

    if r.status_code == 200:
        results_data = r.json()['data']
        results_retrieved = len(results_data)
        number_of_expected_results = len(ids)

        if results_retrieved != number_of_expected_results:
            raise Exception("Expected %d results corresponding to %d input ids, but only received %d "
                            "results instead." % (
                            number_of_expected_results, number_of_expected_results, results_retrieved))

        try:
            if profiles:
                results = {}

                for p in results_data:
                    entity = p['entity']
                    del p['entity']
                    profile = p
                    results[profile['_id']] = {'entity': entity, 'profile': profile}

                return results
            else:
                results = {}

                for e in results_data:
                    profiles = e['profiles']
                    del e['profiles']
                    entity = e
                    results[entity['_id']] = {'entity': entity, 'profiles': profiles}

                return results
        except Exception as e:
            message = """"
            An Exception happened trying to obtain the data for the following ids: %s

             Possible causes:
             - Bad endpoint: The endpoint provided is %s.
             - Trying to parse /profiles?ids=... response when profiles=False.
             - Trying to parse /entities?ids=...&profiles=true when profiles=True

             These are the input parameters:
             - ids: %s
             - endpoint_url: %s
             - profiles: %s

             Exception message:
                %s
            """ % (str(ids), endpoint_url, str(ids), endpoint_url, str(profiles), e)
            raise Exception(message)

    else:
        raise Exception('Server responded with status %d and message %s' % (r.status_code, r.json()['message']))


def perform_calculations(auction, calculations_url):
    """
    Performs calculations on an auction object.
    :param auction: Object to be decorated with calculations.
    :param calculations_url: URL used to ask for the calculations.
    """
    try:
        r = requests.post(calculations_url, json=auction)

        if r.status_code == 200:
            return r.json()['data']['auction']
        else:
            raise Exception("Server responded with status %d" % r.status_code)
    except Exception as e:
        message = """
             A problem occurred trying to calculate the auction.

             Possible causes:
             - Wrong structure of the auction.
             - Bad endpoint.

             Input parameters:
             - Auction: %s
             - Endpoint: %s

             Exception message:
             %s
            """ % (str(auction), calculations_url, e)
        raise Exception(message)


def decode_user_data(request):
    """
    Extracts the user information that comes in the User-Data header.
    :param request: Request object.
    :return: User identifier, profile identifier and a list of the user's privileges.
    """
    import base64
    _MIN_NUMBER_OF_HEADER_COMPONENTS = 3

    # request must be a flask.request proxy object.

    header_data = request.headers.get(_HEADER_NAME)

    if not header_data:
        raise Exception("%s header wasn't found" % _HEADER_NAME)

    # We already know data comes encoded in Base64, so we proceed to decode it.
    decoded_data = base64.b64decode(header_data.encode('ascii')).decode('ascii')

    # Each data element is separated by "::"
    components = decoded_data.strip().split("::")

    if len(components) < _MIN_NUMBER_OF_HEADER_COMPONENTS:
        raise Exception('Expected at least %d elements, but few received.' % _MIN_NUMBER_OF_HEADER_COMPONENTS)

    user_id = components[0]
    profile_id = components[1]
    privileges = components[2:]

    return user_id, profile_id, privileges

