import copy
from ._ahocorasick import AhoCorasick

UniversalGeneticCode = {"F" :("TTT","TTC"),
                        "L" :("TTA","TTG","TAG","CTA",'CTG',"CTC","CTT"),
                        "S" :("TCA","TCC","TCG","TCT","AGA","AGC","AGG","AGT"),
                        "Y" :("TAA","TAC","TAT"),
                        "C" :("TGT","TGC"),
                        "W" :("TGA","TGG"),
                        "P" :("CCA","CCG","CCT","CCC"),
                        "H" :("CAT","CAC"),
                        "Q" :("CAA","CAG"),
                        "R" :("CGA","CGC","CGG","CGT","AGA","AGG"),
                        "I" :("ATT","ATC","ATA"),
                        "M" :("ATA","ATG"),
                        "T" :("ACA","ACT","ACG","ACC"),
                        "N" :("AAT","AAC","AAA"),
                        "K" :("AAA","AAG"),
                        "V" :("GTA","GTC","GTG","GTT"),
                        "A" :("GCA","GCC","GCG","GCT"),
                        "D" :("GAT","GAC"),
                        "E" :("GAA","GAG"),
                        "G" :("GGA","GGC","GGG","GGT")}

def listCodons2Dict(codons,offset=0,protein='prot'):
    d = [[(protein,offset)],None,{}]

    for c in codons:
        s = d[2]
        p = 0
        for l in c:
            s[l] = s.get(l,[[(protein,p+offset)],None,{}])
            s=s[l][2]
            p+=1
    
    return d[2]
        
def connect2codons(codon1,codon2,prot='prot'): 
    
    for l1 in codon1:
        for l2 in codon1[l1][2]:
            for l3 in codon1[l1][2][l2][2]:
                codon1[l1][2][l2][2][l3][2]=copy.deepcopy(codon2)
                
def mergeAutomata(automata1,automata2):
    
    for k in automata2:
        if k in automata1:
            automata1[k][0].extend(automata2[k][0])
            mergeAutomata(automata1[k][2], automata2[k][2])
        else:
            automata1[k]=copy.deepcopy(automata2[k])

def cleanAutomata(automata,length=100000,keepOnlyTerminal=True):
    lword=0
    d = automata
    
    stack=[(lword,d)]
    
    while stack:
        lword,d = stack.pop(0)
        lword+=1
        for val in d.itervalues():
            if lword==length:
                val[2]={}
            else:
                stack.append((lword,val[2]))
                
            # Keep only leaves as terminal state 
                
            if keepOnlyTerminal and val[2]:
                val[0]=[]

def buildAutomata(sequence,prot="prot",kup=4):
    
    automata = {}
    kup+=1
        
    for pos in xrange(len(sequence)-kup+1):
        peptide = sequence[pos:(pos+kup)]
        print(peptide)
        bt= [listCodons2Dict(UniversalGeneticCode[peptide[x]],
                             (pos+x)*3,
                             prot) 
             for x in xrange(kup)
            ]
        for shift in xrange(kup-1,0,-1):
            print(shift)
            connect2codons(bt[shift-1],bt[shift],prot) 
            
        autopep = bt[0]
        mergeAutomata(automata, autopep)
        for k in autopep:
            autopep2 = autopep[k][2]
            mergeAutomata(automata, autopep2)
            for k2 in autopep2:
                mergeAutomata(automata, autopep2[k2][2])
                
    cleanAutomata(automata, (kup-1)*3)
                    
    return automata
            
        
        
    

def automataIterator(automata):
    word=""
    d = automata[1]
    
    stack=[(word,d)]
    
    while stack:
        word,d = stack.pop(0)
        for k,val in d.iteritems():
            if k!='*':
                seq = word+k
            else:
                seq = word
            if isinstance(val, dict):
                stack.append((seq,val))
            if isinstance(val, list):
                yield seq,val

                       
def setLastCodon(codon1,prot='prot'):
    for l1 in codon1[1]:
        if l1!='*':
            for l2 in codon1[1][l1]:
                if l2!='*':
                    for l3 in codon1[1][l1][l2]:
                        if l3!='*':
                            codon1[1][l1][l2][l3]=[(prot,codon1[0]*3+2),None]
                        else:
                            codon1[1][l1][l2][l3]=[(prot,codon1[0]*3+1),None]
                else:
                    codon1[1][l1][l2]=[(prot,codon1[0]*3),None]
        else:
            codon1[1][l1]=[(prot,codon1[0]*3-1),None]

#def buildAutomata(sequence,prot='prot'):
#    bt = [listCodons2Dict(UniversalGeneticCode[sequence[x]],x*3,prot) for x in xrange(len(sequence))]
#    
#    setLastCodon(bt[-1], prot)
#    
#    for x in xrange(len(sequence)-1):
#        connect2codons(bt[-x-2], bt[-x-1], prot)
#        
#    return bt[0]

                
def matchSuffix(automata,suffixe):
    d = automata[1]
    
    for i in xrange(len(suffixe)):
        l = suffixe[i]
        if l in d:
            d=d[l]
        else:
            return None
    return d 

def longestSuffix(automata,seq):
    if seq:
        seq=seq[1:]
        
    d = matchSuffix(automata,seq)
    
    while not isinstance(d, dict):
        seq=seq[1:]
        d = matchSuffix(automata,seq)
        
    return seq,d

def buildErrorLink(automata):
    word=""
    d = automata[1]
    
    stack=[(word,d)]
    
    while stack:
        word,d = stack.pop(0)
        print >>sys.stderr,"Seq length : %d \r" % len(word),
        for k,val in d.iteritems():
            if k!='*':
                seq = word+k
            else:
                seq = word
            if isinstance(val, dict):
                stack.append((seq,val))
            if isinstance(val, list):
                val[1]=longestSuffix(automata, word)[1]
                
