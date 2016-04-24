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
import sys
import logging

from biolib.common import check_file_exists, make_sure_path_exists
from biolib.external.execute import check_dependencies

from genometk.metadata_nucleotide import MetadataNucleotide
from genometk.metadata_genes import MetadataGenes
from genometk.ssu import SSU


class OptionsParser():
    def __init__(self):
        """Initialization"""
        self.logger = logging.getLogger()

    def _read_config_file(self):
        """Read configuration info."""

        cfg_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'genometk.cfg')

        d = {}
        for line in open(cfg_file):
            key, value = line.split('=')
            d[key] = value.strip()

        return d

    def nucleotide(self, options):
        self.logger.info('Calculating nucleotide properties of genome.')

        check_file_exists(options.genome_file)
        make_sure_path_exists(options.output_dir)

        meta_nuc = MetadataNucleotide()
        metadata_values, metadata_desc = meta_nuc.generate(options.genome_file,
                                                           options.contig_break)

        # write statistics to file
        output_file = os.path.join(options.output_dir, 'metadata.genome_nt.tsv')
        fout = open(output_file, 'w')
        for field in sorted(metadata_values.keys()):
            fout.write('%s\t%s\n' % (field, str(metadata_values[field])))
        fout.close()

        # write description to file
        output_file = os.path.join(options.output_dir, 'metadata.genome_nt.desc.tsv')
        fout = open(output_file, 'w')
        for field in sorted(metadata_desc.keys()):
            fout.write('%s\t%s\t%s\n' % (field,
                                         metadata_desc[field],
                                         type(metadata_values[field]).__name__.upper()))
        fout.close()

    def gene(self, options):
        self.logger.info('Calculating gene properties of genome.')

        check_file_exists(options.genome_file)
        check_file_exists(options.gff_file)
        make_sure_path_exists(options.output_dir)

        meta_genes = MetadataGenes()
        metadata_values, metadata_desc = meta_genes.generate(options.genome_file,
                                                                options.gff_file)

        # write statistics to file
        output_file = os.path.join(options.output_dir, 'metadata.genome_gene.tsv')
        fout = open(output_file, 'w')
        for field in sorted(metadata_values.keys()):
            fout.write('%s\t%s\n' % (field, str(metadata_values[field])))
        fout.close()

        # write description to file
        output_file = os.path.join(options.output_dir, 'metadata.genome_gene.desc.tsv')
        fout = open(output_file, 'w')
        for field in sorted(metadata_desc.keys()):
            fout.write('%s\t%s\t%s\n' % (field,
                                         metadata_desc[field],
                                         type(metadata_values[field]).__name__.upper()))
        fout.close()

    def ssu(self, options):
        self.logger.info('Identifying, extracting, and classifying 16S rRNA genes.')

        check_file_exists(options.genome_file)
        check_file_exists(options.ssu_taxonomy_file)
        make_sure_path_exists(options.output_dir)

        ssu = SSU(options.cpus)
        ssu.run(options.genome_file,
                    options.evalue,
                    options.concatenate,
                    options.ssu_db,
                    options.ssu_taxonomy_file,
                    options.output_dir)

    def parse_options(self, options):
        """Parse user options and call the correct pipeline(s)"""

        if options.subparser_name == 'nucleotide':
            self.nucleotide(options)
        elif options.subparser_name == 'gene':
            self.gene(options)
        elif options.subparser_name == 'ssu':
            check_dependencies(['blastn', 'nhmmer'])
            self.ssu(options)
        else:
            self.logger.error('  [Error] Unknown RefineM command: ' + options.subparser_name + '\n')
            sys.exit()

        self.logger.info('Done.')

        return 0
