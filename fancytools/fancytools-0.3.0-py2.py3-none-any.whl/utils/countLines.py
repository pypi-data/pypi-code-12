import os

def countLines(paths, exclude_files_containing=[],
                      exclude_folders_containing=[],
                      exclude_blank_lines=True,
                      exclude_commented_lines=True,
                      count_only_py_files=True):
    '''
    count and return lines  of all *.py files in the given directory/-ies
    '''
    exclude_files_containing = list(exclude_files_containing)
    exclude_files_containing.append("countLines.py")
    
    loclist = []#number of lines, filepath
    
    if isinstance(paths, basestring):
        paths = [paths]
        
    if not len(paths):
        raise Exception('need one or more paths to count lines')
    
    ignore = [] #ignore these signs ...
    excl = [] #exclude line if first sign is...
    if exclude_blank_lines or exclude_commented_lines:
        ignore.extend([' ', '\t', '\n'])
    if exclude_commented_lines:
        excl.append('#')
    
    for cur_path in paths:
        print 'Check path %s' %cur_path

        for pydir, _, pyfiles in os.walk(cur_path):
            for pyfile in pyfiles:
                if ( (not count_only_py_files or pyfile.endswith(".py") )
                    and not sum([ex in pydir for ex in exclude_folders_containing])
                    and not sum([ex in pyfile for ex in exclude_files_containing]) 
                    ):
                    totalpath = os.path.join(pydir, pyfile)
                    lines = open(totalpath, "r").readlines()
                    #count lines:
                    if ignore:
                        n = 0
                        for l in lines:
                            for i, sign in enumerate(l):
                                if sign not in ignore:
                                    if sign in excl:
                                        i = len(l)
                                    break
                            if i and i < len(l):
                                n += 1
                    else:
                        n = len(lines)
                    loclist.append( ( n,
                                       totalpath.split(cur_path)[1]) )
        
    for linenumbercount, filename in loclist: 
        print "%05d lines in %s" % (linenumbercount, filename)
    
    print "\nTotal: %s lines (%s paths)" %(sum([x[0] for x in loclist]), len(paths))



if __name__ == '__main__':
    import sys
    countLines(sys.argv[1:])