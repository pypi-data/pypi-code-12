from time import sleep

from pronto.obo import Obo
from pronto.owl import OwlXML


if __name__ == '__main__':

    import sys
    path = sys.argv[-1]

    if len(sys.argv) != 3:
        sys.exit(1)

    if path.endswith('obo'):

        ont = Obo(sys.argv[-1])

    elif path.endswith('owl'):

        ont = OwlXML(sys.argv[-1])
        
    if sys.argv[1] == 'json':
        print(ont.json)
    
    elif sys.argv[1] == 'obo':
        print(ont.obo)
    
    elif sys.argv[1] == 'rship':
        for t in ont:
            
            print(t)
            for p in t.parents:
                print('   ┗ parent: ', p)
            

            for c in t.children:
                if c == t.children[-1]:
                    print('   ┗ child:  ', c)
                else:
                    print('   ┣ child:  ', c)         

    elif sys.argv[1] == 'meta':
        for k,m in ont.meta.items():
            print(k,': ',m)


