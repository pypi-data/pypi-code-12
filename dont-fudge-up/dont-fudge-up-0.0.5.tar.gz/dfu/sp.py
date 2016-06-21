from sphinx.pycode import AttrDocVisitor, ModuleAnalyzer
from os.path import abspath, dirname, join
path = abspath(join(dirname(__file__), '../tests/input.py'))
print path


ma = ModuleAnalyzer.for_file(path, 'input.py')
ma.parse()
print ma.find_tags()
ma.tokenize()
print ma.find_attr_docs()
