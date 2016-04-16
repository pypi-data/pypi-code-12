import os
import sys
from fmap import fmap
from tempfile import mkstemp
from subprocess import Popen, PIPE

DIR = os.path.abspath(os.path.dirname(__file__))
TESTDIR = os.path.join(DIR, 'tree')

#-------------------------------------------------------------------------------

def test_fmap():
    seen = []
    def accum(name):
        seen.append(name)

    fmap(TESTDIR, accum)
    assert set(seen) == {'c', 'd', 'f', 'g', 'h'}

    del seen[:]
    fmap(TESTDIR, accum, max_depth=0)
    assert set(seen) == {'c', 'd'}

    del seen[:]
    fmap(TESTDIR, accum, apply_dirs=True)
    assert set(seen) == {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}

    del seen[:]
    fmap(TESTDIR, accum, apply_dirs=True, max_depth=0)
    assert set(seen) == {'a', 'b', 'c', 'd'}

    del seen[:]
    fmap(TESTDIR, accum, excludes=['a'])
    assert set(seen) == {'c', 'd', 'h'}

    del seen[:]
    fmap(TESTDIR, accum, patterns=['g', 'd', 'h'], excludes=['a'])
    assert set(seen) == {'d', 'h'}

#-------------------------------------------------------------------------------

def test_main():
    from fmap import main
    main = main.main
    main('-x', '*', 'echo')

    _, path = mkstemp()
    tf = open(path, 'rt')

    cmd = 'echo {{}} >> {}'.format(path)
    def seen():
        tf.seek(0)
        out = tf.read()
        seen = map(os.path.basename, filter(bool, out.split('\n')))
        with open(path, 'wt') as f:
            f.write('')
        return set(seen)

    main('-r', TESTDIR, cmd)
    assert seen() == {'c', 'd', 'f', 'g', 'h'}

    main('-r', TESTDIR, '-z0', cmd)
    assert seen() == {'c', 'd'}

    main('-r', TESTDIR, '-z0', '-p', cmd)
    assert seen() == set()

    argv = sys.argv
    sys.argv = ['', '-r', TESTDIR, cmd]
    main()
    assert seen() == {'c', 'd', 'f', 'g', 'h'}
    sys.argv = argv

    tf.close()
    os.remove(path)

#-------------------------------------------------------------------------------

def test_fmap_invocation():
    def seen(p):
        out = p.communicate()[0].decode('utf-8')
        seen = map(os.path.basename, filter(bool, out.split('\n')))
        return set(seen)

    p = Popen('fmap -r {} echo'.format(TESTDIR), stdout=PIPE, shell=True)
    assert seen(p) == {'c', 'd', 'f', 'g', 'h'}

    p = Popen('fmap -r {} -z0 echo'.format(TESTDIR), stdout=PIPE, shell=True)
    assert seen(p) == {'c', 'd'}

    p = Popen('fmap -r {} -d echo'.format(TESTDIR), stdout=PIPE, shell=True)
    assert seen(p) == {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}

    p = Popen('fmap -r {} -d -z0 echo'.format(TESTDIR), stdout=PIPE, shell=True)
    assert seen(p) == {'a', 'b', 'c', 'd'}

    p = Popen('fmap -r {} -x a echo'.format(TESTDIR), stdout=PIPE, shell=True)
    assert seen(p) == {'c', 'd', 'h'}
    
    p = Popen('fmap -r {} -x a echo g d h'.format(TESTDIR), stdout=PIPE, 
              shell=True)
    assert seen(p) == {'d', 'h'}

    p = Popen('python -m fmap -r {} -x a echo g d h'.format(TESTDIR), 
              stdout=PIPE, shell=True)
    assert seen(p) == {'d', 'h'}

#-------------------------------------------------------------------------------
