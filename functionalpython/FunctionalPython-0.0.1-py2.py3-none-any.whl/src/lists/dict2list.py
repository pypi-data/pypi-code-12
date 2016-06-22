"""
Return an array given a dictionary"
author: Yuhang(Steven) Wang
date: 06/20/2016
""
def flatten_dict(d):
    def find_keys(obj):
        if isinstance(obj, dict):
            return [x for x in obj.keys()]
        else:
            return []
        
    def aux(obj, keys, atom_accum, result_accum):
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
