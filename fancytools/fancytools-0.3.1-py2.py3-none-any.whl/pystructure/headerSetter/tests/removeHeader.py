import os
from fancytools.pystructure.headerSetter.headerSetter import removeHeader

header_start = '#<<<<<<<<<<<<<<<<<<'
header_end =   '#>>>>>>>>>>>>>>>>>>'

package_path = os.path.join( os.path.dirname(__file__), 'testPackage' )


removeHeader(package_path, header_start, header_end)