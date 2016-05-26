"""cubicweb-dataprocessing tests"""

from cubicweb import Binary


def create_file(cnx, data, data_name=None, **kwargs):
    """Create a File entity"""
    data_name = data_name or data.decode('utf-8')
    kwargs.setdefault('data_format', u'text/plain')
    return cnx.create_entity('File', data=Binary(data),
                             data_name=data_name,
                             **kwargs)


def script_from_code(cnx, kind, code, name, **kwargs):
    """Build a Script entity from `code` string and `name`."""
    etype = {
        'transformation': 'TransformationScript',
        'validation': 'ValidationScript',
    }[kind]
    fscript = create_file(cnx, code, data_name=name)
    return cnx.create_entity(etype, name=name, implemented_by=fscript,
                             **kwargs)


def script_from_file(cnx, kind, fpath, **kwargs):
    """Build a Script entity from the content of file at `fpath`."""
    name = unicode(fpath)
    with open(fpath) as f:
        return script_from_code(cnx, kind, f.read(), name)


def create_process(cnx, etype, script, **kwargs):
    """Create a "simple" data process with a single script."""
    if etype == 'DataTransformationProcess':
        seq = cnx.create_entity('TransformationSequence')
        cnx.create_entity('TransformationStep', index=0, in_sequence=seq,
                          step_script=script, **kwargs)
        relation = {'transformation_sequence': seq}
    elif etype == 'DataValidationProcess':
        relation = {'validation_script': script}
    return cnx.create_entity(etype, **relation)
