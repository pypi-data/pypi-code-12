from flask import Flask


def create_app(import_name, config, config_name='default', ext_list=None, bp_list=None, **kwargs):
    app = Flask(import_name, **kwargs)
    app_config = config.get(config_name)
    app.config.from_object(app_config)

    if hasattr(app_config, 'init_app'):
        app_config.init_app(app)

    if ext_list and isinstance(ext_list, (list, tuple)):
        for ext in ext_list:
            ext.init_app(app)

    if bp_list and isinstance(bp_list, (list, tuple)):
        for bp in bp_list:
            app.register_blueprint(bp)

    return app