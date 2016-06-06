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
import gzip
import string
import collections

import pysam

from paleomix.ui import \
    print_warn

from paleomix.node import \
    CommandNode, \
    Node

from paleomix.common.fileutils import \
    safe_coerce_to_frozenset

from paleomix.common.fileutils import \
    try_remove, \
    reroot_path, \
    make_dirs, \
    move_file

from paleomix.atomiccmd.command import \
    AtomicCmd

import paleomix.tools.factory as factory


class SplitReadsNode(Node):
    # TODO: Add options for kmer locations / sizes
    def __init__(self, input_files, output_dir, per_file=4000000,
                 dependencies=()):
        self._output_table = os.path.join(output_dir, "list.txt")
        self._output_files = []
        self._output_dir = output_dir
        self._per_file = per_file

        Node.__init__(self,
                      input_files=input_files,
                      output_files=(self._output_table,),
                      dependencies=dependencies)

    def _run(self, config, temp):
        Node._run(self, config, temp)

        handle = None
        for fpath in sorted(self.input_files):



            output_fpath = os.path.join(temp, "%03i.fasta.gz" % (idx,))
            with gzip.open(output_fpath, "w") as handle:
                pass # FIXME


    def _teardown(self, config, temp):
        moved_files = set()
        try:
            for fname in self._output_files:
                src_fpath = os.path.join(temp, fname)
                dst_fpath = os.path.join(self._output_dir, fname)
                move_file(src_fpath, dst_fpath)
                moved_files.add(dst_fpath)
        except:
            for fpath in moved_files:
                try_remove(fpath)
            raise




class MrCNVRPrepNode(CommandNode):
    def __init__(self, fasta_fpath, output_file, dependencies=()):
        cmd = AtomicCmd(["mrcanavar", "--prep",
                         "-fasta", "%(IN_FASTA)s",
                         "-gaps", "/dev/null",
                         "-conf", "%(OUT_CONF)s"],
                        IN_FASTA=fasta_fpath,
                        OUT_CONF=output_file)

        CommandNode.__init__(self,
                             command=cmd,
                             dependencies=dependencies)


class CatFASTANode(CommandNode):
    def __init__(self, fasta_fpaths, output_file, dependencies=()):
        cmd = factory.new("cat")
        cmd.add_multiple_values(fasta_fpaths)
        cmd.set_kwargs(OUT_STDOUT=output_file)

        CommandNode.__init__(self,
                             command=cmd.finalize(),
                             dependencies=dependencies)


class MaskBedNode(CommandNode):
    def __init__(self, fasta_fpath, bed_fpath, output_file,
                 slop=0, contig_size=float("inf"), dependencies=()):
        self._slop = slop
        self._bed_fpath = bed_fpath
        self._contig_size = contig_size

        cmd = AtomicCmd(["bedtools", "maskfasta",
                         "-fi", "%(IN_FASTA)s",
                         "-bed", "%(TEMP_OUT_BED)s",
                         "-fo", "%(OUT_FASTA)s"],
                        IN_FASTA=fasta_fpath,
                        IN_BED=bed_fpath,
                        TEMP_OUT_BED=os.path.basename(bed_fpath),
                        OUT_FASTA=output_file)

        CommandNode.__init__(self,
                             command=cmd,
                             dependencies=dependencies)

    def _setup(self, config, temp):
        CommandNode._setup(self, config, temp)
        if self._slop:
            records = []
            with open(self._bed_fpath) as handle:
                for contig, start, end in MergeBedsNode.read_bed(self._bed_fpath):
                    start = max(0, start - self._slop)
                    end = min(self._contig_size, end + self._slop)
                    records.append((contig, start, end, None))

            with open(reroot_path(temp, self._bed_fpath), "w") as handle:
                for contig, start, end, _ in CountHitsNode.merge_beds(records):
                    handle.write("%s\t%i\t%i\n" % (contig, start, end))
        else:
            os.symlink(os.path.abspath(self._bed_fpath),
                       os.path.join(temp, os.path.basename(self._bed_fpath)))


class MergeBedsNode(Node):
    def __init__(self, hits_files, bed_files, output_file, contig,
                 max_hits=1, dependencies=()):
        self._contig = contig
        self._bed_files = {}

        for fpath in safe_coerce_to_frozenset(hits_files):
            self._bed_files[fpath] = max_hits
        for fpath in safe_coerce_to_frozenset(bed_files):
            self._bed_files[fpath] = None

        Node.__init__(self,
                      input_files=self._bed_files.keys(),
                      output_files=(output_file,),
                      dependencies=dependencies)

    def _run(self, config, temp):
        Node._run(self, config, temp)

        records = []
        contig = self._contig
        for fpath, max_score in self._bed_files.iteritems():
            bed_records = self.read_bed(fpath=fpath,
                                        contig=contig,
                                        max_score=max_score)
            for contig, start, end in bed_records:
                records.append((contig, start, end, None))

        if not records:
            # Create dummy entry
            records = [("_" + contig, 0, 1, None)]

        output_file, = self.output_files
        with open(reroot_path(temp, output_file), "w") as handle:
            for contig, start, end, _ in CountHitsNode.merge_beds(records):
                handle.write("%s\t%i\t%i\n" % (contig, start, end))

    def _teardown(self, config, temp):
        output_file, = self.output_files
        move_file(reroot_path(temp, output_file), output_file)
        Node._teardown(self, config, temp)

    @classmethod
    def read_bed(cls, fpath, contig=None, max_score=None):
        with open(fpath) as handle:
            for line in handle:
                if line.lstrip().startswith("#"):
                    continue

                fields = line.split("\t")
                if max_score is not None and fields[4] <= max_score:
                    continue

                cur_contig, start, end = fields[:3]
                if contig is None or cur_contig == contig:
                    yield cur_contig, int(start), int(end)


class CountHitsNode(Node):
    def __init__(self, input_files, output_file, dependencies=()):
        self._output_table = output_file
        Node.__init__(self,
                      input_files=input_files,
                      output_files=(output_file,),
                      dependencies=dependencies)

    def _run(self, config, temp):
        Node._run(self, config, temp)
        results = collections.defaultdict(int)
        for fpath in self.input_files:
            with gzip.open(fpath) as handle:
                for line in handle:
                    name, _ = line.split('\t', 1)
                    results[name] += 1

        selection = self.select_parse_and_merge_ranges(results)
        with open(reroot_path(temp, self._output_table), "w") as handle:
            for contig, start, end, count in selection:
                handle.write("%s\t%s\t%s\tNA\t%i\t+\n"
                             % (contig, start, end, count))

    def _teardown(self, config, temp):
        src_fpath = reroot_path(temp, self._output_table)
        move_file(src_fpath, self._output_table)
        Node._teardown(self, config, temp)

    @classmethod
    def select_parse_and_merge_ranges(cls, ranges):
        selection = []
        for key, count in ranges.iteritems():
            if count > 1:
                contig, start, end = cls.split_record(key)
                selection.append((contig, start, end, count))

        return cls.merge_beds(selection)

    @classmethod
    def split_record(cls, record):
        contig, positions = record.rsplit(":", 1)
        start, end = positions.split("-", 1)

        return contig, int(start), int(end)

    @classmethod
    def merge_beds(cls, records):
        records = list(sorted(records))
        if not records:
            return []

        merged = []
        last_contig, last_start, last_end, last_count = records[0]
        for contig, start, end, count in records:
            if last_contig != contig or last_end <= start or count != last_count:
                merged.append((last_contig, last_start, last_end, last_count))
                last_contig, last_start, last_end, last_count \
                    = contig, start, end, count
            else:
                last_end = max(end, last_end)

        merged.append((last_contig, last_start, last_end, last_count))

        return merged


class MrFastIndexNode(CommandNode):
    def __init__(self, fasta_fpath, ws=12, dependencies=()):
        cmd = AtomicCmd(["mrfast",
                         "--index", "%(TEMP_OUT_FASTA)s",
                         "--ws", str(ws)],
                        IN_FASTA=fasta_fpath,
                        TEMP_OUT_FASTA=os.path.basename(fasta_fpath),
                        OUT_INDEX=fasta_fpath + ".index")

        CommandNode.__init__(self,
                             description="<MrFastIndex: %r>" % (fasta_fpath,),
                             command=cmd,
                             dependencies=dependencies)

    def _setup(self, config, temp):
        CommandNode._setup(self, config, temp)

        fasta_fpath = tuple(self.input_files)[0]
        os.symlink(os.path.abspath(fasta_fpath),
                   os.path.join(temp, os.path.basename(fasta_fpath)))


class MrFastMapNode(CommandNode):
    def __init__(self,
                 reads_fpath,
                 fasta_fpath,
                 output_prefix,
                 dependencies=()):
        cmd = AtomicCmd(["mrfast",
                         "--seqcomp", "--outcomp",
                         "--search", "%(IN_FASTA)s",
                         "--seq", "%(IN_READS)s",
                         "-o", "%(TEMP_OUT_MAPPED)s",
                         "-u", "/dev/null",
                         ],
                        IN_FASTA=fasta_fpath,
                        IN_FASTA_INDEX=fasta_fpath + ".index",
                        IN_READS=reads_fpath,
                        TEMP_OUT_MAPPED=os.path.basename(output_prefix + ".sam"),
                        OUT_MAPPED=output_prefix + ".sam.gz")

        CommandNode.__init__(self,
                             description="<MrFastMap: %r -> %r>"
                             % (reads_fpath, output_prefix),
                             command=cmd,
                             dependencies=dependencies)


class FASTAKMerNode(Node):
    def __init__(self,
                 fasta_fpath, output_dir, contigs,
                 kmer_size=36, step_size=5, per_file=4000000,
                 dependencies=()):
        self._fasta_fpath = fasta_fpath
        self._kmer_size = kmer_size
        self._step_size = step_size
        self._per_file = per_file

        n_kmers = 0
        for size in contigs.itervalues():
            n_kmers += (size - kmer_size + step_size) // step_size

        output_files = []
        for counter in xrange((n_kmers + per_file - 1) // per_file):
            output_fname = "%03i.fasta.gz" % (counter, )
            output_files.append(os.path.join(output_dir, output_fname))

        Node.__init__(self,
                      description="<FASTA Kmers: %r -> %r>" \
                          % (fasta_fpath, output_dir),
                      input_files=(fasta_fpath,),
                      output_files=output_files,
                      dependencies=dependencies)

    def _run(self, config, temp):
        Node._run(self, config, temp)

        try:
            handle = None
            records = self.fragment_fasta(self._fasta_fpath,
                                          self._kmer_size,
                                          self._step_size)
            for idx, record in enumerate(records):
                if idx % self._per_file == 0:
                    if handle:
                        handle.close()

                    fname = "%03i.fasta.gz" % (idx % self._per_file,)
                    handle = gzip.open(os.path.join(temp, fname), "w")

                handle.write(record)
        finally:
            if handle:
                handle.close()

    def _teardown(self, config, temp):
        for dst_fpath in self.output_files:
            src_path = reroot_path(temp, dst_fpath)
            move_file(src_path, dst_fpath)

    @classmethod
    def fragment_fasta(cls, filename, kmer_size, step_size):
        with open(filename) as handle:
            position = 0
            offset = 0
            cache = ""
            name = None

            while True:
                while offset + kmer_size < len(cache):
                    yield "%s:%s-%s\n%s\n" \
                        % (name, position, position + kmer_size,
                           cache[offset:offset + kmer_size])
                    offset += step_size
                    position += step_size

                line = handle.readline()
                if line.startswith(">"):
                    position = 0
                    offset = 0
                    cache = ""
                    name = line.split(None, 1)[0]
                elif line:
                    if offset:
                        cache = cache[offset:]
                        offset = 0

                    cache += line.rstrip()
                else:
                    break


class SplitFASTANode(Node):
    def __init__(self, fasta_fpath, output_dir, dependencies=()):
        self._fasta_fpath = fasta_fpath
        self._output_dir = output_dir

        self.contigs = []
        for name, size in _read_contig_list(self._fasta_fpath):
            target = _transform_seq_name(name)
            fpath = os.path.join(output_dir, target + ".fasta")
            self.contigs.append((fpath, size))

        output_files = [os.path.join(output_dir, "list.txt")]
        output_files.extend(fpath for fpath, _ in self.contigs)

        Node.__init__(self,
                      input_files=(fasta_fpath, fasta_fpath + ".fai"),
                      output_files=output_files,
                      dependencies=dependencies)

    def _run(self, _config, temp):
        try:
            last_handle = None
            with open(self._fasta_fpath) as handle:
                for line in handle:
                    if line.startswith(">"):
                        if last_handle:
                            last_handle.close()
                            last_handle = None

                        name = line.split(None, 1)[0][1:]
                        target = _transform_seq_name(name)
                        target_fpath = os.path.join(temp, target + ".fasta")

                        last_handle = open(target_fpath, "w")
                        last_handle.write(line)
                    elif last_handle:
                        last_handle.write(line)
                    else:
                        assert False, self._fasta_fpath
        finally:
            if last_handle:
                last_handle.close()

        make_dirs(self._output_dir)
        with open(os.path.join(self._output_dir, "list.txt"), "w") as handle:
            for fpath, _ in self.contigs:
                handle.write("%s\n" % (os.path.basename(fpath),))

        for fpath_dst, _ in self.contigs:
            fpath_src = os.path.join(temp, os.path.basename(fpath_dst))
            move_file(fpath_src, fpath_dst)


def _transform_seq_name(name):
    valid_chars = string.letters + string.digits
    filtered = []
    for char in name:
        if char in valid_chars:
            filtered.append(char)
        elif not filtered or filtered[-1] != "_":
            filtered.append("_")
    return "".join(filtered)


def _read_contig_list(fpath):
    fai_fpath = fpath + ".fai"
    # TODO: Check permissions / that file exists(?)

    if not os.path.exists(fai_fpath):
        print_warn("Creating index for %r; this may take a while ...\n"
                   % (fpath,))
        pysam.Fastafile(fpath).close()

    with open(fai_fpath) as handle:
        for line in handle:
            fields = line.split('\t', 2)
            yield fields[0], int(fields[1])
