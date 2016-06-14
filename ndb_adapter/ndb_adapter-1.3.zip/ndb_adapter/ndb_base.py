

class NDBBase(object):
    """Base class for NDB

    :cvar siteUrl: ndb site url
    :cvar _advancedUrl: private advanced search url
    :cvar _summaryUrl: private summary url
    :cvar _dnaUrl: private dna search url
    :cvar _rnaUrl: private rna search url
    :cvar _chiralCorrectUrl: private chiral correct coordinates download url
    :cvar _nmrUrl: private nmr pdb coordinates download url
    :cvar _nmrMmCifUrl: private nmr mmcif coordinates download url
    :cvar _bioAssemblyCoordinateUrl: private bio assembly coordinates download url
    :cvar _mmCifUrl: private mmCIF coordinates download url
    :cvar _structureFactorsUrl: private structure factors download url
    :cvar _nmrRestraintsUrl: private nmr restraints download url
    :cvar _xmlCompleteUrl: private complete xml download url
    :cvar _xmlCoordinatesUrl: private coordinates only xml download url
    :cvar _xmlHeaderUrl: private header only xml download url
    """
    siteUrl = 'http://ndbserver.rutgers.edu'
    _advancedUrl = siteUrl + '/service/ndb/report/advSearchReport'
    _summaryUrl = siteUrl + '/service/ndb/atlas/summary'
    _dnaUrl = siteUrl + '/service/ndb/atlas/gallery/dna'
    _rnaUrl = siteUrl + '/service/ndb/atlas/gallery/rna'
    _chiralCorrectUrl = siteUrl + '/files/ftp/NDB/coordinates/na-chiral-correct/'
    _nmrUrl = siteUrl + '/files/ftp/NDB/coordinates/na-nmr/'
    _nmrMmCifUrl = siteUrl + '/files/ftp/NDB/coordinates/na-nmr-mmcif/'
    _bioAssemblyCoordinateUrl = siteUrl + '/files/ftp/NDB/coordinates/na-biol/'
    _mmCifUrl = siteUrl + '/files/ftp/NDB/coordinates/na-mmcif/'
    _structureFactorsUrl = siteUrl + '/files/ftp/NDB/structure-factors/'
    _nmrRestraintsUrl = siteUrl + '/files/ftp/NDB/nmr-restraints/'
    _xmlCompleteUrl = siteUrl + '/files/ftp/NDB/coordinates/xml/'
    _xmlCoordinatesUrl = siteUrl + '/files/ftp/NDB/coordinates/xml-extatom/'
    _xmlHeaderUrl = siteUrl + '/files/ftp/NDB/coordinates/xml-noatom/'
