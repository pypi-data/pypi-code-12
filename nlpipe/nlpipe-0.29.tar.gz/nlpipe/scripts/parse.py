"""
Parse articles or text directly
"""
from __future__ import print_function

import sys, argparse

from nlpipe import tasks
from nlpipe.celery import app
from nlpipe import backend

modules = {n.split(".")[-1]: t for (n,t) in app.tasks.iteritems() if n.startswith("nlpipe")}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('module', help='nlpipe module (task) name ({})'.format(", ".join(sorted(modules))),
                    choices=modules, metavar="module")
parser.add_argument('--adhoc', help='Ad hoc: parse sentence directly (provide sentence instead of ids)',
                    action='store_true', default=False)
parser.add_argument('-p', '--print', help='Print results to stdout', action='store_true', default=False)
parser.add_argument('-f', '--force', help='Force re-parse even if result is cached', action='store_true', default=False)
parser.add_argument('target', nargs='+', help='Article id(s) (or text in adhoc mode)')

args = parser.parse_args()
task = modules[args.module]

if args.adhoc:
    if args.target == ["-"]:
        text = sys.stdin.read()
    else:
        text = " ".join(args.target)
    print("Parsing {text!r} using {task}".format(**locals()), file=sys.stderr)
    result = task._process(text)
    print(result)
else:
    aids = [int(x) for x in args.target]
    for aid in aids:
        if args.force and backend.exists(task.doc_type, aid):
            backend.delete_result(task.doc_type, aid)
        
        task.run(aid)
        if args.print:
            result = backend.get_document(aid, task.doc_type)
            print(result.text.encode('utf-8'))
