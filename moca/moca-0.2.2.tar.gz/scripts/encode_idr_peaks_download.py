import os
import requests
import shutil
import gzip
import json
from moca.helpers import safe_makedir

__base_url__ = 'https://www.encodeproject.org/'
__root_dir__ = '/media/data1/ENCODE_V3/'

ALLOWED_FILETYPES = ['bed narrowPeak', 'bed broadPeak']

def download_peakfile(source_url, filename, destination_dir):
    """Download peakfile from encode"""
    response = requests.get(source_url, stream=True)
    with open(os.path.join(destination_dir, filename), 'wb') as f:
        shutil.copyfileobj(response.raw, f)

    with gzip.open(os.path.join(destination_dir, filename), 'rb') as in_file:
        with open(os.path.join(destination_dir, filename.replace('.gz','')), 'wb') as out_file:
            out_file.write( in_file.read()  )
    del response


def download_idr_tfs(root_dir, metadata):
    """Download all tfs with idr called peaks"""
    idr_records = fetch_idr_record(metadata)
    ## Theere is only one IDR per sample
    assert len(idr_records) == 1
    for idr_record in idr_records:
        dataset = idr_record['dataset']
        peakfilename = idr_record['peakfilename'] + '.bed.gz'
        dataset_dir = os.path.join(root_dir, dataset)
        safe_makedir(dataset_dir)
        source_url = __base_url__ + idr_record['href']
        download_peakfile(source_url, peakfilename, dataset_dir)
        save_metadata_json(metadata, dataset_dir)
        return {'assembly': idr_record['assembly'],'bedfile': os.path.join(dataset_dir, peakfilename.replace('.gz',''))}

def get_experiment(experiment_id):
    """Get and save metadata for an experiment"""
    req = requests.get("{}experiments/{}/?format=json".format(__base_url__, experiment_id))
    metadata = req.json()
    return metadata

def save_metadata_json(metadata, directory):
    """Save metadata locally"""
    with open('metadata.json', 'w') as outfile:
        json.dump(metadata, outfile)

def filter_metadata(metadata,
                    filter_dict={'files.output_type': 'optimal idr thresholded peaks'}):
    """Can think of supporting one nested key for now"""
    filter_keys = filter_dict.keys()[0].split('.')
    value = filter_dict.values()[0]
    files = metadata['files']
    biosample_term_name = metadata['biosample_term_name']
    assay_term_name = metadata['assay_term_name']
    description = metadata['description']
    gene_name = metadata['target']['label']
    filter_records = []
    for f in files:
        file_status = f['status']
        file_type = f['file_type']
        #output_type = f['output_type']
        filter_1 = f[filter_keys[0]]
        filter_2 = f[filter_keys[1]]
        if filter_2 == value and file_type in ALLOWED_FILETYPES and file_status == 'released':
            dataset = f['dataset']
            dataset = dataset.replace('experiments','').replace('/','')
            href = f['href']
            title = f['title']
            assembly = f['assembly']
            print dataset
            filter_records.append({'href': href,
                                   'metadata':f,
                                   'parent_metadata': metadata,
                                   'dataset': dataset,
                                   'peakfilename': title,
                                   'file_type': file_type,
                                   'file_status': file_status,
                                   'biosample_term_name': biosample_term_name,
                                   'assay_term_name': assay_term_name,
                                   'gene_name': gene_name,
                                   'description': description,
                                   'assembly': assembly})
    return filter_records

def search_encode_tfs():
    url = __base_url__ + '/search?type=Experiment&assay_title=ChIP-seq&limit=all&status=released&target.investigated_as=transcription+factor&format=json'
    req = requests.get(url)
    resp_json = req.json()
    all_samples = resp_json['@graph']
    all_tfs = [sample['target']['label'] for sample in all_samples]
    all_tfs =  set(all_tfs)
    all_experiments = [sample['@id'].strip().replace('/','').replace('experiments', '') for sample in all_samples]
    for experiment in all_experiments:
        expt_metadata = get_experiment(experiment)
        metadata = filter_metadata(expt_metadata)
        download_idr_tfs(__root_dir__, metadata)


if __name__ == '__main__':
    search_encode_tfs()
