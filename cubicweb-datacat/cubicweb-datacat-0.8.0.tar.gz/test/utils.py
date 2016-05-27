"""cubicweb-datacat test utilities"""

from mock import Mock

from cubicweb import Binary


def create_file(cnx, data, data_name=None, **kwargs):
    """Create a File entity"""
    data_name = data_name or data.decode('utf-8')
    kwargs.setdefault('data_format', u'text/plain')
    return cnx.create_entity('File', data=Binary(data),
                             data_name=data_name,
                             **kwargs)


def produce_file(cnx, resourcefeed, inputfile):
    """Simulate the production of `inputfile` by resource feed `resourcefeed`"""
    tseq = resourcefeed.transformation_script[0].transformation_sequence
    # Build a transformation process "by hand".
    with cnx.security_enabled(write=False):
        process = cnx.create_entity(
            'DataTransformationProcess',
            process_input_file=inputfile,
            process_for_resourcefeed=resourcefeed,
            transformation_sequence=tseq)
        cnx.commit()  # transformation triggered in a hook.
    return process.reverse_produced_by[0]


def mock_entity_cw_url(cnx, eid, returned_url):
    """Mock an entity's ``absolute_url()`` method by returning a given and fixed URL.

    Entity to mock is given by its eid.
    """
    entity = cnx.entity_from_eid(eid)
    entity.absolute_url = Mock(return_value=returned_url)


def mock_concept_cwuri(cnx, concept_eid, returned_url):
    """Mock a ``Concept`` entity's ``cwuri`` attribute by returning a given and fixed URL.

    Concept to mock is given by its eid.
    """
    concept = cnx.entity_from_eid(concept_eid)
    concept_mock = Mock(return_value=returned_url)

    # rdflib check if returned URI contains invalid chars; always say it does not
    def contains(self, item):
        return False

    concept_mock.__contains__ = contains
    # rdflib uses repr as string serialization
    concept_mock.__repr__ = Mock(return_value=returned_url)

    concept.absolute_url = concept_mock
    concept.cw_attr_cache['cwuri'] = concept_mock


def mediatypes_scheme(cnx, *labels):
    """Build a "dummy" media-types concept scheme to satisfy hooks on
    distribution/file media type conformance. Return concepts corresponding to
    requested `labels`.
    """
    scheme = cnx.create_entity(
        'ConceptScheme',
        cwuri=u'http://www.iana.org/assignments/media-types/media-types.xml')
    return [scheme.add_concept(label) for label in labels]
