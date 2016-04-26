import requests
import shutil
import tempfile
import os

class Restclient(object):

    def __init__(self,host,username,password):
        self.host = host
        self.auth = (username,password)


    def download_study_file(self,studyid,directory=None):
        headers = {'Accept':'application/x-hdf'}
        URL = '%s/provider/study/%s/pvalues.hdf5' % (self.host,studyid)
        r = requests.get(URL,headers=headers,auth=self.auth,stream=True)
        if r.status_code == 200:
            fd,path = tempfile.mkstemp(suffix='.hdf5',dir=directory)
            with os.fdopen(fd,'w') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f) 
            return path
        raise Exception(r.text)

    def get_candidate_genes(self,candidate_gene_id):
        headers = {'Accept':'application/json'}
        URL = '%s/provider/candidategenelist/%s/genes' % (self.host,candidate_gene_id)
        r = requests.get(URL,headers=headers,auth=self.auth)
        if r.status_code == 200:
            return r.json()
        raise Exception(r.text)
    

    def get_phenotype_data(self,studyid):
        headers = {'Accept':'application/json'}
        URL = '%s/provider/study/%s/studygwasdata' % (self.host,studyid)
        r = requests.get(URL,headers=headers,auth=self.auth)
        if r.status_code == 200:
            return r.json()
        raise Exception(r.text)

    def upload_study_file(self,hdf5_file,studyid):
        headers = {'Accept':'application/json'}
        URL = '%s/provider/study/%s/store' % (self.host,studyid)
        files = {'file': ('%s.hdf5'% studyid,open(hdf5_file,'rb'),'application/x-hdf')}
        r = requests.post(URL,headers=headers,auth=self.auth,files=files)
        if r.status_code == 200:
            if r.json() == studyid:
                return
        raise Exception(r.text)
