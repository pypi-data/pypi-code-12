## DTModel
#
# Copyright (c) 2016, Expressive Analytics, LLC <info@expressiveanalytics.com>.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# @package Deep Thought
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

from deepthought.store.DTQueryBuilder import DTQueryBuilder
from deepthought.utils.DTLog import DTLog
from deepthought.core.DTParams import DTParams
from deepthought.core.DTResponse import DTResponse
from deepthought.store.DTStore import DTStore
import json
import re

from importlib import import_module

class DTModelNotFoundException(Exception):
    pass

class DTModel(object):
    ## require properties to be defined in the class, defaults to False
    strict_properties = False
    storage_table = None
    primary_key_column = "id"

    has_a_manifest = {}
    has_many_manifest = {}
    is_a_manifest = {}

    #db = None
    #input = {}
    #id = 0

    #_properties = {} ## @internal
    #_bypass_accessors = False ## @internal a flag used to bypass accessors during construction

    #_unsanitary = True

    @staticmethod
    def _classFromString(str):
        p = str.rsplit('.', 1)
        mod = import_module(p[0])
        if len(p) > 1:
            return getattr(mod, p[1])
        else:
            return getattr(mod, p[0])

    @staticmethod
    def _tableAlias(modelName):
        p = modelName.split(".") # get the table alias
        return p[-1]

    def __init__(self,paramsOrQuery=None):
        self.db = None
        self.input = {}
        self.id = 0
        self._properties = {}
        self._bypass_accessors = False
        self._unsanitary = True

        properties = None
        if paramsOrQuery is None:
            return # just create an empty object
        self._bypass_accessors = True # we want direct access to properties by default
        if isinstance(paramsOrQuery,dict):
            properties = paramsOrQuery
        elif isinstance(paramsOrQuery, DTQueryBuilder): # grab the parameters from storage
            self.db = paramsOrQuery.db #save where we came from
            if self.storage_table is not None:
                paramsOrQuery = self.selectQB(paramsOrQuery)
                properties = paramsOrQuery.select1("*, "+self.__class__.__name__+".*")
            if properties is None:
                raise DTModelNotFoundException("Failed to find "+self.__class__.__name__+" in storage.\n"+str(paramsOrQuery))
        if properties is None:
            DTLog.error("Invalid parameters used to construct DTModel"+json.loads(paramsOrQuery)+")")
            raise Exception("Invalid parameters for DTModel constructor.")
        if isinstance(properties,dict): # must be an associative array
            for k,v in properties.iteritems():
                self[k] = v #make sure we go through the set method
        else:
            DTLog.warn("Attempt to instantiate "+self.__class__.__name__+" from invalid type ("+json.loads(properties)+")")
        self._bypass_accessors = False # make sure we use the accessors now

    def __setitem__(self,offset,value):
        if offset is None:
            self._properties.append(value)
            return value
        else:
            accessor = "set"+re.sub(r"[^A-Z^a-z^0-9]+","",offset)
            if not self._bypass_accessors:
                try:
                    attr = getattr(self,accessor)
                    if offset != "many" and offset != "a" and callable(attr): # try to use the accessor method
                        return attr(value)
                except:
                    pass
                # note: setMany causes immediate database insertion
                # this is necessary, because we need these objects hooked up
                manifest = self.__class__.hasManyManifest()
                if offset in manifest: # this is a set-many relationship
                    value = self.setMany(manifest[offset],value)
                manifest = self.__class__.hasAManifest()
                if offset in manifest: # this is a has-a relationship
                    value = self.setA(offset)
            if hasattr(self,offset): #use the property
                setattr(self,offset,value)
                return getattr(self,offset)
            if not self.strict_properties: # set object property
                self._properties[offset] = value
                return value

    def __contains__(self,offset):
        return offset in self._properties

    def __delitem__(self,offset):
        del self._properties[offset]

    def __getitem__(self,offset):
        accessor = re.sub(r"[^A-Z^a-z^0-9]+","",offset)
        try:
            return getattr(self,accessor)() # use the accessor method
        except:
            pass
        if hasattr(self,offset): # use the property, if set
            val = getattr(self,offset)
            if val is not None:
                return val
        if self.strict_properties == False: # get object property if set
            if offset in self._properties:
                return self._properties[offset]
        manifest = self.__class__.hasManyManifest()
        if offset in manifest:
            val = self.getMany(manifest[offset])
            if hasattr(self,offset):
                setattr(self,offset,val)
            else:
                self._properties[offset] = val
            return val
        manifest = self.__class__.hasAManifest()
        if offset in manifest:
            val = self.getA(manifest[offset][0],manifest[offset][1])
            self.__tooComplex(offset,val)
            return val
        return None

    # python thinks __getitem__ is too complex?? so we moved this bit out
    def __tooComplex(self,offset,val):
        if hasattr(self,offset):
            setattr(self,offset,val)
        else:
            self._properties[offset] = val

    def isDirty(self,offset):
        if hasattr(self,offset) or offset in self._properties:
            return True
        return False

    def getMany(self,chainOrName,qb=None):
        chain,qb = self.__tooComplexII(chainOrName,qb)
        qb,target_cls = self.getManyQB(chain,qb)
        return target_cls.select(qb,target_cls.__name__+".*")

    def __tooComplexII(self,chainOrName,qb):
        chain = chainOrName[:]
        if isinstance(chainOrName, basestring):
            manifest = self.__class__.hasManyManifest()
            chain = manifest[chainOrName]
        if qb is None:
            qb = self.db.qb()
        return chain, qb

    def getManyQB(self,chainOrName,qb=None,target_class=None):
        chain,qb = self.__tooComplexII(chainOrName,qb)

        if isinstance(chain[0],tuple):
            mdl,key_col = chain[0]
        else:
            mdl = self._classFromString(chain[0]) if isinstance(chain[0],basestring) else chain[0]
            key_col = mdl.columnForModel(self.__class__)

        key_val = self[self.primary_key_column]
        link = chain.pop()
        if isinstance(link,tuple):
            target_class = link[0]
        else:
            target_class = link
        target_cls = self._classFromString(target_class)

        last_col = None
        if isinstance(link,tuple):
            last_col = link[1]
        elif len(chain) > 0:
            last_col = self._classFromString(target_class).columnForModel(self._classFromString(chain[len(chain)-1]))

        last_alias = target_cls.__name__
        last_model = target_class
        if len(chain)>0: # if we are joining anything, we need to use group-by
            qb.groupBy(self._tableAlias(target_class)+"."+self._classFromString(target_class).primary_key_column)
        while len(chain) > 0:
            link = chain.pop()
            model = link[0] if isinstance(link,tuple) else link
            col = self._classFromString(model).columnForModel(self._classFromString(last_model))
            if isinstance(link,tuple):
                col = link[1]

            model_alias = self._tableAlias(model)+"_"+str(len(chain))
            #owner_alias = self._classFromString(model).aliasForOwner(col)
            owner_alias = None
            if owner_alias is None:
                owner_alias = model_alias
            qb.join("{} {}".format(self._classFromString(model).storage_table,self._tableAlias(model_alias)),"{}.{}={}.{}".format(last_alias,last_col,self._tableAlias(owner_alias),col))
            self._classFromString(model).isAQB(qb,model_alias)

            last_alias = model_alias
            last_model = model
            last_col = col

        manifest = self.__class__.isAManifest()
        if len(manifest) > 0: # we need to use the parent class id
            qb.join(self.storage_table+" "+self.__class__.__name__,self.__class__.__name__+"."+str(self.primary_key_column)+"="+str(self[self.primary_key_column]))
            qb.addColumns([self.__class__.__name__+".*"]) #make sure we pull into the new attributes
        else: # use our own ID
            if not isinstance(last_alias,basestring): #we're on the original chain
                a = last_alias.__name__
                target_cls = self
            else:
                a = self._tableAlias(last_alias)
                target_cls = self._classFromString(target_class)
            qb.filter({a+"."+key_col:key_val})
        return qb, target_cls

    def closure(self,chain,defaults={}):
        closure = {}
        last_model_cls = self.__class__
        val = str(self[self.primary_key_column])
        last_ids = {val:val}
        closure[self.__class__.__name__] = last_ids
        for c in chain:
            # get the column to back-link
            #link = c.split(":")
            if isinstance(c,tuple):
                model = c[0]
                col = c[1]
            else:
                model = c
                col = self._classFromString(model).columnForModel(last_model_cls)
            model_cls = self._classFromString(model)
            # get the current primary key
            key = model_cls.primary_key_column #id
            arr = {}
            for id,v in last_ids.iteritems():
                defaults[self._tableAlias(model)] = id
                filter = {col: id}
                matches = model_cls.select(self.db.filter(filter))
                out = {}
                for i in matches:
                    out[str(i[key])] = str(id)
                out.update(arr)
                arr = out
            last_ids = arr
            closure[self._tableAlias(model)] = last_ids
            last_model_cls = model_cls
        return closure, defaults

    def setMany(self,chainOrName,vals,builder_f=None):
        chain = chainOrName[:] # MUST be copied... ?
        if isinstance(chainOrName,basestring):
            manifest = self.__class__.hasManyManifest()
            chain = manifest[chainOrName]

        #prepare the parameters for filter/upsert in the target table (builder_f)
        #link = chain[-1].split(":")
        target_class = chain[-1][0] if isinstance(chain[-1],tuple) else chain[-1]
        key = self._classFromString(target_class).primary_key_column
        if builder_f is None:
            builder_f = self.defaultBuilder
        params = builder_f(key,vals)

        defaults = {}
        stale_sets,defaults = self.closure(chain,defaults)

        # do the chain of upserts
        delete_stale = len(chain)==1 # don't delete from the destination table, unless it's the only stop
        inserted = []
        first_link = True
        chain = [self.__class__] + chain
        #chain.insert(0,self.__class__) # this is a horrible bit of code that injects garbage in the manifest, despite every every to make copies--don't use it

        while len(chain) > 1:
            c = chain.pop()
            #link1 = c.split(":")
            model = c[0] if isinstance(c,tuple) else c
            model_cls = self._classFromString(model)
            if isinstance(chain[-1],(tuple,basestring)):
                #link2 = chain[-1].split(":")
                next_model = chain[-1][0] if isinstance(chain[-1],tuple) else chain[-1]
                next_model_cls = self._classFromString(next_model)
                next_col = chain[-1][1] if isinstance(chain[-1],tuple) else next_model_cls.columnForModel(model_cls)
            else: # for the first chain item, we only have the self.__class__ instance...
                next_model_cls = chain[-1]
                next_col = next_model_cls.columnForModel(model_cls)
            col = c[1] if isinstance(c,tuple) else model_cls.columnForModel(next_model_cls)

            stale = stale_sets[self._tableAlias(model)]
            if self._tableAlias(model) in defaults:
                default_v = defaults[self._tableAlias(model)]
            else:
                default_v = "0"
            last_params = []
            i = 0
            for p in params:
                vs = p.values()
                v = str(vs[0]) if len(vs) > 0 else None
                # if nextmodel hasMany model, hook up col=>nextmodel.key
                if col != model_cls.primary_key_column:
                    p[col] = stale[v] if v in stale else default_v # default (for now entries) is to link to the first entry from the previous table
                if first_link: # don't try to set all the values unless we're at the target table
                    vs = vals
                    up = vals[i] if isinstance(vs[0],dict) else p
                    up[col] = p[col]
                else:
                    up = p
                obj = model_cls.upsert(self.db.filter(p),up)
                if first_link: #we're doing the last table
                    inserted.append(obj)
                if str(obj[model_cls.primary_key_column]) in stale:
                    del stale[obj[model_cls.primary_key_column]]
                last_params.append({next_col:p[col]} if next_col == next_model_cls.primary_key_column else {next_col:obj[col]} )
                i += 1
            if len(stale) > 0:
                if delete_stale:
                    model_cls.deleteRows(self.db.filter({model_cls.primary_key_column:["IN",stale.keys()]}))
                elif first_link: # we can't delete from the destination table, but we should unset the association
                    if col != model_cls.primary_key_column: # need to clear our back-link
                        model_cls.updateRows(self.db.filter({model_cls.primary_key_column:["IN",stale.keys()]}),{col:None})
            delete_stale = True
            first_link = False
            params = last_params
        return inserted

    def defaultBuilder(self,key,vals):
        out = []
        for i in vals:
            if isinstance(i,dict):
                out.append(i)
            else:
                out.append({key:i})
        return out

    def isEqual(self,obj):
        return self == obj

    ## attempts to access +property+ directly (does not work with accessors), assigning value of +f+ if not found
    def selfOr(self,property,f):
        if property is None:
            property = f()
        return property

    def publicProperties(self,defaults={},purpose=None):
        public_params = {}
        names = dir(self)
        mdl_names = dir(DTModel)
        for n in names:
            attr = getattr(self,n)
            if n == "id" or n not in mdl_names: #don't worry about DTModel stuff (except ID)
                if not re.match(r"_",n) and not callable(attr): #hide methods and _* (python's ridiculous concept of private)
                    public_params[n] = DTResponse.objectAsRenderable(self[n])
        public_params.update(defaults)
        return public_params

    def storageProperties(self,db,defaults={},purpose=None):
        storage_params = {}
        cols = db.columnsForTable(self.storage_table)
        if len(cols)==0:
            DTLog.error("Found 0 columns for table ({})".format(self.storage_table))
        for k in cols:
            if purpose != "insert" or k != self.primary_key_column: # don't try to insert the id, assume it's autoincrementing
                if self.isDirty(k): # we don't want to unset columns we don't control (subsetted models)
                    storage_params[k] = self[k]
        defaults.update(storage_params)
        return defaults

    def clean(self,db=None):
        db = db if db is not None else self.db
        p = DTParams(self.storageProperties(db,{},"reinsertion"))
        clean = p.allParams()
        for k,v in clean.iteritems():
            self[k] = v
        self._unsanitary = False

    def merge(self,params,changes=None):
        self.input = params
        if changes is None:
            changes = {"old":{},"new":{}}
        cols = self.db.columnsForTable(self.storage_table)
        updated = 0
        for k,v in params.iteritems():
            old_val = self[k]
            # don't set the primary key, no matter what anyone says
            if k != self.primary_key_column:
                #don't record changes that don't affect storage
                if k in cols and old_val != v:
                    changes["old"][k] = old_val
                    changes["new"][k] = v
                self[k] = v
                updated += 1
        return updated, changes

    def insert(self,db=None,qb=None):
        db = self.db if db is None else db
        self.setStore(db)
        qb = DTQueryBuilder(db) if qb is None else qb # allow the query builder to be passed, in case it's a subclass
        properties = self.storageProperties(db,{},"insert")
        new_id = qb.fromT(self.storage_table).insert(properties)
        self[self.primary_key_column] = new_id
        return new_id

    def update(self,db=None,qb=None):
        if self._unsanitary:
            DTLog.warn(DTLog.colorize(self.__class__.__name__+" updated without calling clean()"),"warn")
            DTLog.debug(self)
            DTLog.debug(DTLog.lastBacktrace())
        db = self.db if db is None else db
        qb = db.filter({self.primary_key_column:self[self.primary_key_column]}) if qb is None else qb
        properties = self.storageProperties(db,{},"update")
        return qb.fromT(self.storage_table).update(properties)

    #...

    @classmethod
    def upsert(cls,qb,params,defaults={},changes={}):
        try:
            obj = cls(qb) # if we fail out here, it's probably because the record needs to be inserted
            if len(params)==0:
                return obj # there are no changes, let's get outta here
            obj.clean(qb.db) #replace storage with clean varieties
            ct, changes = obj.merge(params) # now we're ready to merge in the new stuff
            obj.upsertAncestors(params)
            obj.update(qb.db) #it's essential that this use *only* the +primary_key_column+
        except DTModelNotFoundException: # the record doesn't exist, insert it instead
            obj = cls({"db":qb.db}) # the store needs to be available in the constructor
            obj.clean()
            obj.merge(defaults) # use the accessor for defaults
            obj.insert(qb.db)
            ct, changes = obj.merge(params) # this has to happen after insertion to have the id available for setMany
            obj.upsertAncestors(params) #must be after merge
            obj.update(qb.db)
        #return obj,changes
        return obj

    def upsertAncestors(self,params):
        manifest = self.__class__.isAManifest()#[::-1]
        for col,m in manifest.iteritems():
            #link = m.split(":")
            if isinstance(m,tuple):
                dst_model = m[0]
                dst_col = m[1]
            else:
                dst_model = m
                dst_col = self._classFromString(dst_model).primary_key_column
            #old_id = params[col] if col in params else 0
            parent = dst_model.upsert(self.db.filter({"{}.{}".format(dst_model,dst_col):self[col]}),params)
            self[col] = parent[dst_col]

    ## called during instantiation from storage--override to modify QB
    @classmethod
    def selectQB(cls,qb):
        qb.fromT(cls.storage_table+" "+cls.__name__)
        manifest = cls.isAManifest()
        if len(manifest) > 0:
            qb.addColumns([cls.__name__+".*"]) #make sure we get our own ID, not a subclass
        return qb

    @classmethod
    def isAQB(cls,qb,alias=None):
        if alias is None:
            alias = cls.__name__
        manifest = cls.isAManifest()
        i = 0
        for col,m in manifest.iteritems():
            #link = m.split(":")
            if isinstance(m,tuple):
                dst_model = m[0]
                dst_col = m[1]
            else:
                dst_model = m
                dst_col = cls._classFromString(dst_model).primary_key_column
            dst_model_cls = cls._classFromString(dst_model)
            dst_alias = cls._tableAlias(dst_model)+"_"+str(i)
            dst = dst_model_cls.storage_table+" "+dst_alias
            qb.join(dst,"{}.{}={}.{}".format(alias,col,dst_alias,dst_col))
            qb = dst_model_cls.isAQB(qb,dst_alias) # also join in the parent's selectQB()
            qb.addColumns([dst_alias+".*"]) # makes parent attributes available
            i += 1
        return qb

    ## traverses the is_a hierarchy for the attribute owner
    @classmethod
    def aliasForOwner(cls,col):
        names = dir(cls)
        if col in names:
            return cls.aliasForParent(cls.__name__)
        return None

    @classmethod
    def select(cls,qb,cols=None):
        cls.selectQB(qb)
        if cols is None:
            cols = cls.__name__+".*"
        return qb.selectAs(cls,cols)

    @classmethod
    def selectKV(cls,qb,cols):
        cls.selectQB(qb)
        return qb.selectKV(cols)

    @classmethod
    def count(cls,qb):
        return qb.fromT(cls.storage_table+" "+cls.__name__).count(cls.__name__+".*")

    @classmethod
    def sum(cls,qb,col):
        return qb.fromT(cls.storage_table+" "+cls.__name__).sum(col)

    @classmethod
    def updateRows(cls,qb,params):
        return qb.fromT(cls.storage_table).update(params)

    @classmethod
    def deleteRows(cls,qb):
        return qb.fromT(cls.storage_table).delete()

    @classmethod
    def byID(cls,db,id,cols="*"):
        if not isinstance(db,DTStore):
            raise Exception("invalid storage for id('{}')".format(id))
        rows = cls.select(db.where(cls.__name__+"."+cls.primary_key_column+"='{}'".format(id)),cols)
        if len(rows) > 0:
            return rows[0]
        else:
            return None

    def setStore(self,db):
        self.db = db

    #...

    def __str__(self):
        return json.dumps(self.publicProperties())

    def getA(self,class_name,column):
        cls = self._classFromString(class_name)
        try:
            return cls(self.db.filter({cls.primary_key_column:self[column]}))
        except:
            pass
        return None

    def setA(self,name,params=None):
        manifest = self.__class__.hasAManifest()
        cls = self._classFromString(manifest[name][0])
        col = manifest[name][1]
        if params is None: # default to exact match on preprocessed params
            params = cls.processForStorage(self.input,self.db)
        obj = cls.upsert(self.db.filter(params),params)
        self[col] = obj[self.primary_key_column]
        original_ba = self._bypass_accessors
        self._bypass_accessors = True # don't end up back here, just store the obj appropriately
        self[name] = obj
        self._bypass_accessors = original_ba
        return obj

    @classmethod
    def processForStorage(cls,params,db):
        obj = cls({"db":db})
        obj.merge(params)
        properties = obj.storageProperties(db)
        del properties[cls.primary_key_column]
        return properties

    __has_many_manifests = {}
    @classmethod
    def hasManyManifest(cls):
        if cls is DTModel:
            raise Exception("invalid access to DTModel manifests")
        try:
            return cls.__has_many_manifests[cls.__name__]
        except:
            if cls.__bases__[0] is not DTModel:
                cls.__has_many_manifests[cls.__name__] = cls.__bases__[0].hasManyManifest()
            else:
                cls.__has_many_manifests[cls.__name__] = {}
            cls.__has_many_manifests[cls.__name__].update(cls.has_many_manifest)
        return cls.__has_many_manifests[cls.__name__]

    @classmethod
    def modelFor(cls,name):
        manifest = cls.hasManyManifest()
        return manifest[name][-1]

    __has_a_manifests = {}
    @classmethod
    def hasAManifest(cls):
        try:
            return cls.__has_a_manifests[cls.__name__]
        except:
            if hasattr(cls.__bases__[0],"hasAManifest"):
                cls.__has_a_manifests[cls.__name__] = cls.__bases__[0].hasAManifest()
            else:
                cls.__has_a_manifests[cls.__name__] = {}
            cls.__has_a_manifests[cls.__name__].update(cls.has_a_manifest)
        return cls.__has_a_manifests[cls.__name__]

    __is_a_manifests = {}
    @classmethod
    def isAManifest(cls):
        try:
            return cls.__is_a_manifests[cls.__name__]
        except:
            cls.__is_a_manifests[cls.__name__] = cls.is_a_manifest
        return cls.__is_a_manifests[cls.__name__]

    @classmethod
    def aliasForParent(cls,model):
        manifest = cls.isAManifest()
        i = 0
        for k,class_name in manifest:
            if class_name == model.__name__:
                return model+"_"+str(i)
            i += 1
        parent = cls.__bases__[0]
        if parent is not DTModel:
            return parent.aliasForParent(model)
        return None

    @classmethod
    def columnForModel(cls,model):
        manifest = cls.hasAManifest()
        while True: #crawl up the ancestors
            for k,m in manifest.iteritems():
                if cls._tableAlias(m[0]) == model.__name__:
                    return m[1]
            model = model.__bases__[0]
            if model is DTModel:
                break
        return cls.primary_key_column # we've got the relationship backward

    def primaryKey(self):
        return self[self.primary_key_column]

    @classmethod
    def primaryKeyColumn(cls):
        return cls.primary_key_column
