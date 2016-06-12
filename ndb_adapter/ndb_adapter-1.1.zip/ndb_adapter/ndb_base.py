

class NDBBase(object):
    """Base class for NDB

    :cvar siteUrl: ndb site url
    :cvar _advancedUrl: private advanced search url
    :cvar _summaryUrl: private summary url
    :cvar _dnaUrl: private dna search url
    :cvar _rnaUrl: private rna search url
    """
    siteUrl = 'http://ndbserver.rutgers.edu'
    _advancedUrl = siteUrl + '/service/ndb/report/advSearchReport'
    _summaryUrl = siteUrl + '/service/ndb/atlas/summary'
    _dnaUrl = siteUrl + '/service/ndb/atlas/gallery/dna'
    _rnaUrl = siteUrl + '/service/ndb/atlas/gallery/rna'
    _chiralCorrectUrl = siteUrl + '/files/ftp/NDB/coordinates/na-chiral-correct/'
    _bioAssemblyCoordinateUrl = siteUrl + '/files/ftp/NDB/coordinates/na-biol/'
    _mmCifUrl = siteUrl + '/files/ftp/NDB/coordinates/na-mmcif/'
    _structureFactorsUrl = siteUrl + '/files/ftp/NDB/structure-factors/'
    _xmlCompleteUrl = siteUrl + '/files/ftp/NDB/coordinates/xml/'
    _xmlCoordinatesUrl = siteUrl + '/files/ftp/NDB/coordinates/xml-extatom/'
    _xmlHeaderUrl = siteUrl + '/files/ftp/NDB/coordinates/xml-noatom/'
