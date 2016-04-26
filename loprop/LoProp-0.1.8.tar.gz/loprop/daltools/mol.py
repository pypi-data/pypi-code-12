"""Extract molecular info from Dalton molecule file"""

ll = ('s', 'p', 'd', 'f', 'g', 'h', 'i')

def readin(inputfile):
    """Read from DALTON.BAS"""
    import sys
#
# Read inputfile into list lines
#
    molinp = open(inputfile,'r')
    lines = molinp.readlines()
#
# Check if input format is INTGRL, remove all lines before that
#
    start = lines.index('INTGRL\n')
    if start > 0: del lines[0:start]
#
# Two comment lines
#
    comments = lines[1:3]
#
# Symmetry info extracted form this line
#
    symline = lines[3]
    atom_types = int(symline[1:5])
    charge = float(symline[5:8])
#
# The molecule is a list of atom types which are hashes with structure
#    atom{'charge'} charge of this atom type
#    atom{'label'}  list of atom label strings of this type
#    atom{'center'} list of atom label strings of this type
#    atom{'basis '} structure of form
#                   [angmom][block]{'prim':[], 'cont':[][]}
#
    molecule = []
    for atype in range(atom_types):
        atom = {}
        molecule.append(atom)
        atline = lines.pop(4)
        atfield = atline.split()
#
#   Information for this atom type
#
        atom['charge'] = float(atfield[0])
        unique = int(atfield[1])
        maxl = int(atfield[2])
        atom['label'] = []
        atom['center'] = []
        atom['basis'] = []
#
#   Information for all atoms of this atom type
#
        for at in range(unique):
            line = lines.pop(4)
            field = line.split()
            atom['label'].append([])
            atom['label'][at] = field[0]
            atom['center'].append([])
            for i in range(1, 4): 
                atom['center'][at].append(float(field[i]))
#
#   Information for the basis set of this atom type
#
        for l in range(maxl):
            atom['basis'].append([])
            nbl = int(atfield[3+l])
            for block in range(nbl):
                atom['basis'][l].append([])
                atom['basis'][l][block] = {}
                atom['basis'][l][block]['prim'] = []
                atom['basis'][l][block]['cont'] = []
                line = lines.pop(4)
                field = line.split()
                npr = int(field[1])
                nco = int(field[2])
                for prim in range(npr):
                    line = lines.pop(4)
                    if nco > 3:
                        line += lines.pop(4)
                    if nco > 6:
                        line += lines.pop(4)
                    field = line.split()
                    atom['basis'][l][block]['prim'].append(float(field[0]))
                    atom['basis'][l][block]['cont'].append([])
                    for cont in range(nco):
                        atom['basis'][l][block]['cont'][prim].append(
                            float(field[cont+1])
                            )
    return molecule

def printbasis(molecule):
    """Print molecular info returned by function molecule"""
    i = 0
    for atom in molecule:
        i += 1
        print("Atom type %d charge %f" % (i, atom['charge']))
        for at in range(len(atom['label'])):
            print("center" + " %d "%(at+1) + str(atom['center'][at]))
        for l in range(len(atom['basis'])):
            print("%s-functions" % ll[l])
            for block in range(len(atom['basis'][l])):
                prim = atom['basis'][l][block]['prim']
                cont = atom['basis'][l][block]['cont']
                for ip in range(len(prim)):
                    print("    %s %s"%(prim[ip], cont[ip][:]))


#Test nuclear repulsion

def atoms_in(molecule):
    """Whats this"""
    atomlist = []
    ia = 0
    for atype in molecule:
        for a in atype["center"]:
            atomlist.append({})
            Z = atype["charge"]
            atomlist[ia]["charge"] = Z
            atomlist[ia]["center"] = a
            atomlist[ia]["type"] = atype
            contracted = 0
            for l in range(len(atype['basis'])):
                contracted_l = 0
                for block in range(len(atype['basis'][l])):
                    cont = atype['basis'][l][block]['cont']
                    contracted += len(cont[0])*(2*l+1)
                    contracted_l += len(cont[0])*(2*l+1)
                atomlist[ia][ll[l]] = contracted_l
            atomlist[ia]["contracted"] = contracted
            ia += 1
    return atomlist

def contracted_per_atom(molecule):
    """Return number of contracted per atom"""
    atomlist = atoms_in(molecule)
    contracted = []
    for atom in atomlist:
        contracted.append(atom["contracted"])
    return contracted

def contracted_per_atom_l(molecule):
    """Return number of contracted and angular momentum"""
    atomlist = atoms_in(molecule)
    contracted_l = []
    for i in range(len(atomlist)):
        atom = atomlist[i]
        contracted_l.append([])
        for l in range(len(atom["type"]["basis"])):
            contracted_l[i].append(atom[ll[l]])
    return contracted_l

def occupied_per_atom(molecule):
    """Return number of occupied per atom (assuming ANO type basis)"""
    cpal = contracted_per_atom_l(molecule)
    atomlist = atoms_in(molecule)
    assert len(cpal) == len(atomlist)
    nocclist = []
    for a in range(len(atomlist)):
        offset = 0
        atom = atomlist[a]
        Z = int(atom["charge"]+0.5)
        nocclist.append([])
        for l in range(len(cpal[a])):
            if Z <= 1:
                if l == 0:
                    nocclist[a].append(offset)
            elif Z <= 2:
                if l == 0:
                    nocclist[a].append(offset)
                    nocclist[a].append(offset+1)
            elif Z <= 8:
                if l == 0:
                    nocclist[a].append(offset)
                    nocclist[a].append(offset+1)
                elif l == 1:
                    nocclist[a].append(offset)
                    nocclist[a].append(offset+1)
                    nocclist[a].append(offset+2)
            elif Z <= 18:
                if l == 0:
                    nocclist[a].append(offset)
                    nocclist[a].append(offset+1)
                    nocclist[a].append(offset+2)
                elif l == 1:
                    nocclist[a].append(offset)
                    nocclist[a].append(offset+1)
                    nocclist[a].append(offset+2)
                    nocclist[a].append(offset+3)
                    nocclist[a].append(offset+4)
                    nocclist[a].append(offset+5)
            else:
                raise Exception( "occupied_per_atom:not implemented")
            offset += cpal[a][l]
    return nocclist

def nuc(molecule):
    """Test nuclear repulsion energy"""
    atomlist = atoms_in(molecule)
    Z = 0.0
    for a in atomlist:
        ZA = a["charge"]
        RA = a["center"]
        ia = atomlist.index(a)
        for b in atomlist[:ia]:
            ZB = b["charge"]
            RB = b["center"]
            Z += ZA*ZB/dist(RA, RB)
    return Z

def dist(A, B):
    """distance beteen two atoms"""
    from math import sqrt
    return sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2 + (A[2]-B[2])**2)

if __name__ == "__main__":
    mo = readin("DALTON.BAS")
    printbasis(mo)
