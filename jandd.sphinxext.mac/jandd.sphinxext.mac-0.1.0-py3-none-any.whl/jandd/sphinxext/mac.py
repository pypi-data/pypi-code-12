__version__ = '0.1.0'


from docutils import nodes


def setup(app):
    app.add_generic_role('mac', nodes.literal)
    return {'version': __version__}
