"""Functions for interacting with the RSCB PDB web services."""

import requests
import xml.etree.ElementTree as ElementTree
import molecupy

ROOT_URL = "http://www.rcsb.org/pdb/rest/"

advanced_search_xml = """<orgPdbQuery>
    <queryType>org.pdb.query.simple.%s</queryType>
        %s
</orgPdbQuery>"""

def query_rcsb(query_type, criteria):
    """Queries the RSCB PDB web services with a simple GET request.

    :param str query_type: The type of query to make
    :param str criteria: The criteria for this query
    :rtype: ``ElementTree`` XML element"""

    param_string = "&".join(["%s=%s" % (key, criteria[key]) for key in criteria])
    response = requests.get(
     "%s%s?%s" % (ROOT_URL, query_type, param_string)
    )
    if "xml" in response.headers["Content-Type"]:
        return ElementTree.fromstring(response.text)
    else:
        return None


def query_rcsb_advanced(query_type, criteria):
    """Queries the RSCB PDB web services  as an advanced search with a POST request.

    :param str query_type: The type of query to make
    :param str criteria: The criteria for this query
    :returns: list of ``str`` PDB codes"""

    param_elements = "\n".join(["<%s>%s</%s>" % (key, criteria[key], key) for key in criteria])
    query_xml = advanced_search_xml % (query_type, param_elements)
    response = requests.post(
     "%ssearch" % ROOT_URL,
     data=query_xml.encode(),
     headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if "problem" not in response.text.lower() and "null" not in response.text.lower():
        return response.text.split()
    else:
        return None


def ask_about_molecupy(func):
    """A decorator which, when applied to a function, will add a 'as_molecupy'
    keyword argument - if set to True this will convert any PDB codes the
    function returns to `molecuPy <http://molecupy.readthedocs.io>`_ PDB objects."""

    def new_func(*args, as_molecupy=False, **kwargs):
        pdbs = func(*args, **kwargs)
        if as_molecupy:
            return [molecupy.get_pdb_remotely(pdb) for pdb in pdbs]
        else:
            return pdbs
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    return new_func
