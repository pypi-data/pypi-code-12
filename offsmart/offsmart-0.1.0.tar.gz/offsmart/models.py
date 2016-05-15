import storm.locals as storm

class Data(object):
    __storm_table__ = 'data'
    id = storm.Int(primary=True)
    payload = storm.RawStr()
    sent = storm.Bool()

    @staticmethod
    def create_table(store):
        store.execute('CREATE TABLE data'
                    '(id INTEGER PRIMARY KEY AUTOINCREMENT, payload VARCHAR, sent INT)')
