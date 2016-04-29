from copy import deepcopy
from file import read_JSON
import os

class drugListProcessing():
    typesOfID = ["CAS","chembl_id","chebi_id","DrugBank","PubChem","MeSH_ID","KEGG_drug","name","Rname","stitch_id"]
    namePrettifier = {'name':'Name'}#,
#                       'target_entrez':'Target Entrez IDs',
#                       'union_target':'Union Targets',
#                       'level2_description': 'Level 2 Description',
#                       'level1_description': 'Level 1 Description',
#                       'chembl_id':'Chembl ID',
#                       'SEAtarget_entrez': 'SEA Target Entrez IDs',
#                       'chebi_id': 'Chebi ID',
#                       'level4_description': 'Level 4 Description',
#                       'moa':'Method of Action',
#                       'union_entrez': 'Union Entrez IDs',
#                       'target': 'Targets',
#                       'KEGG_drug': 'KEGG Drug ID',
#                       'atc_code':'ATC Code',
#                       'indication':'Indication',
#                       'level3_description': 'Level 3 Description',
#                       'side_effects': "Side Effects",
#                       'SEAtarget': "SEA Target"}
    bannedCols = ['Rname']
    def __init__(self, cmap):
        if isinstance(cmap, basestring) and os.path.isfile(cmap):
            cmap = read_JSON(cmap)
        self.cmap = cmap
        allDrugIDsByType = dict(map(lambda x: (x,
                                         set(map(lambda y: y[x].lower(),
                                                 filter(lambda y: x in y,
                                                        cmap)
                                                 ))
                                         ),
                              self.typesOfID)
                          )
        entryLookupByID = {}
        for entry in cmap:
            for type in self.typesOfID:
                if type in entry and entry[type] not in ['NA', '']:
                    if not entry[type].lower() in entryLookupByID:
                        entryLookupByID[entry[type].lower()] = entry
                    elif entryLookupByID[entry[type].lower()] == entry:
                        pass #normal
                    else:
                        countNA_1 = entry.values().count('NA')
                        countNA_2 = entryLookupByID[entry[type].lower()].values().count('NA')
                        if countNA_1 < countNA_2:
                            entryLookupByID[entry[type].lower()] = entry
                        elif countNA_1 == countNA_2:
                            #print entry[type] + ' was duplicated in cmap for a different entry and no entry was determined to be better.'
                            pass
            for key, value in entry.items():
                if key in self.namePrettifier:
                    del entry[key]
                    entry[self.namePrettifier[key]] = value
            del entry['Rname']
                            
        self.entryLookupByID = entryLookupByID
        #print allDrugIDsByType.keys()
        allDrugIDs = set.union(*allDrugIDsByType.values())
        #print len(allDrugIDs)
        self.allDrugIDsByType = allDrugIDsByType
        self.allDrugIDs = allDrugIDs
    
    def inCMAP(self, ids, type = None):
        if type and not type in self.allDrugIDsByType:
            print str(type) + ' is not in the list of accepted types.'
            return False
        ids = deepcopy(ids)
        if (isinstance(ids, list) or isinstance(ids, set)) and isinstance(next(iter(ids)), basestring):
            for index, id in enumerate(ids):
                if not type:
                    ids[index] = (id, id.lower() in self.allDrugIDs)
                else:
                    ids[index] = (id, id.lower() in self.allDrugIDsByType[type])
            return ids
        elif isinstance(ids, basestring):
            if not type:
                return ids.lower() in self.allDrugIDs
            else:
                return ids.lower() in self.allDrugIDsByType[type]
        else:
            if (isinstance(ids, list) or isinstance(ids, set)):
                print str(type(next(iter(ids)))) + ' is not a valid input type for id'
            else:
                print str(type(ids)) + ' is not a valid input type for id'
        return False
        
    def annotateIDs(self, ids):
        drugList = self.inCMAP(ids)
        hits = map(lambda x: x[0], filter(lambda x: x[1],drugList))
        misses = map(lambda x: x[0], filter(lambda x: not x[1],drugList))
        for index, hit in enumerate(hits):
            hits[index] = self.namePrettifier[self.entryLookupByID[hit.lower()]]
        return (hits, misses)
    
    def annotateCMAP(self, hits):
        if not isinstance(hits, set):
            hits = set(hits)
        for row in self.cmap:
            if row['Name'] in hits:
                row['In Query Set'] = 'True'
            else:
                row['In Query Set'] = 'False'
            
        return self.cmap