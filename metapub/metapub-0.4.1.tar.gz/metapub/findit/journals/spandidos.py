from __future__ import absolute_import, unicode_literals

# Spandidos: volume/issue/firstpage AND a journal abbreviation. Fancy.
spandidos_format = 'http://www.spandidos-publications.com/{ja}/{a.volume}/{a.issue}/{a.first_page}/download'
spandidos_journals = {
    'Int J Oncol': {'ja': 'ijo'},
    'Int J Mol Med': {'ja': 'ijmm'},
    'Oncol Lett': {'ja': 'ol'},
    'Oncol Rep': {'ja': 'or'},
}
