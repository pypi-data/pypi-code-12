#!/usr/bin/env python2

import argparse
import os.path
import re
import sys
import pprint

global GProfiler
global ParamTransformer

VERSION = "0.2.3"



def debug(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def warn(msg, is_error=0):
    if (is_error):
        msg = "ERROR: " + msg
    else:
        msg = "WARNING: " + msg
    debug(msg)

def err(msg):
    warn(msg, is_error=1)
    sys.exit(1)

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

def import_gprofiler_modules():
    
    """
    Fix import conflicts due to the fact that gprofiler.py and the
    gprofiler package have the same name (for the import mechanism). This
    routine attempts to first load packages from outside the script's
    directory and falls back if this fails. The default is vice versa.
    """
    
    if (os.path.realpath(sys.path[0]) == get_script_dir()):
        sys.path.pop(0) 
    
    def attempt_import():
        global GProfiler
        global ParamTransformer         
        from gprofiler import GProfiler
        from gprofiler import ParamTransformer  
    
    try:
        attempt_import()
    except ImportError as e:
        sys.path.insert(0, get_script_dir())
        attempt_import()

def parse_command_line():
    parser = argparse.ArgumentParser(\
        description = "Query g:Profiler (http://biit.cs.ut.ee/gprofiler).")
    qgroup = parser.add_mutually_exclusive_group(required=True)
    cbgroup = parser.add_mutually_exclusive_group()

    qgroup.add_argument(
        "-q", "--query-file", default=None,
        help="A list of query symbols"
    )
    parser.add_argument(
        "-o", "--organism", default="hsapiens",
        help="The organism name in g:Profiler format"
    )
    parser.add_argument(
        "-a", "--all-results", action="store_true",
        help="All results, including those deemed not significant"
    )
    parser.add_argument(
        "--ordered", action="store_true",
        help="Ordered query"
    )
    parser.add_argument(
        "-r", "--region-query", action="store_true",
        help="The query consists of chromosomal regions"
    )
    parser.add_argument(
        "-e", "--exclude-iea", action="store_true",
        help="Exclude electronic GO annotations"
    )
    parser.add_argument(
        "-u", "--underrep", action="store_true",
        help="Measure underrepresentation"
    )
    parser.add_argument(
        "-E", "--evcodes", action="store_true",
        help="Request evidence codes in output as the final column"
    )
    parser.add_argument(
        "-H", "--hier-sorting", action="store_true",
        help="Sort output into subgraphs"
    )
    parser.add_argument(
        "--hier-filtering", default=None, choices=["moderate", "strong"],
        help="Hierarchical filtering, implies --hier-sorting"
    )
    parser.add_argument(
        "-p", "--max-p-value", default=None, type=float,
        help="Custom p-value threshold"
    )
    parser.add_argument(
        "--min-set-size", default=None, type=int,
        help="Minimum size of functional category"
    )
    parser.add_argument(
        "--max-set-size", default=None, type=int,
        help="Maximum size of functional category"
    )
    parser.add_argument(
        "--min-isect-size", default=None, type=int,
        help="Minimum size of query / functional category intersection"
    )
    parser.add_argument(
        "--max-isect-size", default=None, type=int,
        help="Maximum size of query / functional category intersection"
    )
    parser.add_argument(
        "-c", "--correction-method", default="gSCS", choices=["gSCS", "fdr", "bonferroni"],
        help="Algorithm used for determining the significance threshold"
    )
    parser.add_argument(
        "-d", "--domain-size", default="annotated", choices=["annotated", "known"],
        help="Statistical domain size"
    )
    parser.add_argument(
        "--numeric-ns", default=None,
        help="Namespace to use for fully numeric IDs"
    )
    cbgroup.add_argument(
        "-b", "--custom-bg", default=None,
        help="List of symbols to use as a statistical background"
    )
    cbgroup.add_argument(
        "-B", "--custom-bg-file", default=None,
        help="List of symbols to use as a statistical background (file name)"
    )
    parser.add_argument(
        "-f", "--src-filter", default=None,
        help="Data sources to use, space-separated (e.g. \"GO:BP GO:CC KEGG\")"
    )
    qgroup.add_argument(
        "query", nargs="*", default=[],
        help="Query symbols (if --query-file has not been specified)"
    )

    # Options not passed to GProfiler

    parser.add_argument(
        "-U", "--base-url", default=None,
        help="Use a different base URL for the requests, e.g. the beta version"
    )
    parser.add_argument(
        "-O", "--output", default=None,
        help="Store output in the specified file instead of standard output"
    )
    parser.add_argument(
        "--columns", default=None,
        help="Output nth columns only, separate multiple columns with commas"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=VERSION,
        help="Print version info and exit"
    )
    
    # Parse and set implied options
    
    args = parser.parse_args()
    
    if (args.hier_filtering):
        args.hier_sorting = True

    return args
    

def transform_params(args):

    # Transform command-line parameters into a parameter set
    # expected by g:Profiler API

    pt = ParamTransformer()
    out_params = pt.transform(vars(args), {
        "query"             : [pt.TF_LIST, "query"],
        "query_file"        : [pt.TF_FILE, "query"],
        "custom_bg_file"    : [pt.TF_FILE, "custom_bg"],
        "hier_filtering"    : [pt.TF_MAP, "hier_filtering", {
            "moderate"  : GProfiler.HIERF_MODERATE,
            "strong"    : GProfiler.HIERF_STRONG
        }],
        "correction_method" : [pt.TF_MAP, "correction_method", {
            "gSCS"      : GProfiler.THR_GSCS,
            "fdr"       : GProfiler.THR_FDR,
            "bonferroni": GProfiler.THR_BONFERRONI
        }],
        "domain_size"   : [pt.TF_MAP, "domain_size", {
            "annotated" : GProfiler.DOMAIN_ANNOTATED,
            "known"     : GProfiler.DOMAIN_KNOWN
        }],
        "src_filter"        : lambda in_params, in_param: [\
            in_param, \
            filter(lambda x: len(x), re.split(r"\s+", in_params[in_param]))\
        ]
    }, passthrough=True)

    del(out_params["base_url"])
    del(out_params["columns"])
    del(out_params["output"])
    del(out_params["query_file"])
    del(out_params["custom_bg_file"])

    return out_params

def main():
    args = parse_command_line()
    import_gprofiler_modules()
    
    gp_args = transform_params(args)
    query = gp_args["query"]; del(gp_args["query"])
    columns = None
    outf = None

    # Initialization

    gp = GProfiler(
        "gprofiler.py-official/" + VERSION,
        base_url = args.base_url,
        output_type = GProfiler.OUTPUT_TYPE_LINES
    )

    if (args.columns):
        columns = [int(cid.strip())-1 for cid in re.sub(r"[^\d,]", "", args.columns).split(",")]
        columns.sort()
    if (args.output):
        outf = open(args.output, "w")

    # g:Profiler query

    res = gp.gprofile(query, **gp_args)
    
    for line in res:
        if (columns is not None):
            entries = line.split("\t")
            line = "\t".join([entries[i] for i in columns])
        line = line.rstrip()

        if (outf):
            outf.write(line + "\n")
        else:
            print line

    sys.exit(0);

main()
