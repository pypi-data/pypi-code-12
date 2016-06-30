import logging


logger = logging.getLogger(__name__)


def process_transform(**attrs):
    transform = []

    if 'x' in attrs or 'y' in attrs:
        x = float(attrs.get('x', 0))
        y = float(attrs.get('y', 0))

        transform.append(
            "translate(%s,%s)" % (x, y)
        )

    if 'scaleX' in attrs or 'scaleY' in attrs:
        transform.append("scale(%s,%s)" % (
            float(attrs.get('scaleX', '1')), 
            float(attrs.get('scaleY', '1')),
        ))

    if 'rotation' in attrs:
        transform.append("rotate(%s)" % attrs['rotation'])

    return {
        'transform': ' '.join(transform)
    } if len(transform) > 0 else {}


def get_attribute(element, attrname):
    if element is None:
        return None
    if attrname in element.attrib:
        return element.attrib[attrname]
    return get_attribute(element.getparent(), attrname)


def populate_transform(element):
    for ch in element:
        if 'transform' in ch.attrib:
            # ch.set('transform', '%s %s' % (ch.attrib['transform'], element.attrib['transform']))
            ch.set('transform', '%s %s' % (element.attrib['transform'], ch.attrib['transform']))
        else:
            ch.set('transform', element.attrib['transform'])
        if ch.tag in ('clipPath', 'g'):
            populate_transform(ch)
    del element.attrib['transform']
