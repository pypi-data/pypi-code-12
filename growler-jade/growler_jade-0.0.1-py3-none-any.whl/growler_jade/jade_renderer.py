#
# growler_jade/jade_renderer.py
#

import logging
from growler.middleware.renderer import RenderEngine


class JadeRenderer(RenderEngine):
    """
    A render engine using the pyjade package to render jade files into mako
    files, which are then turned into html by the mako.template package.
    """
    default_file_extension = '.jade'

    def __init__(self, path):
        """
        Constructor

        Args:
            path (str): Top level directory to search for template files.
        """

        super().__init__(path)

        from pyjade.ext import mako
        from pyjade.ext.mako import preprocessor as mako_preprocessor

        from mako.template import Template
        from mako.lookup import TemplateLookup


        # self._engine = JadeRenderer.mako
        # self._preprocessor = JadeRenderer.mako_preprocessor
        self._render = lambda *args, **kwargs: \
            Template(*args,
                     preprocessor=mako_preprocessor,
                     lookup=TemplateLookup(
                         directories=str(path),
                         preprocessor=mako_preprocessor,
                     ), **kwargs)

        self.log = logging.getLogger(__name__)
        self.log.info("%d Constructed JadeRenderer" % (id(self)))

    def render_source(self, file_path, obj=None):
        """
        Uses pyjade to render the file at file_path

        Params:
            file_path (pathlib.Path): Path to jade text file
            obj (dict): Template data used to fill the jade file.

        Returns:
            (str): The rendered output.
        """

        jade_source = file_path.read_text()
        tmpl = self._render(jade_source)
        html = tmpl.render(**obj)

        return html

    @staticmethod
    def register_engine():
        """
        Add this rendering engine to the standard growler renderer
        """

        import growler.middleware.renderer
        growler.middleware.renderer.render_engine_map['jade'] = JadeRenderer
