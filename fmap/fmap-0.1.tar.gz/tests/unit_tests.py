from fmap._fmap import excluded, applicable

#-------------------------------------------------------------------------------
# Exclusion/Inclusion Utilities

def test_excluded():
    excludes = ['*a', '*b']
    names = ['a', 'b', 'c', 'ca', 'cb', 'ac', 'ab', 'cd', 'e']
    assert list(excluded(names, excludes)) == ['a', 'b', 'ca', 'cb', 'ab']

def test_applicable():
    excludes = ['*a', '*b']
    names = ['a', 'b', 'c', 'ca', 'cb', 'ac', 'ab', 'cd', 'e']
    
    patterns = ['*']
    assert list(applicable(names, patterns, excludes)) == ['c', 'ac', 'cd', 'e']

    patterns = ['*d']
    assert list(applicable(names, patterns, excludes)) == ['cd']

    patterns = ['*d', '*c']
    assert list(applicable(names, patterns, excludes)) == ['c', 'ac', 'cd']

#-------------------------------------------------------------------------------
