import sys

def print_lol(lines,indent=False,level=0,fn=sys.stdout):
    for each_line in lines:
        if isinstance(each_line,list):
            print_lol(each_line,indent,level+1,fn)
        else:
            if indent:
                for each_item in range(level):
                    print('\t',end='',file=fn)
            print(each_line,file=fn)
        
            
    
        
    
