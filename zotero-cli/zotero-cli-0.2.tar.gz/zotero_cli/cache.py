try:
    import apsw
    HAS_APSW = True
except ImportError:
    HAS_APSW = False


def is_json_supported():
    if not HAS_APSW:
        return False
    conn = apsw.Connection(":memory:")
    cursor = conn.cursor()
    try:
        return cursor.execute("SELECT json(?)", (1,)).fetchone() == ('1',)
    except apsw.SQLError:
        return False


def is_fts5_supported():
    if not HAS_APSW:
        return False
    conn = apsw.Connection(":memory:")
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE VIRTUAL TABLE testing USING fts5(data);")
        return True
    except apsw.SQLError:
        return False
