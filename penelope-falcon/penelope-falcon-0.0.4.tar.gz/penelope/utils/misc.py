def parse_content_type(content_type):
    mimetype = None
    charset = None

    values = [value.strip() for value in content_type.split(';')]

    mimetype = values[0]

    parameters = values[1:]
    for param in parameters:
        attribute, value = param.split('=')
        if attribute.lower() == 'charset':
            charset = value.lower()

    charset = charset if charset else 'utf-8'

    return mimetype, charset
