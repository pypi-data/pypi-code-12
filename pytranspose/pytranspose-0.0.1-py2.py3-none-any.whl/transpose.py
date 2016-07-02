
def transpose (root, dimensions) :
    """transpose

    root and root's children are dict or list.

    root's children with the same level should have the same type.

    dimensions are list of index.

    If object can be accessed as
        [a[0]][a[1]][a[2]]... ,
    same value in returned object can be acceesd as
        [a[d[0]]][a[d[1]]][a[d[2]]] ...
    where d is inverse permutation of dimensions.

    More concretely, if you objects have the following "path",
        [year][month][day]
    transposed object with dimension = [2, 1, 0] can be accessed as
        [day][month][year]

    """
    N = len(dimensions)
    root_target = None
    dim = inverse(dimensions)

    types = [None] * N
    cursor = [None] * N
    key = [None] * N
    index = [None] * N
    path = [None] * N

    cursor[0] = root
    key[0] = get_keys(root)
    index[0] = 0
    n = 0

    while (0 <= n) :
        if (types[n] == None) :
            types[n] = type(cursor[n])

        if (index[n] == len(key[n])) :
            n -= 1
            continue

        if (n + 1 < N) :
            path[n] = key[n][index[n]]
            cursor[n + 1] = cursor[n][key[n][index[n]]]
            key[n + 1] = get_keys(cursor[n + 1])
            index[n + 1] = 0
            index[n] += 1
            n += 1
            continue

        if (root_target == None) :
            root_target = types[dim[0]]()

        path[N - 1] = key[N - 1][index[N - 1]]

        target = root_target
        for i in range(0, N - 1) :
            p = path[dim[i]]
            if (not exist_key(target, p)) :
                append(target, p, types[dim[i + 1]]())
            target = target[p]

        append(target, path[dim[N - 1]], cursor[N - 1][key[N - 1][index[N - 1]]])

        index[N - 1] += 1

    return root_target

def exist_key (dictlike, key) :
    if (isinstance(dictlike, list)) :
        return key < len(dictlike)
    elif (isinstance(dictlike, dict)) :
        return (key in dictlike)

def get_keys (dictlike) :
    if (isinstance(dictlike, list)) :
        return [i for i in range(len(dictlike))]
    elif (isinstance(dictlike, dict)) :
        return [i for i in dictlike.keys()]

def append (dictlike, key, val) :
    if isinstance(dictlike, list) :
        dictlike.append(val)
    elif (isinstance(dictlike, dict)) :
        dictlike[key] = val

def inverse (perm) :
    # http://stackoverflow.com/questions/9185768/inverting-permutations-in-python
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv 
