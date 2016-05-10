#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os,sys

def main():
    filename=''.join(sys.argv[1:])
    if os.path.isfile(filename):
        print 'the file already exists'
    elif not filename.endswith('.py'):
        print 'the filename should end with .py'
    else:
        lines=['#!/usr/bin/env python','# -*- coding:utf-8 -*-','\n','\n','if __name__==\'__main__:\'']
        content='\n'.join(lines)
        with open(filename,'w+') as f:
            f.writelines(content)




if __name__=='__main__':

    main()