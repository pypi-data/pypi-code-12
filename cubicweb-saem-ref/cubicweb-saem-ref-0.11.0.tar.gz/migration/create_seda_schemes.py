# coding: utf-8
"""Create concept schemes used by SEDA profile data model"""

from cubes.saem_ref.dataimport.seda import import_seda_schemes


print('-> creating SEDA concept schemes')
import_seda_schemes(cnx)

if repo.system_source.dbdriver == 'postgres':
    # massive store is used, which doesn't handle full-text indexation
    reindex_entities(['ConceptScheme', 'Concept'])
