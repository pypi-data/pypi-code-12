from .core import DbgCode


def clean(inputstring):
    dbgcode = DbgCode(inputstring)
    cleaned = dbgcode.clean()
    return cleaned


def clean_file(filepath):
    with open(filepath, "r+") as f:
        inputstring = f.read()
        dbgcode = DbgCode(inputstring)
        cleaned = dbgcode.clean()
        f.seek(0)
        f.write(cleaned)
        f.truncate()
    return cleaned
