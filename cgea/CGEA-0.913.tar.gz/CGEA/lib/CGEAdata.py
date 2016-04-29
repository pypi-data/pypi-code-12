from file import read_JSON
import os
from sklearn.externals import joblib
dir = os.path.dirname(__file__)

class CGEAdata():
    #Default file locations for data
    data = {"cmap":"data/cmap_1309_entrez.json", 
            "cmapDrugMetaData" : "data/cmapDrugMetaDataOfficial.json", 
            "cmapDrugMetaDataWithOffsides" : "data/cmapDrugMetaDataWithOffsides.json",
            "cmap1309map" : "data/drugPRLidMap.txt",
            "drugbank_carriers_cmap" : "data/annotations/drugbank/carriers_cmap.json", 
            "drugbank_carriers_all" : "data/annotations/drugbank/carriers_all.json",
            "drugbank_targets_cmap" : "data/annotations/drugbank/targets_cmap.json", 
            "drugbank_targets_all" : "data/annotations/drugbank/targets_all.json",
            "drugbank_enzymes_cmap" : "data/annotations/drugbank/enzymes_cmap.json",
            "drugbank_enzymes_all" : "data/annotations/drugbank/enzymes_all.json",
            "drugbank_transporters_cmap" : "data/annotations/drugbank/transporters_cmap.json",
            "drugbank_transporters_all" : "data/annotations/drugbank/transporters_all.json",
            "SEA_alltargets_cmap" : "data/annotations/SEA_alltargets_cmap.json",
            "SEA_alltargets_cmap_MDDR" : "data/annotations/SEA_alltargets_cmap_MDDR.json",
            "ATC_3" : "data/annotations/ATC_3.json",
            "ATC_4" : "data/annotations/ATC_4.json",
            "drugSets_CODIM" : "data/annotations/drugSets_CODIM.json",
            "molFragmentsSize" : "data/annotations/molFragmentsSize.json",
            "sideFx" : "data/annotations/sideFx.json",
            "unifiedCompoundLevelSets" : "data/annotations/unifiedCompoundLevelSets.json",
            "offsides" : "data/annotations/offsides.json",
            "mixmdl" : "data/mixmdl/mixmdl_1309.pkl",
            "nullscores" : "data/nullScores_1309.json"
            }
    
    def __init__(self, data = None):
        for key, value in self.data.items():
            if not os.path.isfile(value):
                self.data[key] = os.path.join(dir, '../'+value)
        self.enrichmentData = {'Known Target Enrichment':self.data['drugbank_targets_cmap'],
                               'Known Enzyme Enrichment':self.data['drugbank_enzymes_cmap'],
                               'Known Transporter Enrichment':self.data['drugbank_transporters_cmap'],
                               'Known Carrier Enrichment':self.data['drugbank_carriers_cmap'],
                               'Known and Predicted Enrichment':self.data['SEA_alltargets_cmap'],
                               'ATC3 Enrichments':self.data['ATC_3'],
                               'ATC4 Enrichments':self.data['ATC_4'],
                               'DITM Enrichments':self.data['drugSets_CODIM'],
                               'Fragment Enrichments':self.data['molFragmentsSize'],
                               'Side Effects - Enrichments':self.data['sideFx'],
                               'Offsides - Enrichments':self.data['offsides']
                               }
        if data:
            try:
                for key, value in files.items():
                    if not key in data:
                        self.data[key] = value
            except TypeError:
                print "Warning: Invalid data input. Must input as a python dictionary"
    
    def get(self, identifier):
        if os.path.isfile(self.data[identifier]):
            return read_JSON(self.data[identifier])
        else:
            return False
    
    def getEnrichmentData(self):
        output = {}
        for key, value in self.enrichmentData.items():
            output[key] = read_JSON(value)
        return output
    
    def getPath(self, identifier):
        return self.data[identifier]
    
    def getModel(self, identifier):
        if os.path.isfile(self.data[identifier]):
            return joblib.load(self.data[identifier]) 
        else:
            return False