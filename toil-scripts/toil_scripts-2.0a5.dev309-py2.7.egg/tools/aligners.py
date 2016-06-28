import os

import subprocess

from toil_scripts.lib.programs import docker_call
from toil_scripts.lib.urls import download_url


def run_star(job, cores, r1_id, r2_id, star_index_url):
    """
    Performs alignment of fastqs to bam via STAR

    :param JobFunctionWrappingJob job: passed automatically by Toil
    :param int cores: Number of cores to run star with
    :param str r1_id: FileStoreID of fastq (pair 1)
    :param str r2_id: FileStoreID of fastq (pair 2 if applicable, else pass None)
    :param str star_index_url: STAR index tarball
    :return: FileStoreID from RSEM
    :rtype: str
    """
    work_dir = job.fileStore.getLocalTempDir()
    download_url(url=star_index_url, name='starIndex.tar.gz', work_dir=work_dir)
    subprocess.check_call(['tar', '-xvf', os.path.join(work_dir, 'starIndex.tar.gz'), '-C', work_dir])
    os.remove(os.path.join(work_dir, 'starIndex.tar.gz'))
    # Determine tarball structure - star index contains are either in a subdir or in the tarball itself
    star_index = os.path.join('/data', os.listdir(work_dir)[0]) if len(os.listdir(work_dir)) == 1 else '/data'
    # Parameter handling for paired / single-end data
    parameters = ['--runThreadN', str(cores),
                  '--genomeDir', star_index,
                  '--outFileNamePrefix', 'rna',
                  '--outSAMtype', 'BAM', 'SortedByCoordinate',
                  '--outSAMunmapped', 'Within',
                  '--quantMode', 'TranscriptomeSAM',
                  '--outSAMattributes', 'NH', 'HI', 'AS', 'NM', 'MD',
                  '--outFilterType', 'BySJout',
                  '--outFilterMultimapNmax', '20',
                  '--outFilterMismatchNmax', '999',
                  '--outFilterMismatchNoverReadLmax', '0.04',
                  '--alignIntronMin', '20',
                  '--alignIntronMax', '1000000',
                  '--alignMatesGapMax', '1000000',
                  '--alignSJoverhangMin', '8',
                  '--alignSJDBoverhangMin', '1',
                  '--sjdbScore', '1']
    if r1_id and r2_id:
        job.fileStore.readGlobalFile(r1_id, os.path.join(work_dir, 'R1.fastq'))
        job.fileStore.readGlobalFile(r2_id, os.path.join(work_dir, 'R2.fastq'))
        parameters.extend(['--readFilesIn', '/data/R1.fastq', '/data/R2.fastq'])
    else:
        job.fileStore.readGlobalFile(r1_id, os.path.join(work_dir, 'R1_cutadapt.fastq'))
        parameters.extend(['--readFilesIn', '/data/R1.fastq'])
    # Call: STAR Mapping
    docker_call(tool='quay.io/ucsc_cgl/star:2.4.2a--bcbd5122b69ff6ac4ef61958e47bde94001cfe80',
                work_dir=work_dir, parameters=parameters)
    # Write to fileStore
    transcriptome_id = job.fileStore.writeGlobalFile(os.path.join(work_dir, 'rnaAligned.toTranscriptome.out.bam'))
    sorted_id = job.fileStore.writeGlobalFile(os.path.join(work_dir, 'rnaAligned.sortedByCoord.out.bam'))
    return transcriptome_id, sorted_id


def run_bwakit(job, threads, r1, r2, ref, fai, amb, ann, bwt, pac, sa, uuid, library, platform, program_unit,
               alt=None, rg_line=None, sort=True, trim=False):
    """
    Runs BWA-Kit to align a fastq file or fastq pair into a BAM file

    :param JobFunctionWrappingJob job: Passed by Toil automatically
    :param int threads: Number of threads to use
    :param str r1: FileStoreID of first fastq
    :param str r2: FileStoreID of second fastq (None if not using paired data)
    :param str ref: FileStoreID of reference
    :param str fai: FileStoreID of fai
    :param str amb: FileStoreID of amb
    :param str ann: FileStoreID of ann
    :param str bwt: FileStoreID of bwt
    :param str pac: FileStoreID of pac
    :param str sa: FileStoreID of sa
    :param str uuid: UUID of sample (for readgroup)
    :param str library: library of sample (for readgroup)
    :param str platform: platform of sample (for readgroup)
    :param str program_unit: program unit for sample (for readgroup)
    :param str alt: FileStoreID for alt sequence
    :param str rg_line: rg line. Use the format "@RG\\tID:foo\\tLB:bar" ...
    :param bool sort: If True, sorts the BAM
    :param bool trim: If True, performs adapter trimming
    :return: FileStoreID of BAM
    :rtype: str
    """
    work_dir = job.fileStore.getLocalTempDir()
    file_names = ['r1.fq.gz', 'ref.fa.fai', 'ref.fa', 'ref.fa.amb', 'ref.fa.ann',
                  'ref.fa.bwt', 'ref.fa.pac', 'ref.fa.sa']
    ids = [r1, ref, fai, amb, ann, bwt, pac, sa]
    if r2:
        file_names.insert(1, 'r2.fq.gz')
        ids.insert(1, r2)
    if alt:
        file_names.append('ref.fa.alt')
        ids.append(alt)
    for fileStoreID, name in zip(ids, file_names):
        job.fileStore.readGlobalFile(fileStoreID, os.path.join(work_dir, name))
    # Read groups
    if rg_line:
        rg = rg_line
    else:
        rg = "@RG\\tID:{0}".format(uuid)  # '\' character is escaped so bwakit gets individual '\' and 't' characters
        for tag, info in zip(['LB', 'PL', 'PU', 'SM'], [library, platform, program_unit, uuid]):
            rg += '\\t{0}:{1}'.format(tag, info)
    # BWA Options
    opt_args = []
    if sort:
        opt_args.append('-s')
    if trim:
        opt_args.append('-a')
    # Call: bwakit
    parameters = (['-t', str(threads),
                   '-R', rg] +
                  opt_args +
                  ['-o', '/data/aligned',
                   '/data/ref.fa',
                   '/data/r1.fq.gz'])
    mock_bam = uuid + '.bam'
    outputs = {'aligned.aln.bam': mock_bam}
    if r2:
        parameters.append('/data/r2.fq.gz')
    docker_call(tool='quay.io/ucsc_cgl/bwakit:0.7.12--528bb9bf73099a31e74a7f5e6e3f2e0a41da486e',
                parameters=parameters, inputs=file_names, outputs=outputs, work_dir=work_dir)

    # BWA insists on adding an `*.aln.sam` suffix, so rename the output file
    output_file = os.path.join(work_dir, '{}.bam'.format(uuid))
    os.rename(os.path.join(work_dir, 'aligned.aln.bam'),
              output_file)

    # Either write file to local output directory or upload to S3 cloud storage
    job.fileStore.logToMaster('Aligned sample: {}'.format(uuid))
    return job.fileStore.writeGlobalFile(output_file)
