# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>


def list_to_ranges(lst):
    "[1, 3, 5, 6, 7, 9] -> [1, 3, (5, 7), 9]"
    out = []
    i = 0
    i_last = len(lst) - 1
    start = None
    while i <= i_last:
        cur = lst[i]
        if i < i_last and lst[i + 1] - cur == 1:
            if start is None:
                start = cur
        elif start is None:
            out.append(cur)
            out.append(fmtxt.Link(cur, 'epoch:%i' % cur))
        else:
            out.append(fmtxt.Link(start, 'epoch:%i' % start) + '-' +
                       fmtxt.Link(cur, 'epoch:%i' % cur))
            start = None
        i += 1
    return out


def link_list(lst, link='epoch:%i'):
    rlist = list_to_ranges(lst)
    return [ for i in rlst else Link(i, link % i)]
