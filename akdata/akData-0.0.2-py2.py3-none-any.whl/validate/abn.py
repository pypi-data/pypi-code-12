

def isValidAbn(abn):
    """Validates a parsed ABN string."""
    weights=(10,1,3,5,7,9,11,13,15,17,19)
    abn=[int(a) for a in abn]
    abn[0]-=1
    abn=[a*w for a,w in zip(abn,weights)]
    r=sum(abn)
    if r%89!=0:
        return False
    return True
