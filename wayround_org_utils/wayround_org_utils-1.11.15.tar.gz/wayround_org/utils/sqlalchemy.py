

def get_column_names(metadata, tablename):

    length = len(tablename) + 1

    ret = []

    for i in metadata.tables[tablename].columns:
        # FIXME: need to find more correct way than str()
        #        ret.append(str(i)[length:])
        ret.append(i.name)

    return ret
