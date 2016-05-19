def render(template, mapping):
    """
    Call jinja2 to render a template with mapping

    :param template:
    :param mapping:
    :return:
    """
    from jinja2 import Environment, DictLoader

    env = Environment(loader=DictLoader({
        'cfn': str(template)
    }))
    tpl = env.get_template('cfn')

    return tpl.render(mapping)
