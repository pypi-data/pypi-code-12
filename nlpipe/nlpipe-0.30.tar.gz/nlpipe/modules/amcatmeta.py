from io import BytesIO

from KafNafParserPy.KafNafParserMod import KafNafParser
from KafNafParserPy.header_data import Cpublic, CHeader, CfileDesc

from ..backend import get_input, get_input_fields, esconfig

def _add_meta(naf, raw, uri, publicid, author, title, date, filename):
    if naf.header is None:
        naf.header = CHeader(type=naf.type)
        naf.root.insert(0, naf.header.get_node())

    fd = CfileDesc()
    fd.set_author(author)
    fd.set_title(title)
    fd.set_filename(filename)
    fd.set_creationtime(date)
    naf.header.set_fileDesc(fd)

    pub = Cpublic()
    pub.set_uri(uri)
    pub.set_publicid(publicid)
    naf.header.set_publicId(pub)

    naf.set_raw(raw)

def set_amcatmeta(naf, id):
    doc = get_input(id)
    f = get_input_fields(id, ['medium', 'url', 'uuid', 'medium', 'headline', 'date'])
    url = "/".join(["http:/", esconfig.ES_HOST, esconfig.ES_INPUT_INDEX, esconfig.ES_INPUT_DOCTYPE, str(id)])
    _add_meta(naf, doc.text, f['url'][0], f['uuid'][0], f['medium'][0], f['headline'][0], f['date'][0]+'.000Z', url)

def add_amcatmeta(naf_bytes, id):
    f = BytesIO(naf_bytes.encode("utf-8"))
    naf = KafNafParser(filename=f, type="NAF")
    set_amcatmeta(naf, id)
    s = BytesIO()
    naf.dump(s)
    return s.getvalue()
