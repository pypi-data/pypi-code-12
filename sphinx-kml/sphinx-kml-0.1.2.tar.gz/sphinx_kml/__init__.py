import os
import urlparse
import uuid

from docutils import nodes
from jinja2 import Environment, FileSystemLoader
from sphinx.util.compat import Directive


def spec_bool(value):
    if value.lower() not in ('true', 'false', ):
        raise ValueError("Valid options include 'true' and 'false'.")

    return value.lower() == 'true'


def spec_point(value):
    lat, lng = value.split(' ')
    return float(lat), float(lng)


def spec_map_type(value):
    options = {
        'satellite': 'google.maps.MapTypeId.SATELLITE',
        'roadmap': 'google.maps.MapTypeId.ROADMAP',
        'hybrid': 'google.maps.MapTypeId.HYBRID',
        'terrain': 'google.maps.MapTypeId.TERRAIN',
    }
    if value.lower() not in options:
        raise ValueError("Invalid map type %s" % value)

    return options[value.lower()]


class KmlNode(nodes.General, nodes.Element):
    pass


class KMLDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        'center': spec_point,
        'height': int,
        'type': spec_map_type,
        'zoom': int,
        'zoomonclick': spec_bool,
    }

    def run(self):
        env = self.state.document.settings.env
        node = KmlNode()

        node['html_id'] = str(uuid.uuid4())
        node['unique_name'] = env.dlfiles.add_file(
            '',
            urlparse.urljoin(
                env.docname,
                ' '.join(self.arguments)
            )
        )
        node['options'] = self.options

        if 'type' not in node['options']:
            node['options']['type'] = spec_map_type(
                env.config.default_map_type
            )

        return [node]


def visit_kml_node(self, node):
    environment = Environment(
        loader=FileSystemLoader(os.path.dirname(__file__)),
        trim_blocks=True,
    )
    rendered = environment.get_template('google.html').render(
        html_id=node['html_id'],
        kml_url=urlparse.urljoin(
            '/_downloads/',
            node['unique_name'],
        ),
        options=node['options']
    )

    self.body.append(rendered)


def depart_kml_node(self, node):
    pass


def builder_inited(app):
    app.add_javascript(
        'https://maps.googleapis.com/maps/api/js?key=%s' % (
            app.config.google_api_key
        )
    )
    app.add_javascript('KmlMapParser_packed_1.0.js')
    app.add_stylesheet('KmlMapParser_packed.css')

def setup(app):
    app.add_node(
        KmlNode,
        html=(
            visit_kml_node,
            depart_kml_node,
        )
    )
    app.add_directive('kml', KMLDirective)

    app.add_config_value(
        'google_api_key',
        None,
        'html',
    )
    app.add_config_value(
        'default_map_type',
        'satellite',
        'html',
    )
    app.connect('builder-inited', builder_inited)
