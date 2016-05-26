import requests


def get_users_data(users_ids, profile_url, entity_url):
    """
    From a list of user_ids, extracts the profile and entity data for each of them.
    :param users_ids: List of user_ids (actually profile ids)
    :param profile_url: URL used to index profiles.
    :param entity_url: URL used to index entities.
    :return: List of objects with the structure {'profile': {...}, 'entity': {...}}
    """
    assert isinstance(users_ids, list) and all(isinstance(user_id, str) for user_id in users_ids), \
        "Input has to be of type list of str."

    # First, we ask for the profiles.
    r = requests.get(profile_url, params={'id': users_ids})

    if r.status_code == 200:
        profiles = r.json()['data']
        profiles_retrieved = len(profiles)
        expected_profiles = len(users_ids)

        if profiles_retrieved != expected_profiles:
            raise Exception("Expected %d profiles corresponding to %d input user_ids, but only received %d "
                            "profiles instead." % (expected_profiles, expected_profiles, profiles_retrieved))

        # Extract entities ids from profiles.
        entities_ids = [p['entityId'] for p in profiles]
        r = requests.get(entity_url, params={'id': entities_ids})

        if r.status_code == 200:
            entities = r.json()['data']

            # Check if each profile's entity was retrieved.
            not_found_entities_ids = set(entities_ids).difference(set(e['_id'] for e in entities))
            if not_found_entities_ids != set():
                raise Exception("The following entities weren't found: %s" % str(not_found_entities_ids))

            # Store entities in a dictionary (indexed by their id) to ease their access.
            entities_dict = {e['_id']: e for e in entities}

            return [{
                        'profile': p,
                        'entity': entities_dict[p['entityId']]
                    } for p in profiles]
        else:
            raise Exception('Server responded with status %d and message \"%s\"' % (r.status_code, r.json()['message']))
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

