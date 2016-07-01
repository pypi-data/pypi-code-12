
"""Perform a disk space check on listed hosts.

This module allows for command line or programtic checking of
free disk space on given hosts.
-Ryan Birmingham
"""

import subprocess


class DiskCheck(object):
    """An object to keep track of a disk space search.

    Args:
        warnsize (int): Warn if less than this much disk free, gbytes.
        hostlist: A list, file, or file path containing a list of hosts.
    """

    def __init__(self, warnsize=None, hostlist=None):
        """initalize, trying to normalize input."""
        self.warnsize = int(warnsize)
        # if hostlist looks like a list, then use it
        if type(hostlist) is list:
            self.hostlist = hostlist
        else:
            if type(hostlist) is not file:
                try:
                    hostlist = open(hostlist)
                except IOError:
                    raise IOError('Hostlist file interpreted as path,'
                                  'not found')
                except TypeError:
                    raise TypeError('hostlist input type not understood')
            self.hostlist = hostlist.read().splitlines()

    def __str__(self):
        """Return a string for command line invoke."""
        a = "DiskCheck warning for less than" + self.warnsize + "Gb free on "
        return a + str(self.hostlist)

    def search(self):
        """Search through hosts to see which may have issues."""
        allres = []
        for host in self.hostlist:
            subprocess.call(['ssh', host,
                             "df -g / | tail -1 | awk '{print $4}'"])
            try:
                allres.append([self.host, int(subprocess.stdout)])
            except ValueError:
                raise RuntimeWarning("Host: " + self.host + " not included.")
        result = [x for x in allres if x[1] >= self.warnsize]
        return result

if __name__ == "__main__":
    import sys
    args = [10, ['localhost']]
    for x in range(0, len(sys.argv)-1):
        args[x] = sys.argv[x]
    searcher = DiskCheck(args[0], args[1])
    print((searcher.__str__())+'\n')
    print(searcher.search())
