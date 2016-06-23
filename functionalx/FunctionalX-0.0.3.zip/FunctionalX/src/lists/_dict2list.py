def dict2list(d: dict) -> list:
    """Return an array given a dictionary"
   
    :param dict d: input dictionary object 

    :return: a list for possible combinations of keys/values
    :rtype: list [['a', 1, 'A'], ['a', 2, 'B'], ['b', 3, 'C'], ['b', 4, 'D']]

    >>> dict2list({
        "a": {
            1: "A",
            2: "B"
        },
        "b": {
            3: "C",
            4: "D"
        }
        })
    [['a', 1, 'A'], ['a', 2, 'B'], ['b', 3, 'C'], ['b', 4, 'D']]
    """
    def find_keys(obj: dict) -> list:
        if isinstance(obj, dict):
            return [x for x in obj.keys()]
        else:
            return []
        
    def aux(obj: dict, keys, atom_accum: list, result_accum: list) -> list:
        if len(keys) == 0:
            return result_accum + [atom_accum + [obj]]
        elif len(keys) == 1:
            k = keys[0]
            return aux(obj[k], find_keys(obj[k]), atom_accum + [k], result_accum)
        else:
            k_now = keys[0]
            k_next = keys[1]
            return aux(
                    obj[k_next], 
                    find_keys(obj[k_next]), 
                    atom_accum + [k_next], 
                    aux(obj[k_now], find_keys(obj[k_now]), atom_accum + [k_now], result_accum)
                    )
        
    if not isinstance(d, dict):
        return []
    else:
        return aux(d, find_keys(d), [], [])
