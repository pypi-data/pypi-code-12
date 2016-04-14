import argparse

parser = argparse.ArgumentParser()

sub = parser.add_subparsers()

parser = sub.add_parser() # Pas de changement, sauf arg `onerror`
sub.add_binary("foo")
sub.add_regexp_binaries()
sub.add_prefix_binaries()
sub.add_function(func) # func(args)
sub.add_package("foo") # "python -m foo"
sub.add_iter_modules() # Comme walk_packages, mais non récursif. Set PYTHONPATH accordingly; use "python -m foo". Garder les mêmes options que pkgutil.*
