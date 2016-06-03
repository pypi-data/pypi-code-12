import requests


def get_users_data(profiles_ids, endpoint_url):
    """
    From a list of user_ids, extracts the profile and entity data for each of them.
    :param users_ids: List of user_ids (actually profile ids)
    :param profile_url: URL used to index profiles.
    :param entity_url: URL used to index entities.
    :return: List of objects with the structure {'profile': {...}, 'entity': {...}}
    """
    assert isinstance(profiles_ids, list) and all(isinstance(user_id, str) for user_id in profiles_ids), \
        "Input has to be of type list of str."

    # First, we ask for the profiles.
    r = requests.get(endpoint_url, params={'id': profiles_ids})

    if r.status_code == 200:
        users_data = r.json()['data']
        profiles_retrieved = len(users_data)
        expected_profiles = len(profiles_ids)

        if profiles_retrieved != expected_profiles:
            raise Exception("Expected %d profiles corresponding to %d input user_ids, but only received %d "
                            "profiles instead." % (expected_profiles, expected_profiles, profiles_retrieved))

        return {
            data['profile']['_id']: {
                'profile': data['profile'],
                'entity': data['profile']['entity']
            } for data in users_data}
    else:
        raise Exception('Server responded with status %d and message \"%s\"' % (r.status_code, r.json()['message']))


def perform_calculations(auction, calculations_url):
    """
    Performs calculations on an auction object.
    :param auction: Object to be decorated with calculations.
    :param calculations_url: URL used to ask for the calculations.
    """
    r = requests.post(calculations_url, json=auction)

    if r.status_code == 200:
        return r.json()['data']['auction']
    else:
        raise Exception("Server responded with status %d" % r.status_code)

