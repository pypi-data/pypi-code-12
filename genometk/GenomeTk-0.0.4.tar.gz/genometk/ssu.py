###############################################################################
#
# ssuFinder.py - identify SSU (16S rRNA) in genome bins
#
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import os
import logging

import biolib.seq_io as seq_io
from biolib.external.blast import Blast
from biolib.taxonomy import Taxonomy


class SSU(object):
    """Identify, extract, and classify 16S rRNA genes."""

    def __init__(self, cpus):
        """Initialization."""
        self.logger = logging.getLogger()

        self.cpus = cpus

        file_dir = os.path.dirname(os.path.realpath(__file__))
        hmm_dir = os.path.join(file_dir, 'data_files', 'hmms')
        self.bac_ssu_model = os.path.join(hmm_dir, 'SSU_bacteria.hmm')
        self.ar_ssu_model = os.path.join(hmm_dir, 'SSU_archaea.hmm')
        self.euk_ssu_model = os.path.join(hmm_dir, 'SSU_euk.hmm')

    def _hmm_search(self, seq_file, evalue, output_dir):
        """Identify 16S rRNA genes.

        Parameters
        ----------
        seq_file : str
            File with nucleotide sequences in fasta format.
        evalue : float
            E-value threshold for defining valid hits.
        output_dir : str
            Output directory.
        """

        if seq_file.endswith('gz'):
            pipe = 'zcat ' + seq_file + ' | '
        else:
            pipe = 'cat ' + seq_file + ' | '

        output_prefix = os.path.join(output_dir, 'ssu')

        self.logger.info('Identifying bacterial 16S.')
        os.system(pipe + 'nhmmer --noali --cpu %d -o %s.hmm_bacteria.txt -E %s %s -' % (self.cpus, output_prefix, str(evalue), self.bac_ssu_model))

        self.logger.info('Identifying archaeal 16S.')
        os.system(pipe + 'nhmmer --noali --cpu %d -o %s.hmm_archaea.txt -E %s %s -' % (self.cpus, output_prefix, str(evalue), self.ar_ssu_model))

        self.logger.info('Identifying eukaryotic 18S.')
        os.system(pipe + 'nhmmer --noali --cpu %d -o %s.hmm_euk.txt -E %s %s -' % (self.cpus, output_prefix, str(evalue), self.euk_ssu_model))

    def _read_hits(self, results_file, domain, evalue_threshold):
        """Parse hits from nhmmer output.

        Parameters
        ----------
        results_file : str
            Output file from nhmmer to parse.
        domain : str
            Domain of HMM model used.
        evalue_threshold : float
            E-value threshold for defining valid hits.

        Returns
        -------
        dict : d[seq_id] -> information about hit
            Information about hits for individual sequences.
        """

        seq_info = {}

        read_hit = False
        for line in open(results_file):
            if line[0:2] == '>>':
                line_split = line.split()
                seq_id = line_split[1]
                read_hit = True
                hit_counter = 0
            elif line.strip() == '':
                read_hit = False
            elif read_hit:
                hit_counter += 1
                if hit_counter >= 3:
                    line_split = line.split()

                    iEvalue = line_split[3]
                    ali_from = int(line_split[7])
                    ali_to = int(line_split[8])

                    rev_comp = False
                    if ali_from > ali_to:
                        rev_comp = True
                        ali_from, ali_to = ali_to, ali_from

                    align_len = int(ali_to) - int(ali_from)

                    if float(iEvalue) <= evalue_threshold:
                        seq_info[seq_id] = seq_info.get(seq_id, []) + [[domain, iEvalue, str(ali_from), str(ali_to), str(align_len), str(rev_comp)]]

        return seq_info

    def _add_hit(self, hits, seq_id, info, concatenate_threshold):
        """Add hits from individual HMMs and concatenate nearby hits.

        Parameters
        ----------
        hits : d[seq_id] -> information about hit
            Information about hits for individual sequences.
        seq_id : str
            Sequence identifier with hit to add.
        info : list
            Information about hit.
        concatenate_threshold : int
            Concatenate hits within the specified number of base pairs.
        """

        # check if this is the first hit to this sequence
        if seq_id not in hits:
            hits[seq_id] = info
            return

        # check if hits to sequence are close enough to warrant concatenating them,
        # otherwise record both hits
        base_seq_id = seq_id
        index = 1
        bConcatenate = False
        concate_seq_id = seq_id
        while(True):
            # if hits overlap then retain only the longest
            start_new = int(info[2])
            end_new = int(info[3])
            rev_new = bool(info[5])

            start = int(hits[seq_id][2])
            end = int(hits[seq_id][3])
            rev = bool(info[5])

            # check if hits should be concatenated
            if abs(start - end_new) < concatenate_threshold and rev_new == rev:
                # new hit closely preceded old hit and is on same strand
                del hits[seq_id]
                info[2] = str(start_new)
                info[3] = str(end)
                info[4] = str(end - start_new)
                hits[concate_seq_id] = info
                bConcatenate = True

            elif abs(start_new - end) < concatenate_threshold and rev_new == rev:
                # new hit closely follows old hit and is on same strand
                del hits[seq_id]
                info[2] = str(start)
                info[3] = str(end_new)
                info[4] = str(end_new - start)
                hits[concate_seq_id] = info
                bConcatenate = True

            index += 1
            new_seq_id = base_seq_id + '-#' + str(index)
            if bConcatenate:
                if new_seq_id in hits:
                    seq_id = new_seq_id  # see if other sequences concatenate
                else:
                    break
            else:
                # hits are not close enough to concatenate
                if new_seq_id in hits:
                    seq_id = new_seq_id  # see if the new hit overlaps with this
                    concate_seq_id = new_seq_id
                else:
                    hits[new_seq_id] = info
                    break

    def _add_domain_hit(self, hits, seq_id, info):
        """Add hits from different domain models and concatenate nearby hits.

        Parameters
        ----------
        hits : d[seq_id] -> information about hit
            Information about hits for individual sequences.
        seq_id : str
            Sequence identifier with hit to add.
        info : list
            Information about hit.
        """

        if seq_id not in hits:
            hits[seq_id] = info
            return

        base_seq_id = seq_id
        overlap_seq_id = seq_id

        index = 1
        bOverlap = False
        while(True):
            # if hits overlap then retain only the longest
            start_new = int(info[2])
            end_new = int(info[3])
            length_new = int(info[4])

            start = int(hits[seq_id][2])
            end = int(hits[seq_id][3])
            length = int(hits[seq_id][4])

            if (start_new <= start and end_new >= start) or (start <= start_new and end >= start_new):
                bOverlap = True

                if length_new > length:
                    hits[overlap_seq_id] = info
                else:
                    hits[overlap_seq_id] = hits[seq_id]

                if overlap_seq_id != seq_id:
                    del hits[seq_id]

            index += 1
            new_seq_id = base_seq_id + '-#' + str(index)
            if new_seq_id in hits:
                seq_id = new_seq_id  # see if the new hit overlaps with this
                if not bOverlap:
                    overlap_seq_id = seq_id
            else:
                break

        if not bOverlap:
            hits[new_seq_id] = info

    def _identify_ssu(self, genome_file, evalue_threshold, concatenate_threshold, output_dir):
        """Identify 16S rRNA genes.

        Parameters
        ----------
        genome_file : str
            Name of fasta file containing nucleotide sequences.
        evalue_threshold : float
            E-value threshold for defining valid hits.
        concatenate_threshold : int
            Concatenate hits within the specified number of base pairs.
        output_dir : str
            Output directory.

        Returns
        -------
        dict : d[seq_id] -> information about best hit
            Information about best hits.
        """

        # identify 16S reads from contigs/scaffolds
        self._hmm_search(genome_file, evalue_threshold, output_dir)

        # read HMM hits
        hits_per_domain = {}
        for domain in ['archaea', 'bacteria', 'euk']:
            seq_info = self._read_hits(os.path.join(output_dir, 'ssu' + '.hmm_' + domain + '.txt'), domain, evalue_threshold)

            hits = {}
            if len(seq_info) > 0:
                for seq_id, seq_hits in seq_info.iteritems():
                    for hit in seq_hits:
                        self._add_hit(hits, seq_id, hit, concatenate_threshold)

            hits_per_domain[domain] = hits

        # find best domain hit for each sequence
        best_hits = {}
        for _, hits in hits_per_domain.iteritems():
            for seq_id, info in hits.iteritems():
                if '-#' in seq_id:
                    seq_id = seq_id[0:seq_id.rfind('-#')]

                self._add_domain_hit(best_hits, seq_id, info)

        return best_hits

    def _extract_ssu(self, genome_file, best_hits, output_dir):
        """Extract 16S rRNA genes.

        Parameters
        ----------
        genome_file : str
            Name of fasta file containing nucleotide sequences.
        best_hits : d[seq_id] -> information about best hit
            Information about best hits.
        output_dir : str
            Output directory.

        Returns
        -------
        str
            Name of fasta file containing extractracted sequences.
        """

        # write summary file and putative SSU rRNAs to file
        summary_file = os.path.join(output_dir, 'ssu.hmm_summary.tsv')
        summary_out = open(summary_file, 'w')
        summary_out.write('Sequence Id\tHMM\ti-Evalue\tStart hit\tEnd hit\tSSU gene length\tReverse Complement\tSequence length\n')

        ssu_seq_file = os.path.join(output_dir, 'ssu.fna')
        seq_out = open(ssu_seq_file, 'w')

        seqs = seq_io.read(genome_file)

        for seq_id in best_hits:
            orig_seq_id = seq_id
            if '-#' in seq_id:
                seq_id = seq_id[0:seq_id.rfind('-#')]

            seq_info = [orig_seq_id] + best_hits[orig_seq_id]
            seq = seqs[seq_id]
            summary_out.write('\t'.join(seq_info) + '\t' + str(len(seq)) + '\n')

            seq_out.write('>' + seq_info[0] + '\n')
            seq_out.write(seq[int(seq_info[3]) + 1:int(seq_info[4]) + 1] + '\n')

        summary_out.close()
        seq_out.close()

        return ssu_seq_file

    def _classify_ssu(self, seq_file, ssu_db, ssu_taxonomy_file, evalue_threshold, output_dir):
        """Classify 16S rRNA genes.

        Parameters
        ----------
        seq_file : str
            Name of fasta file containing 16S rRNA sequences.
        ssu_db : str
            BLAST database of 16S rRNA genes.
        ssu_taxonomy_file : str
            Taxonomy file for genes in the 16S rRNA database.
        evalue_threshold : float
            E-value threshold for defining valid hits.
        output_dir : str
            Output directory.
        """

        # blast sequences against 16S database
        blast = Blast(self.cpus)
        blast_file = os.path.join(output_dir, 'ssu.blastn.tsv')
        blast.blastn(seq_file, ssu_db, blast_file, evalue=evalue_threshold, max_matches=1, output_fmt='custom')

        # read taxonomy file
        taxonomy = Taxonomy().read(ssu_taxonomy_file)

        # write out classification file
        classification_file = os.path.join(output_dir, 'ssu.taxonomy.tsv')
        fout = open(classification_file, 'w')
        fout.write('query_id\tssu_taxonomy\tssu_length\tssu_blast_subject_id\tssu_blast_evalue\tssu_blast_bitscore\tssu_blast_align_len\tssu_blast_perc_identity\n')

        processed_query_ids = set()
        for line in open(blast_file):
            line_split = [x.strip() for x in line.split('\t')]
            query_id = line_split[0]

            if query_id in processed_query_ids:
                # A query may have multiple hits to different sections
                # of a gene. Blast results are organized by e-value so
                # here only the first hit is considered. The subject gene
                # is the same in all cases so the taxonomy string will
                # be identical.
                continue

            processed_query_ids.add(query_id)
            query_len = int(line_split[1])
            subject_id = line_split[2]
            align_len = line_split[5]
            perc_identity = line_split[6]
            evalue = line_split[7]
            bitscore = line_split[8]

            taxonomy_str = ';'.join(taxonomy[subject_id])

            fout.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (query_id, taxonomy_str, query_len, subject_id, evalue, bitscore, align_len, perc_identity))

        fout.close()

    def run(self, genome_file, evalue_threshold, concatenate_threshold, ssu_db, ssu_taxonomy_file, output_dir):
        """Identify, extract, and classify 16S rRNA genes.

        Parameters
        ----------
        genome_file : str
            Name of fasta file containing nucleotide sequences.
        evalue_threshold : float
            E-value threshold for defining valid hits.
        concatenate_threshold : int
            Concatenate hits within the specified number of base pairs.
        ssu_db : str
            BLAST database of 16S rRNA genes.
        ssu_taxonomy_file : str
            Taxonomy file for genes in the 16S rRNA database.
        output_dir : str
            Output directory.
        """

        self.logger.info('Identifying SSU rRNAs on sequences.')
        best_hits = self._identify_ssu(genome_file, evalue_threshold, concatenate_threshold, output_dir)
        self.logger.info('Identified ' + str(len(best_hits)) + ' putative SSU genes.')

        if len(best_hits):
            self.logger.info('Extracting SSU rRNAs on sequences.')
            ssu_seq_file = self._extract_ssu(genome_file, best_hits, output_dir)

            self.logger.info('Classifying SSU rRNA sequences.')
            self._classify_ssu(ssu_seq_file, ssu_db, ssu_taxonomy_file, evalue_threshold, output_dir)
