mode = 'serve'


def stylesheet(url):
    if mode != 'serve':
        base, ext = url.rsplit('.', 1)
        url = base + '.css'
    return '<link rel="stylesheet" href="%s">' % url


def script(url):
    if mode != 'serve':
        base, ext = url.rsplit('.', 1)
        url = base + '.js'
    return '<script src="%s"></script>' % url
