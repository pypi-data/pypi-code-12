#!/usr/bin/python
#
# Copyright (c) 2015 Mikkel Schubert <MSchubert@snm.ku.dk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os

from paleomix.node import \
    MetaNode

from paleomix.tools.cnv_pipeline.steps.nodes import \
    MrFastIndexNode, \
    SplitFASTANode, \
    FASTAKMerNode, \
    MrFastMapNode, \
    CountHitsNode, \
    MergeBedsNode, \
    MaskBedNode, \
    CatFASTANode, \
    MrCNVRPrepNode

from paleomix.common.fileutils import \
    swap_ext


def build_map_kmer_nodes(prefix, reads, indices, dependencies=()):
    kmer_fpaths = []
    kmer_mappings = []

    for contig_fpath, indice_node in indices.iteritems():
        contig_name = os.path.basename(contig_fpath).split(".", 1)[0]

        output_prefix = "%s_%s" % (prefix, contig_name)
        map_node = MrFastMapNode(reads_fpath=reads,
                                 fasta_fpath=contig_fpath,
                                 output_prefix=output_prefix,
                                 dependencies=dependencies + (indice_node,))
        kmer_mappings.append(map_node)
        kmer_fpaths.extend(map_node.output_files)

    output_table = os.path.join(prefix + ".table")
    return CountHitsNode(input_files=kmer_fpaths,
                         output_file=output_table,
                         dependencies=kmer_mappings)


def build_prefix_pipelines(config, makefile):
    nodes = []
    for (key, prefix) in makefile["Prefixes"].iteritems():
        output_dir = os.path.join(config.destination, "prefixes", key)

        # 1. Split FASTA into a FASTA per contig
        node = SplitFASTANode(fasta_fpath=prefix["Path"],
                              output_dir=os.path.join(output_dir, "raw"))

        # 2. Index each contig using MrFAST
        indices = {}
        for contig_fpath, _ in node.contigs:
            indices[contig_fpath] = MrFastIndexNode(contig_fpath,
                                                    dependencies=(node,))

        # 3. Build KMers from each contig
        kmer_nodes = {}
        for contig_fpath, size in node.contigs:
            kmer_dir = os.path.splitext(contig_fpath)[0]
            kmer_nodes[contig_fpath] = FASTAKMerNode(fasta_fpath=contig_fpath,
                                                     output_dir=kmer_dir,
                                                     contigs={contig_fpath: size},
                                                     dependencies=(node,))

        # 4. Map each set of MKers against each contig
        kmer_hits_nodes = {}
        for contig_fpath, kmer_node in kmer_nodes.iteritems():
            mapping_nodes = []
            for kmer_fpath in kmer_node.output_files:
                contig_dirname, contig_fname = os.path.split(kmer_fpath)

                prefix = os.path.join(contig_dirname,
                                      contig_fname.split(".")[0])

                kmer_node = build_map_kmer_nodes(prefix=prefix,
                                                 reads=kmer_fpath,
                                                 indices=indices,
                                                 dependencies=(kmer_node,))

                mapping_nodes.append(kmer_node)
            kmer_hits_nodes[contig_fpath] = mapping_nodes

        # 5. Build masking beds from hits
        mask_nodes = {}
        for contig_fpath, size in node.contigs:
            kmer_files = set()
            for kmer_node in kmer_hits_nodes[contig_fpath]:
                kmer_files.update(kmer_node.output_files)

            contig_name = os.path.basename(contig_fpath).split(".", 1)[0]
            bed_fpaths = _get_bed_files(config.mask_dir)
            bed_node = MergeBedsNode(hits_files=kmer_files,
                                     bed_files=bed_fpaths,
                                     output_file=swap_ext(contig_fpath, ".bed"),
                                     contig=contig_name,
                                     dependencies=kmer_hits_nodes[contig_fpath])

            mask_nodes[contig_fpath] = bed_node

        # 6. Build and index masked FASTAs for MrFAST
        for contig_fpath, _ in node.contigs:
            bed_node = mask_nodes[contig_fpath]
            bed_fpath, = bed_node.output_files

            fasta_fpath = os.path.join(output_dir, "mrfast",
                                       os.path.basename(contig_fpath))
            mask_node = MaskBedNode(fasta_fpath=contig_fpath,
                                    bed_fpath=bed_fpath,
                                    output_file=fasta_fpath,
                                    dependencies=(bed_node,))

            index_node = MrFastIndexNode(fasta_fpath,
                                         dependencies=(mask_node,))

            nodes.append(index_node)

        # 7. Build, merge, and index masked FASTAs for MrCNVR
        masked_nodes = []
        masked_fpaths = []
        for contig_fpath, contig_size in node.contigs:
            bed_node = mask_nodes[contig_fpath]
            bed_fpath, = bed_node.output_files

            fasta_fpath = os.path.join(output_dir, "mrcnvr", "contigs",
                                       os.path.basename(contig_fpath))
            mask_node = MaskBedNode(fasta_fpath=contig_fpath,
                                    bed_fpath=bed_fpath,
                                    output_file=fasta_fpath,
                                    slop=16,
                                    contig_size=contig_size,
                                    dependencies=(bed_node,))

            masked_nodes.append(mask_node)
            masked_fpaths.append(fasta_fpath)

        fasta_fpath = os.path.join(output_dir, "mrcnvr", "merged.fasta")
        merge_node = CatFASTANode(fasta_fpaths=masked_fpaths,
                                  output_file=fasta_fpath,
                                  dependencies=masked_nodes)

        conf_node = MrCNVRPrepNode(fasta_fpath=fasta_fpath,
                                   output_file=swap_ext(fasta_fpath, ".conf"),
                                   dependencies=(merge_node,))

        nodes.append(conf_node)

    return MetaNode(description="Prefixes",
                    dependencies=nodes)


def build_reads_pipeline(config, makefile):
    records = _iterate_over_records(makefile)
    for target, sample, library, barcode, record in records:
        print target, sample, library, barcode

    return MetaNode()


def build_pipeline(config, makefile):
    return MetaNode(dependencies=(build_prefix_pipelines(config, makefile),
                                  build_reads_pipeline(config, makefile)))


def _get_bed_files(root):
    result = []
    # FIXME: better handling
    if os.path.isdir(root):
        for fname in os.listdir(root):
            result.append(os.path.join(root, fname))
    return result


# FIXME: Move to common module (also in bam_pipeline.makefile)
def _iterate_over_records(makefile):
    for (target, samples) in makefile["Targets"].items():
        for (sample, libraries) in samples.items():
            for (library, barcodes) in libraries.items():
                for (barcode, record) in barcodes.items():
                    yield target, sample, library, barcode, record
