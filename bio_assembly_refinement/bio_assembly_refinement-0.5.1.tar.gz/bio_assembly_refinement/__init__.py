from pkg_resources import get_distribution

try:
    __version__ = get_distribution('bio_assembly_refinement').version
except:
    __version__ = 'local'



__all__ = [ 'contig_cleanup',
			'contig_overlap_trimmer',
			'contig_break_finder',
			'reassembly',
			'utils',
			'prodigal_hit',
			'main'
		   ]
from bio_assembly_refinement import *

