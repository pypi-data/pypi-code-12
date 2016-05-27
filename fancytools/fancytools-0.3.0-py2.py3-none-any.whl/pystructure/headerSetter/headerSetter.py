import os


def removeHeader(*args, **kwargs):
    kwargs.update({'remove_header':True, 'header_text':None})
    return setHeader(*args, **kwargs)


def setHeader(package_path,
              header_start='', header_end='', header_text='',
              remove_header=False,
              exclude_init=True,exclude_empty_files=True):
    '''
    Adds, modifies removes a header text in all *.py files in a python package
    
    header_start -> string indicating the begin of the header e.g. '#<<<<<<<<<'
    header_text -> the header text e.g. '#copyright John Doe 2033\n#licensed under GPLv3'
    header_end -> string indicating the end of the header e.g. '#>>>>>>>>>'

    package_path -> relative or absolute path of the package to modify e.g. 'C:\\...\\myPackage'
    remove_header -> Set to True to remove the header in every py file in the package
    '''
    
    pkg_name = os.path.split(package_path)[-1]
    
    if not os.path.exists(package_path):
        Exception("ERROR: given path '%s' not valid" %package_path)
        
    py_files = _findPyFiles(package_path, exclude_init)
    print 'found %s py files in package %s' %(len(py_files), pkg_name)
    for path in py_files:
        print path
        _setHeaderInPyFile(path, header_start, header_text, 
                           header_end, remove_header, exclude_empty_files)
    print 'done.'


def _findPyFiles(path, exclude_init):
    inits = []
    def recursive(path):
        for f in os.listdir(path):
            p = os.path.join(path,f)
            if os.path.isdir(p):
                recursive(p)
            elif f.endswith('.py'):
                if not exclude_init or f != '__init__.py':
                    inits.append(p)
    recursive(path)
    return inits


def _setHeaderInPyFile(path, header_start, header_text, 
                       header_end, remove_header, exclude_empty_files):
    with open(path, 'r') as init:
        lines = init.readlines()
    if exclude_empty_files and not len(lines):
        return
    #try to find old header
    start = None
    end = None
    for n,line in enumerate(lines):
        if header_start in line:
            start = n
        if start is not None and header_end in line:
            end  = n
            break
    header_not_found = (start == end == None)
    if header_not_found:
        start = 0
        end = 0
    else:
        if (start == None or end == None) :
            raise Exception("!!! header corrupted in file '%s'" %path)      
    #modify lines:  
    newLines = list(lines[:start])
    if not remove_header:
        newLines.append(header_start + '\n')
        newLines.append(header_text + '\n')
        
        if header_not_found:
            newLines.append(header_end + '\n' + '\n')
        
        newLines.extend(lines[end:])
#         else:
#             #exclude header_end
#             newLines.extend(lines[end+1:])
    else:
        if header_not_found:
            newLines.extend(lines[end:])
        else:
            end += 1
            try:
                if lines[end] == '\n':
                    #if there's an empty line - remove that one as well
                    end += 1
            except:
                pass
            newLines.extend(lines[end:])
            
    #write to file
    with open(path, 'w') as init:
        init.writelines(newLines)
    

