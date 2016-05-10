"""
This module is used to sort item in list 
"""
def sort_ins(seq,i):
    """
    i is the last item's index
    """
    if i==0:
        return
    sort_ins(seq,i-1)
    j=i
    while  j !=0 :
        if seq[j]<seq[j-1] :
            seq[j],seq[j-1]=seq[j-1],seq[j]
        j=j-1
