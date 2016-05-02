

def is_url(ref):
    return ref and any(ref.startswith(scheme) for scheme in ['http', 'https'])
