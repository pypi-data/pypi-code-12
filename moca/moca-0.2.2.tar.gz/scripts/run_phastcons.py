from __future__ import division
import os
import numpy as np
import sys
from moca import wigoperations
from moca.bedoperations import fimo_to_sites
from moca.plotter import create_plot
from moca.helpers import read_memefile, get_total_sequences

__root_dir__ = '/media/data1/encode_analysis'
phastcons_file = '/media/data1/genomes/hg19/phastCons/hg19.100way.phastCons.bw'
flank_length = 5
COUNT_TYPE = 'counts'
phastcons_wig = wigoperations.WigReader(phastcons_file)

def touch(fp):
    open(fp, 'a').close()

def save_scores(fimo_dir):

    fimo_file = os.path.join(fimo_dir, 'fimo.txt')
    fimo_sites = fimo_to_sites(fimo_file)

    subset = fimo_sites.loc[:, ['chrom', 'motifStartZeroBased', 'motifEndOneBased', 'strand']]
    subset.loc[:, 'motifStartZeroBased'] = subset['motifStartZeroBased'] - flank_length
    subset.loc[:, 'motifEndOneBased'] = subset['motifEndOneBased'] + flank_length
    intervals = [tuple(x) for x in subset.to_records(index=False)]

    scores_phastcons = phastcons_wig.query(intervals)

    if len(fimo_sites.index):
        scores_phastcons_mean = np.nanmean(scores_phastcons, axis=0)
        np.savetxt(os.path.join(fimo_dir, 'phastcons.raw.txt'), scores_phastcons, fmt='%.4f')
        np.savetxt(os.path.join(fimo_dir, 'phastcons.mean.txt'), scores_phastcons_mean, fmt='%.4f')
    else:
        touch(os.path.join(fimo_dir, 'phastcons.raw.txt'))
        touch(os.path.join(fimo_dir, 'phastcons.mean.txt'))

for d in sorted(os.listdir(__root_dir__)):

    bedfiles = []
    for f in os.listdir(os.path.join(__root_dir__, d)):
        if os.path.splitext(f)[1] == '.sorted':
            bedfiles.append(f)

    if len(bedfiles) != 1:
        sys.stderr.write('Fimo missing: {}\n'.format(d))
        continue

    bedfile = os.path.join(__root_dir__, d, bedfiles[0])

    meme_file = os.path.join(__root_dir__, d, 'moca_output', 'meme_out', 'meme.txt')
    if not os.path.isfile(meme_file):
        continue
    print (d)
    centrimo_dir = os.path.join(__root_dir__, d, 'moca_output', 'centrimo_out')
    meme_info = read_memefile(meme_file)
    total_sequences = get_total_sequences(meme_file)

    for i in range(0, meme_info['total_motifs']):
        record = meme_info['motif_records'][i]

        fimo_sample = os.path.join(os.path.dirname(meme_file), 'fimo_out_{}'.format(i+1))
        fimo_random = os.path.join(os.path.dirname(meme_file), 'fimo_random_{}'.format(i+1))
        save_scores(fimo_sample)
        save_scores(fimo_random)
        try:
            create_plot(meme_file=meme_file,
                        peak_file=bedfile,
                        fimo_file=os.path.join(fimo_sample, 'fimo.sites.txt'),
                        sample_phylop_file=os.path.join(fimo_sample, 'phastcons.mean.txt'),
                        control_phylop_file=os.path.join(fimo_random, 'phastcons.mean.txt'),
                        centrimo_dir=centrimo_dir,
                        sample_gerp_file=os.path.join(fimo_sample, 'gerp.mean.txt'),
                        control_gerp_file=os.path.join(fimo_random, 'gerp.mean.txt'),
                        annotate=False,
                        motif_number=i+1,
                        flank_length=flank_length,
                        out_file_prefix='moca_phastcons',
                        phylop_legend_title = 'PhastCons'
                        )
        except Exception as e:
            sys.stderr.write('{}####\n\n Traceback: {}\n\n'.format(d, e))
