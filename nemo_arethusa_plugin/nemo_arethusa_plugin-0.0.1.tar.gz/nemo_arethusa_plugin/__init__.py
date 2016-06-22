from flask_nemo.plugins.annotations_api import AnnotationsApiPlugin
from flask import url_for, jsonify, send_from_directory
from pkg_resources import resource_filename


class Arethusa(AnnotationsApiPlugin):
    """ Arethusa plugin for Nemo

    .. note:: This class inherits some routes from the base `AnnotationsApiPlugin <http://flask-capitains-nemo.readthedocs.io/en/1.0.0b-dev/Nemo.api.html#flask.ext.nemo.plugins.annotations_api.AnnotationsApiPlugin>`_

    :param queryinterface: QueryInterface to use to retrieve annotations
    :type queryinterface: flask_nemo.query.proto.QueryPrototype

    :ivar interface: QueryInterface used to retrieve annotations
    :cvar HAS_AUGMENT_RENDER: (True) Adds a stack of render


    The overall plugins contains three new routes (on top of AnnotationsAPIPlugin) :

        - :code:`/arethusa.deps.json` which feeds informations about Arethusa assets dependencies
        - :code:`/arethusa-assets/<filename>` which is a self implemented assets route.
        - :code:`/arethusa.config.json` which is the config for the widget

    It contains two new templates :

        - a :code:`arethusa::text.html` template which overrides the original when there is treebank available
        - a :code:`arethusa::widget.tree.json` template which providees the configuration for the widget

    It contains a render functions which will use the arethusa::text.html instead of main::text.html if there is a treebank found within the QueryInterface

    """
    HAS_AUGMENT_RENDER = True
    TEMPLATES = {
        "arethusa": resource_filename("nemo_arethusa_plugin", "data/templates")
    }

    ROUTES = AnnotationsApiPlugin.ROUTES + [
        ("/arethusa.deps.json", "r_arethusa_dependencies", ["GET"]),
        ("/arethusa-assets/<path:filename>", "r_arethusa_assets", ["GET"]),
        ("/arethusa.config.json", "r_arethusa_config", ["GET"])
    ]
    
    def __init__(self, queryinterface, *args, **kwargs):
        super(Arethusa, self).__init__(queryinterface=queryinterface, *args, **kwargs)
        self.__interface__ = queryinterface

    @property
    def interface(self):
        return self.__interface__

    def render(self, **kwargs):
        """ Render function stack.

        If the template called is the main::text.html, it checks annotations from its query interface and replace it by arethusa::text.html if there is a treebank annotation

        :param kwargs: Dictionary of named arguments
        :return: Dictionary of named arguments
        """
        update = kwargs
        if "template" in kwargs and kwargs["template"] == "main::text.html":
            total, update["annotations"] = self.interface.getAnnotations(kwargs["urn"])

            if total > 0:
                update["template"] = "arethusa::text.html"
            else:
                del update["annotations"]

        return update

    def r_arethusa_assets(self, filename):
        """ Routes for assets

        :param filename: Filename in data/assets to retrievee
        :return: Content of the file
        """
        return send_from_directory(resource_filename("nemo_arethusa_plugin", "data/assets"), filename)

    def r_arethusa_dependencies(self):
        """ Return the json config of dependencies asked by arethusa

        :return: Json with dependencies
        """
        return jsonify({
            "css": {
                "arethusa": url_for(".r_arethusa_assets", filename="css/arethusa.min.css"),
                "foundation": url_for(".r_arethusa_assets", filename="css/foundation-icons.css"),
                "font_awesome": url_for(".r_arethusa_assets", filename="css/font-awesome.min.css"),
                "colorpicker": url_for(".r_arethusa_assets", filename="css/colorpicker.css",)
            },
            "js": {
                "arethusa": url_for(".r_arethusa_assets", filename="js/arethusa.min.js"),
                "packages": url_for(".r_arethusa_assets", filename="js/arethusa.packages.min.js")
            }
        })

    def r_arethusa_config(self):
        """ Config JSON route for Arethusa : defines the layout and other resources

        :return: {"template"}
        """
        return {
            "template": "arethusa::nemo_arethusa_plugin.json"
        }
