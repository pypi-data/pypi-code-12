import os
import sqlite3


def main():
    connection = sqlite3.connect(':memory:')
    init_database(connection)
    cursor = connection.cursor()
    connection.commit()
    create_user(cursor, 'testuser1', 'youtube', 'admin')
    create_user(cursor, 'testuser1', 'watchpeoplecode', 'admin')
    create_user(cursor, 'testuser1', 'twitch', 'admin')
    create_user(cursor, 'testuser1', 'livecoding', 'admin')
    create_activity(cursor, 'test_admin', 'admin')
    values = authorized_activity(cursor, 'testuser1', 'youtube', 'test_admin')
    connection.commit()
    connection.close()


def authorized_activity(cursor: sqlite3.Cursor, name, platform, activity):
    platform = 'SELECT roleid FROM {} WHERE name=?'.format(platform)
    name = (name,)
    # get the allowed user value from the table
    cursor.execute(platform, name)
    allowed_user_role = cursor.fetchone()[0]
    activity = (activity,)
    cursor.execute('SELECT roleid FROM activity WHERE name=?', activity)
    activity_role = cursor.fetchone()[0]
    if allowed_user_role >= activity_role:
        return True
    else:
        return False



def _get_roleid(cursor, role):
    role = (role,)
    cursor.execute('SELECT rowid FROM role WHERE name=?', role)
    return cursor.fetchone()[0]


def create_activity(cursor, activity, role='anonymous'):
    role_id = _get_roleid(cursor, role)
    values = (activity, role_id)
    cursor.execute('INSERT INTO activity VALUES (?, ?)',
                   values)


def create_user(cursor: sqlite3.Cursor,
                username,
                platform,
                role='anonymous'):
    """
    Creates user based on username, platform, and role.
    Returns back a rowid from user table
    """
    role_id = _get_roleid(cursor, role)
    # first: create/select a user on platform
    string_template = 'INSERT INTO {platform} VALUES (?, ?)'.format(platform=platform)

    username_and_role = (username, role_id)
    try:
        cursor.execute(string_template, username_and_role)
    except sqlite3.IntegrityError as e:
        rowid = None
    else:
        rowid = cursor.lastrowid

    if rowid is None:
        string_template = 'SELECT rowid FROM {platform} WHERE name=?'.format(platform=platform)
        cursor.execute(string_template, username)
        rowid = cursor.fetchone()[0]

    return rowid


def init_database(connection):
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    role_table = 'CREATE TABLE role (name text, id INTEGER PRIMARY KEY AUTOINCREMENT)'

    youtube_table = '''CREATE TABLE youtube (name text UNIQUE, roleid integer, FOREIGN KEY(roleid) REFERENCES role(id))'''

    wpc_table = '''CREATE TABLE watchpeoplecode (name text UNIQUE, roleid integer, FOREIGN KEY(roleid) REFERENCES role(id))'''

    livecode_table = '''CREATE TABLE livecoding (name text UNIQUE, roleid integer, FOREIGN KEY(roleid) REFERENCES role(id))'''

    twitch_table = '''CREATE TABLE twitch (name text UNIQUE, roleid integer, FOREIGN KEY(roleid) REFERENCES role(id))'''

    # Create role table first!
    cursor.execute(role_table)
    # create the user table second!

    cursor.execute(youtube_table)
    cursor.execute(wpc_table)
    cursor.execute(livecode_table)
    cursor.execute(twitch_table)

    # create activity table
    cursor.execute('CREATE TABLE activity (name text, roleid integer, FOREIGN KEY(roleid) REFERENCES role(id))')
    # create roles table
    roles = (('anonymous',), ('user',), ('trusted_user',), ('admin',))
    cursor.executemany('INSERT INTO role(name) VALUES(?)', roles)
    cursor.execute("PRAGMA user_version = 1")
    # make sure our changes are committed
    connection.commit()


if __name__ == '__main__':
    filename = 'example.db'
    if os.path.isfile(filename):
        os.remove(filename)
    main()
