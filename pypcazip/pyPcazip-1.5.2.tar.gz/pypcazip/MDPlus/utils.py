def pib(coords, box):
    """
    Pack coordinates into periodic box.

    Args:
        coords: (N,3) numpy array of atom coordinates.
        box: (3,3) numpy array of box parameters.

    Returns:
        coords: (N,3) numpy array of packed coordinates (overwrites input).
    """

    assert len(coords.shape) == 2
    assert coords.shape[1] == 3
    assert box.shape == (3, 3)

    boxinv = np.zeros((3))
    boxinv[0] = 1.0 / box[0,0]
    boxinv[1] = 1.0 / box[1,1]
    boxinv[2] = 1.0 / box[2,2]

    for xyz in coords:
        s = np.floor(xyz[2] * boxinv[2])
        xyz[2] -= s * box[2,2]
        xyz[1] -= s * box[2,1]
        xyz[0] -= s * box[2,0]

        s = np.floor(xyz[1] * boxinv[1])
        xyz[1] -= s * box[1,1]
        xyz[0] -= s * box[1,0]

        s = np.floor(xyz[0] * boxinv[0])
        xyz[0] -= s * box[0,0]

    return coords
def pdb2selection(pdbfile):
    '''
    iCreate selection strings from pdbfile data.

    A little utility function to convert 'mask' pdb files into
    MDTraj-style selection strings. Basically it reads the second column
    (atom number) and uses it to construct 'index' selections. Runs
    of consecutive numbers are expressed in 'start to stop' form.

    Args:
        pdbfile (str): Name of a PDB file

    Returns:
        selection (str): MDtraj format selection string
    '''

    sel = ''
    i = 0
    j = 0
    with open(pdbfile, 'r') as f:
        for line in f:
            if line.find('ATOM') == 0 or line.find('HETATM') == 0:
                k = int(line.split()[1])
                # the next line catches the initialization process:
                if i == 0:
                    i = k
                    j = k - 1
                # are we in a run of consecutive numbers?:
                if k == j + 1:
                    j = k
                else:
                    # time to write out another selection:
                    sel = sel + ' index {0} to {1} or'.format(i, j)
                    i = k
                    j = k
                # end-of-file reached. Make sure last selection is included:
    if i > 0 and j > 0:
        sel = sel + ' index {0} to {1} or'.format(i, j)
    if len(sel) > 3:
        # remove the trailing ' or':
        sel = sel[:-3]
    return sel

