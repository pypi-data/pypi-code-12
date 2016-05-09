'''
Created on 13 mars 2013

@author: coissac
'''



def fasta(filename):
    
    data = open(filename).readlines()
    prots = {}
    protid= None
    seq = None
        
    for l in data:
        if l[0]=='>':
            protid = l.split()[0][1:]
            seq = prots.get(protid,[])
            prots[protid]=seq
        else:
            seq.append(l.strip())
            
    for p in prots:
        prots[p]=bytes("".join(prots[p]).upper(),encoding="ascii")
        
    return prots

#
#def fasta(filename,kmer=4):
#    
#    data = open(filename).readlines()
#    prots = {}
#    protid= None
#    seq = None
#    
#    hmer = set(i * 4 for i in 'ACDEFGHIKLMNOPQRSTVWY')
#        
#    for l in data:
#        if l[0]=='>':
#            if seq is not None:
#                seq = "".join(seq).upper()
#                seq = set(seq[i:(i+kmer)] for i in range(len(seq)-kmer))
#                prots[protid]=prots.get(protid,set()) | seq
#            protid = l.split()[0][1:]
#            seq = []
#        else:
#            seq.append(l.strip())
#            
#    if seq:
#        seq = "".join(seq).upper()
#        seq = set(seq[i:(i+kmer)] for i in range(len(seq)-kmer))
#        prots[protid]=prots.get(protid,set()) | seq
#        
#    kmers = {}
#    
#    for protid in prots:
#        prots[protid]-=hmer
#        for k in prots[protid]:
#            kmers[k]=kmers.get(k,set()) | set([protid])
#            
#    kmers = dict((k,kmers[k]) for k in kmers if len(kmers[k]) < 10)
#        
#    pk={}
#    for k,ps in kmers.iteritems():
#        protid = ps.pop()
#        pk[protid] = pk.get(protid,set()) | set([k])
#        
#        
#    return prots,kmers,pk
#        
#        
        
        