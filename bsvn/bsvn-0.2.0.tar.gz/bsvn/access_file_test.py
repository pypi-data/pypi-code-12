

def groups_test():
    """
    >>> import os
    >>> from .svn_access_file import AccessFile
    >>> access_file = AccessFile(os.path.splitext(__file__)[0]+'.ini')
    >>> assert 'HaroldHacker@red-bean.com' in access_file.group_members('calc-developers')
    >>> assert 'HaroldHacker@red-bean.com' in access_file.group_members('calc')
    >>> assert '@calc-developers' not in access_file.group_members('calc')      # no groups
    >>> assert '&harold' not in access_file.group_members('calc')               # no aliases
    >>> assert 'hewlett' in access_file.group_members('calc-owners')
    """

if __name__=='__main__':
    import sys, time
    start = time.time()
    import doctest
    doctest.testmod()
    if '--timed' in sys.argv:
        print(__file__, ": %.03f" % (time.time()-start,), 'seconds')
