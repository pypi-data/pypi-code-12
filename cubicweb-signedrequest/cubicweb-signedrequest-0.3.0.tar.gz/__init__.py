"""cubicweb-signedrequest application package

rest api for cubicweb
"""
import logging

def includeme(config):
    """Activate the signedrequest authentication policy in a
    pyramid_cubiweb instance.

    Usually called from the main pyramid_cubicweb.core configurator
    (see ``pyramid_cubicweb.core``).

    See also :ref:`defaults_module`

    """
    import pyramid.tweens
    from cubes.signedrequest.pconfig import SignedRequestAuthPolicy

    policy = SignedRequestAuthPolicy()
    config.add_tween('cubes.signedrequest.pconfig.body_hash_tween_factory',
                     under=pyramid.tweens.INGRESS)

    # add some bw compat methods
    # these ease code factorization between pyramid related code and legacy one
    config.add_request_method(
        lambda req, header, default=None: req.headers.get(header, default),
        name='get_header', property=False, reify=False)
    config.add_request_method(lambda req: req.method,
        name='http_method', property=False, reify=False)

    if config.registry.get('cubicweb.authpolicy') is None:
        err = "signedrequest: the default cubicweb auth policy should be "\
              "available via the 'cubicweb.authpolicy' registry config "\
              "entry"
        raise ValueError(err)

    # if we use (the default) a multiauth policy in CW, append
    # signedrequest to it
    mainpolicy = config.registry['cubicweb.authpolicy']
    mainpolicy._policies.append(policy)
