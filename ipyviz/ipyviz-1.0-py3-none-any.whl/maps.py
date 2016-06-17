import folium
from IPython.display import HTML


def plot_map(values=[], connections=[], height=300, radius=80, **kwargs):
    """
    Plot a map

    :param values: The coordinates to be plotted on the map
    :type values: :class:`list`
    :param connections: A list of connections between the nodes
    :type connections: :class:`list`
    :param height: The height on the map in `pixels`
    :type height: :class:`int`
    :param radius: The radius of the nodes
    :type radius: :class:`int`
    :param kwargs: Keyword arguments to be passed to :class:`folium.Map`
    :type kwargs: :class:`dict`
    :return: The IPython HTML output
    :rtype: :class:`IPython.display.HTML`
    """
    tileset = "http://b.tile.stamen.com/toner/{z}/{x}/{y}@2x.png"
    map = folium.Map(tiles=tileset,
                     attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                     **kwargs)
    for value in values:
        label_string = value['label'] if 'label' in value else None
        map.circle_marker(location=[value['lat'], value['lon']], radius=radius,
                          popup=label_string, line_color='#3186cc',
                          fill_color='#3186cc')

    for connection in connections:
        map.line(locations=[[connection.src.location.latitude, connection.src.location.longitude],
                            [connection.dst.location.latitude, connection.dst.location.longitude]],
                 line_color='#cc3138', )
    map._build_map()
    srcdoc = map.HTML.replace('"', '&quot;')
    html_object = HTML('<iframe srcdoc="{0}" '
                       'style="width: 100%; height: {1}px; '
                       'border: none"></iframe>'.format(srcdoc, height))
    return html_object
