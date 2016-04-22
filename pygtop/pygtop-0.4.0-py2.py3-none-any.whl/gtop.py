"""Functions for interacting with the Guide to PHARMACOLOGY web services.

Also contains GtoP constants, such as the root URL."""

import json
import requests
import warnings
warnings.filterwarnings("ignore")

ROOT_URL = "http://www.guidetopharmacology.org/services/"

STRUCTURAL_PROPERTIES = "structure"
MOLECULAR_PROPERTIES = "molecularProperties"
DATABASE_PROPERTIES = "databaseLinks"
SYNONYM_PROPERTIES = "synonyms"
COMMENT_PROPERTIES = "comments"
PRECURSOR_PROPERTIES = "precursors"


def get_json_from_gtop(query):
    """Issues a query to the GtoP web services, and returns the resulting JSON.

    If it does not get a valid response, it will try again, and if it still
    doesn't get JSON back, it will return None.

    :param str query: The query to append to the base URL.
    :return: JSON object or None"""

    warnings.filterwarnings("ignore")
    response = requests.get("%s%s" % (ROOT_URL, query))
    if response.status_code == 200 and len(response.text) > 1:
        return json.loads(response.text)
    else:
        # Try ONE more time...
        warnings.filterwarnings("ignore")
        response = requests.get("%s%s" % (ROOT_URL, query))
        if response.status_code == 200 and len(response.text) > 1:
            return json.loads(response.text)
