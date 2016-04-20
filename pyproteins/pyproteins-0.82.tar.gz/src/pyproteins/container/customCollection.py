import os

'''
GL 2015-07-08 Givin up trying to adpat this module to Peptides
 May come back to it later,if Peptide usage is needed on a long term
indexer arguments supply a indexing function to be called for each objects
    -->(typically setting object accessors key based on their fileName)
cIndexer arguments supply a common indexing function to be called once for the entiere collection
    --> eg: Read from a single catalogue file the mapping between object accessors and their fileName
'''
class EntrySet():
    def __init__(self, collectionPath=None, constructor=None, typeCheck=None, indexer=None, cIndexer=None):

        if not collectionPath:
            raise ValueError("You must specify a filesystem path to local cache")
        if not constructor:
            raise ValueError("You must bind an object constructor at cache invocation")
        if not indexer and not cIndexer:
            raise ValueError("You must specify an indexer function to map filename <-> collection key")

        self.typeCheck = typeCheck
        self.constructor = constructor
        self.indexer = indexer

        self.root = collectionPath
        self.data = {}
        for fileName in os.listdir(self.root): # lazy initialization of objects
            id = self.indexer(fileName)
            self.data[id] = { 'updated' : False, 'location' : self.root + '/' + fileName, 'e' : None }  #Entry(id,fileName = self.root + '/' + fileName
        print "Acknowledged " + str(len(self.data)) + " entries (" +  self.root + ")"

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for k,d in self.data.iteritems():
            yield d

    def __repr__(self):
        string = "Cache pool size " + str(len(self)) + '\n'
        for k,d in self.data.iteritems():
            status = "LOADED" if d['e'] else "LAZY"
            string += k + '\t' + status + "\n"
        return string

    def add(self, id):
        self.data[id] = { 'updated' : True, 'location' : None, 'e' : self.constructor(id) } # Newly added object dont have location

    def clear(self):
        n=len(self.data)
        id=[ k for k in self.data ]
        for k in id:
            self.delete(k)
        print "All " + str(n) + " entries deleted!"

    def delete(self, id):
        if os.path.isfile(self.data[id]['location']):
            os.remove(self.data[id]['location'])
        self.data.pop(id, None)

    def get(self, id, reload=False):
        if self.typeCheck:
            if not self.typeCheck(id):
                raise TypeError("invalid supplied identifier \"" + id + "\"")

        if id in self.data and reload:
            self.delete(id)
        # Present but lazy initialized
        if id in self.data and not self.data[id]['e'] and self.data[id]['location']:
            self.data[id]['e'] = self.constructor(id, fileName = self.data[id]['location'])
            self.data[id]['updated'] = True
        # Not present
        if not id in self.data:
            self.add(id)


        return self.data[id]['e']

    def serialize(self, force=False):
        c = 0
        t = 0
        for d in self:
            t += 1
            if d['updated'] or force:
                if d['e']:
                    d['location'] = self.root + '/' + d['e'].id + '.xml' if not d['location'] else d['location']
                with open(d['location'], "w") as textFile:
                    textFile.write(d['e'].serialize())
                c +=1
                d['updated'] = False
        print str(c) + " entries updated, total pool is " + str(t)
