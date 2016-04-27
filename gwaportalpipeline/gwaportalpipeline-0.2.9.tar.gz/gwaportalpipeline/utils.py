import h5py
import numpy 

def get_top_snps(hdf5_file,TOP_SNP_LIMIT):
    f = h5py.File(hdf5_file,'r')
    pvals_group = f['pvalues']
    if 'bonferroni_threshold' in pvals_group.attrs:
        bonferroni_threshold = pvals_group.attrs['bonferroni_threshold']
    else:
        bonferroni_threshold = pvals_group.attrs['bonferroniScore']
    if 'bh_thres' in pvals_group.attrs:
        bh_threshold = pvals_group.attrs['bh_thres']
    else:
        bh_threshold = bonferroni_threshold
    total_positions = None
    total_scores = None
    total_macs = None
    total_mafs = None
    total_chrs = None
    total_overFDR = None
    total_genes = None
    for chr in range(1,6):
        chr_group = pvals_group['chr%s' % chr]
        if total_positions is None:
            total_positions = chr_group['positions'][0:TOP_SNP_LIMIT]
            total_scores = chr_group['scores'][0:TOP_SNP_LIMIT]
            if 'mafs' in chr_group:
                total_mafs = chr_group['mafs'][0:TOP_SNP_LIMIT]
            else:
                total_mafs = numpy.empty([TOP_SNP_LIMIT,],dtype=('float32'))[:]*numpy.nan
            if 'macs' in chr_group:
                total_macs = chr_group['macs'][0:TOP_SNP_LIMIT]
            else:
                total_macs = numpy.empty([TOP_SNP_LIMIT,],dtype=('int32'))[:]*numpy.nan

            total_chrs = [str(chr)] * TOP_SNP_LIMIT
            total_genes = [''] * TOP_SNP_LIMIT
        else:
            total_positions = numpy.append(total_positions,chr_group['positions'][0:TOP_SNP_LIMIT])
            total_scores = numpy.append(total_scores,chr_group['scores'][0:TOP_SNP_LIMIT])
            if 'mafs' in chr_group:
                total_mafs = numpy.append(total_mafs,chr_group['mafs'][0:TOP_SNP_LIMIT])
            else:
                total_mafs = numpy.append(total_mafs,numpy.empty([TOP_SNP_LIMIT,],dtype=('float32'))[:]*numpy.nan)
            if 'macs' in chr_group:
                total_macs = numpy.append(total_macs,chr_group['macs'][0:TOP_SNP_LIMIT])
            else:
                total_macs = numpy.append(total_macs,numpy.empty([TOP_SNP_LIMIT,],dtype=('int32'))[:]*numpy.nan)
            total_chrs.extend([str(chr)]*TOP_SNP_LIMIT)
            total_genes.extend([''] * TOP_SNP_LIMIT)
    total_overFDR  = total_scores > bh_threshold
    data = numpy.rec.fromrecords(zip(total_chrs,total_positions.tolist(),total_scores.tolist(),total_mafs.tolist(),total_macs.tolist(),total_overFDR.tolist(),total_genes),
                                 names ='chr,position,scores,mafs,macs,overFDR,gene')
    #data.sort(key=lambda x:x[2],reverse=True)
    top_snps_sorted = data[numpy.argsort(data['scores'])[::-1]]
    return top_snps_sorted[:TOP_SNP_LIMIT]

