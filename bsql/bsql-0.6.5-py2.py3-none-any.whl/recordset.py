
import sys
from bl.dict import Dict

class RecordSet(list):
    """A set of database records"""

    def select(self, **args):
        """return all records in the set that have the attributes specified in args, or empty RecordSet"""
        result = RecordSet()
        for record in self:
            match = True
            for k in args:
                if record[k] != args[k]:
                    match = False
                    break
            if match == True:
                result.append(record)
        return result
        
    def select_one(self, **args):
        """return the first record in the set that has the attributes specified in args, or None."""
        for record in self:
            match = True
            for k in args:
                if record[k] != args[k]:
                    match = False
                    break
            if match == True:
                return record

    def dict(self, key):
        """returns the RecordSet as a dict of records, keyed to strings or tuples. 
            keys must be unique, or later duplicates will overwrite earlier ones."""
        d = Dict()
        for record in self:
            if type(key) == str:            # string key
                d[record[key]] = record
            else:                           # tuple key
                d[record.key_tuple(key)] = record
        return d
        
    def json(self, fields=[]):
        """Return the contents of this record set as json"""
        l = [record.json(fields=fields) for record in self]
        return '[' + ', '.join(l) + ']'

        
