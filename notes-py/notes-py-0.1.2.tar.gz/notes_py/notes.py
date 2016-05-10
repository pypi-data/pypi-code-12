#!/usr/bin/python3
import sys, os, shutil, getopt, importlib, configparser

import CommonMark

__copyright__ = "Copyright 2016, Maximilian Friedersdorff"
__license__ = "GPLv3"

def usage():
    print(
        "usage: " + sys.argv[0] + " [-c path_to_config] [options]" + os.linesep
        + os.linesep +
        "Options:" + os.linesep +
        "    -h, --help    : Print this help text" + os.linesep +
        "    -c, --config  : Specipy the path to a configuration file" + os.linesep +
        "    -V, --version : Print version and licence info", 
        file=sys.stderr
    )

def version():
    print(
        sys.argv[0] + " 0.0.1" + os.linesep +
        "Licence: GPLv3"
    )


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:V", 
                                   ["help", "config=", "version"])
    except getopt.GetoptError:
        usage()
        return 0 

    _conf = "~/.notes-py.conf"

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            return 0 
        elif opt in ("-c", "--config"):
            _conf = arg
        elif opt in ("-V", "--version"):
            version()
            return 0


    config = configparser.ConfigParser()
    config.read(_conf)
    compile_path = config['DEFAULT']['compile_path']
    content_path = config['DEFAULT']['content_path']
    stylesheet = config['DEFAULT']['stylesheet']
    html_template = config['DEFAULT']['html_template']


    if (os.path.exists(compile_path) and not 
            os.path.isdir(compile_path)):
        raise NotADirectoryError("The compile target path '" + 
                                 compile_path + 
                                 "'exists, but is not a directory!")

    compile(content_path, compile_path, stylesheet, html_template)

def compile(content_path, compile_path, stylesheet, html_template):
    (mds, other) = sep_filetype(content_path, ".md")

    # Prepare dir structure in compile_path
    if os.path.isdir(compile_path):
        shutil.move(compile_path, compile_path + ".old") 

    os.mkdir(compile_path)

    new_dirs = [os.path.dirname(path.replace(content_path, 
                                             compile_path))
                for path in (mds + other)] 

    for d in new_dirs:
        os.makedirs(d, exist_ok=True)

    # Copy all non md files
    for f in other:
        new_path = f.replace(content_path, compile_path)
        # Coply file to new path, but don't follow symlinks!
        shutil.copy2(f, new_path, follow_symlinks=False)

    for f in mds:
        with open(f, "r") as md_f:
            md = md_f.read()

        # Going to use simple str.format to build html to avoid deps with 
        # templating languages
        with open(html_template, 'r') as template_f:
            template = template_f.read()

        compiled_html = template.format(body=CommonMark.commonmark(md), 
                                        stylesheet=stylesheet)

        new_path = f.replace(content_path, compile_path)
        new_path = os.path.splitext(new_path)[0] + ".html"
        with open(new_path, "w") as html_f:
            html_f.write(compiled_html)

    if os.path.isdir(compile_path + ".old"):
        shutil.rmtree(compile_path + ".old")

def sep_filetype(root, ftype):
    """
    Walk along directory tree and separate contained by given ftype.

    Return 2-tuple (ftype_files, other_files) containing lists of files.
    root is the root of the fs tree from which to start the search.
    ftype is the file extention (including leading dot ('.')) by which to 
    separate the files.
    """
    if os.path.isfile(root): 
        if os.path.splitext(root)[-1] == ftype: 
            return ([root], [])
        else:
            return ([], [root])
    elif os.path.isdir(root):
        ret = ([], []) 
        for node in os.listdir(path=root):
            r = sep_filetype(os.path.join(root, node), ftype)
            ret = (ret[0] + r[0], ret[1] + r[1])

            return ret
        else:
            return []

if __name__ == "__main__":
    sys.exit(main())
