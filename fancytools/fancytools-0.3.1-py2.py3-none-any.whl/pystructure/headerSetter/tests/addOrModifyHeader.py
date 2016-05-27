import os
from fancytools.pystructure.headerSetter.headerSetter import setHeader

header_start = '#<<<<<<<<<<<<<<<<<<'
header_end =   '#>>>>>>>>>>>>>>>>>>'
header_text = '''#hello word
#give me some
#foo bar'''

package_path = os.path.join( os.path.dirname(__file__), 'testPackage' )

setHeader(package_path,
          header_start, header_end, header_text)