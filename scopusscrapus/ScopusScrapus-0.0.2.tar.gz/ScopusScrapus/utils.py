__all__ = ['formatScopusEntry']
fields = [("dc:title","title"),
          ("citedby-count","citations"),
          ("dc:identifier","scopusId"),
          ("prism:coverDate","date"),
          ("prism:publicationName","pubName"),
          ("prism:isbn","pubisbn"),
          ("prism:issn","pubissn"),
          ("subtypeDescription","type"),
          ("pii","pii")]

authorFields = [("surname","surname"),
                ("given-name","givenName"),
                ("aithid","id")]

affiliationFields = [('affiliation-country','country'),
                     ('affiliation-city','city'),
                     ('afid','id')]


def _formatAuthor(author):
    res = {nF:author[oF] for oF,nF in authorFields if oF in author}
    res['affiliations'] = [af["$"] for af in author['afid']] if 'afid' in author else []
    return res

def _formatAffiliation(aff):
    res = {nF:aff[oF] for oF,nF in affiliationFields if oF in aff}
    res['names'] = [aff['affilname']] + ([nv["$"] for nv in aff['name-variant']] if 'name-variant' in aff else [])
    return res

def formatScopusEntry(entry):
    res = {nF:entry[oF] for oF,nF in fields if oF in entry}
    res['authors'] = [_formatAuthor(auth) for auth in entry["author"]] if 'author' in entry else []
    res['affiliations'] = ([_formatAffiliation(aff) for aff in entry['affiliation']] if 'affiliation' in entry else [])
    return res
