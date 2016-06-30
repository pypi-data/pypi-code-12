# network renderer based on cytoscape.js;
# see http://cytoscape.github.io/cytoscape.js/

__all__ = (
    "CytoscapeJsNetworkRenderer",)

import json
import logging
import uuid

import base.BaseRenderer
import core.CONTENT_TYPE
from .. import utils

import pydot

_logger = logging.getLogger(__name__)

class CytoscapeJsGraphRenderer (callysto.BaseRenderer):
    def __init__ (self, kernel):
        super(self.__class__, self).__init__(kernel)

        self._is_cytoscapejs_initialized = False
        self._network_layout = "random"
        self._node_label_property = None

    @pre_flight_magic_command("set-layout")
    def set_graph_layout_magic_command (self, code, **kwargs):
        """ Usage:
                set-layout LAYOUT_NAME

            Set the layout for the display; accepted values
            are 'RANDOM', 'GRID', 'CIRCLE', and 'SPRING'
        """
        layout_name = kwargs["LAYOUT_NAME"].lower()

        if (layout_name == "random"):
            self._network_layout = {"name": "random"}

        elif (layout_name == "grid"):
            self._network_layout = {"name": "grid"}

        elif (layout_name == "circle"):
            self._network_layout = {"name": "circle"}

        elif (layout_name == "spring"):
            self._network_layout = {"name": "cose"}
        else:
            raise ValueError("Unknown layout '%s'" % layout_name)

        self._network_layout["fit"] = True
        self._network_layout = json.dumps(self._network_layout)
        _logger.debug("new graph layout: %s" % layout_name)

    @pre_flight_magic_command("set-label")
    def set_node_label_property_magic_command (self, code, **kwargs):
        """ Usage:
                set-label PROPERTY_NAME

            Set the node property that will be used as label
            when display graphs in the Jupyter notebook
        """
        self._node_label_property = kwargs["PROPERTY_NAME"]
        _logger.debug("new node label property: '%s'" % \
            self._node_label_property)

    @renderer("text/vnd.graphviz")
    def network_renderer (self, content, content_type):
        try:
            g = pydot.graph_from_dot_data(content)
        except Exception as e:
            raise Exception("Unable to load DOT document: %s" % e)

        nodes = []
        for node in graph.nodes:
            _logger.debug("NODE %s: %s" % (node, node.properties))
            if (not self._node_label_property in node.properties):
                if (self._node_label_property is None):
                    label = node.ref
                else:
                    raise Exception("Unknown node property '%s'" % \
                        self._node_label_property)
            else:
                label = node.properties[self._node_label_property]

            nodes.append({"data": {
                "id": node.ref,
                "label": label}})

        edges = []
        for edge in graph.relationships:
            _logger.debug("EDGE %s: %s -> %s" % (edge, edge.start_node.ref, edge.end_node.ref))
            edges.append({"data": {
                "source": edge.start_node.ref,
                "target": edge.end_node.ref}})

        unique_id = str(uuid.uuid1()).replace('-', '_')

        # one-time injection of Cytoscape.js-related code
        if (not self._is_cytoscapejs_initialized):
            yield (core.CONTENT_TYPE.JAVASCRIPT, """
                $("head").append('<style type="text/css">%s</style>');
                """ % utils.flatten_text(_CYTOSCAPEJS_CSS))

            self._is_cytoscapejs_initialized = True

        yield (core.CONTENT_TYPE.HTML,
            _CYTOSCAPEJS_CODE_TEMPLATE % {
                "url": _CYTOSCAPEJS_URL,
                "uuid": unique_id,
                "nodes": json.dumps(nodes),
                "edges": json.dumps(edges),
                "layout": self._network_layout})

_CYTOSCAPEJS_CSS = """
    .cytoscape_canvas {
        height: 400px;
        width: 600px;
        display: block;
        left: 0;
        top: 0;
    }
    #info {
        color: #c88;
        font-size: 1em;
        position: absolute;
        z-index: -1;
        left: 1em;
        top: 1em;
    }
    """

_CYTOSCAPEJS_URL = \
    "https://cdnjs.cloudflare.com/ajax/libs/cytoscape/2.5.2/cytoscape.min.js"

_CYTOSCAPEJS_CODE_TEMPLATE = """\
    <script type="text/javascript">
        require(["%(url)s"], function (cytoscape) {
            var cy = cytoscape({
                container: document.getElementById("%(uuid)s"),

                boxSelectionEnabled: false,
                autounselectify: true,

                style: cytoscape.stylesheet()
                    .selector("node").css({
                        "background-color": "#31afdc",
                        "content": "data(label)",
                        "text-valign": "center",
                        "color": "white",
                        "text-outline-width": 2,
                        "text-outline-color": "#31afdc"
                    })
                    .selector("edge").css({
                        "width": 4,
                        "line-color": "#31afdc",
                        "target-arrow-shape": "triangle",
                        "target-arrow-color": "#31afdc"
                    })
                    .selector(":selected").css({
                        "background-color": "black",
                        "line-color": "black",
                        "target-arrow-color": "black",
                        "source-arrow-color": "black"
                    })
                    .selector(".faded").css({
                        "opacity": 0.25,
                        "text-opacity": 0
                    }),

                elements: {
                    nodes: %(nodes)s,
                    edges: %(edges)s
                },

                layout: %(layout)s
            });

            cy.resize();
            console.log("initialized cytoscape.js");
/*
            cy.on("tap", "node", function (event){
                var node = event.cyTarget;
                var neighborhood = node.neighborhood().add(node);

                console.log("tapped " + node.id());

                cy.elements().addClass("faded");
                neighborhood.removeClass("faded");
            });

            cy.on("tap", function(event) {
                if (event.cyTarget === cy) {
                    cy.elements().removeClass("faded");
                }
            });*/
        });
    </script>
    <div id="%(uuid)s" class="cytoscape_canvas"></div>
    """
