
import os, traceback
from glob import glob
from bl.log import Log

from .model import Model

class Migration(Model):
    relation = 'migrations'
    pk = ['id']

    @classmethod
    def create_id(M, filename):
        return os.path.basename(os.path.splitext(filename)[0])

    @classmethod
    def migrate(M, db, path=None, log=Log()):
        """update the database with unapplied migrations"""
        path = path or db.migrations
        try:
            # will throw an error if this is the first migration -- migrations table doesn't yet exist.
            # (and this approach is a bit easier than querying for the existence of the table...)
            migrations_ids = [r.id for r in M(db).select()]
        except:
            migrations_ids = []
        fns = [fn for fn 
                in glob(os.path.join(path, "*.*")) 
                if M.create_id(fn) not in migrations_ids]
        fns.sort()
        log("[%s]" % log.timestamp(), "Migrate Database: %d migrations" % len(fns))
        for fn in fns:
            id = M.create_id(fn)
            ext = os.path.splitext(fn)[1]
            if id in migrations_ids: 
                continue
            else:
                f = open(fn, 'r'); script = f.read(); f.close()
                description = script.split("\n")[0].strip('-#/*; ') # first line is the description
                log('', id+ext, ':', description)
                cursor = db.cursor()
                try:
                    if ext=='.sql':                                     # script is a SQL script, db.execute it
                        db.execute(script, cursor=cursor)
                    else:                                               # script is system script, subprocess it
                        subprocess.check_output(script, {'db': db})
                    migration = M(db, id=id, description=description)
                    migration.insert(cursor=cursor)
                    cursor.connection.commit()
                except:
                    cursor.connection.rollback()
                    raise
                cursor.close()
