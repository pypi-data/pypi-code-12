from twisted.web.template import XMLFile
from twisted.python.filepath import FilePath
import pkg_resources


def tloader(basefile):
    return XMLFile(
        FilePath(
            pkg_resources.resource_filename(
                'py3o.fusion',
                'templates/%s' % basefile
            )
        )
    )
