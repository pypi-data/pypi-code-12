import sqlite3


class SQLite:
    def __init__(self, path='markov.sqlite3'):
        self.conn = sqlite3.connect(path)
        # initialize database
        with self.conn as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS word (
                    word varchar primary key
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS next_relation (
                    w1 integer,
                    w2 integer,
                    FOREIGN KEY(w1) REFERENCES word(id),
                    FOREIGN KEY(w2) REFERENCES word(id)
                );
            ''')

    def insert(self, word, next_word):
        with self.conn as cursor:
            add_words = [w for w in (word, next_word) if not self.known(w)]
            if add_words:
                cursor.executemany('''
                    INSERT INTO word VALUES (?);
                ''', (add_words,))
            cursor.execute('''
                INSERT INTO next_relation VALUES (?, ?);
            ''', (word, next_word))

    def relation_count(self, word):
        with self.conn as cursor:
            cursor.execute('SELECT word FROM next_relation WHERE w1=?', (word,))
        print(self.conn.cursor().fetchall())

    def known(self, word):
        with self.conn as cursor:
            cursor.execute('SELECT word FROM word WHERE word=?', (word,))
        return bool(self.conn.cursor().fetchone())

    def next_words(self, word):
        with self.conn as cursor:
            cursor.execute('SELECT w2 FROM next_relation WHERE w1=?', (word,))
        print(self.conn.cursor().fetchall())
