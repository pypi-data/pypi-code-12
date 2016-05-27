# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def __parse_frontend(b_name, data):
    port = data.get('port')
    mode = data.get('protocol', 'http')
    return dict(balancer_name=b_name,
                port=port,
                mode=mode,
                domains=[],
                pems=[])


def __parse_certificate(b_name, domain, data):
    file_name = '%s_%s' % (b_name, domain)
    fcontent = "\n".join([data['private_key'], data['certificate_chain']])
    pem_file = {file_name: fcontent}
    return file_name, pem_file


def __parse_entrypoints(b_name, open_ports, temp_data, data):
    pem_files = {}
    for entrypoint in data:
        domain = entrypoint.get('domain')
        port = entrypoint.get('port')
        mode = entrypoint.get('protocol')
        if port in open_ports:
            wrapper_domain = dict(domain=domain,
                                  backend_name=b_name)
            temp_data[port]['domains'].append(wrapper_domain)
        else:
            new_frontend = dict(balancer_name=b_name,
                                port=port,
                                mode=mode,
                                domains=[dict(domain=domain,
                                              backend_name=b_name)],
                                pems=[])
            temp_data[port] = new_frontend
        if 'certificate' in entrypoint.keys():
            file_name, pem_file = __parse_certificate(
                b_name, domain, entrypoint['certificate'])
            temp_data[port]['pems'].append(file_name)
            pem_files.update(pem_file)
    return open_ports, temp_data, pem_files


def __parse_backend(b_name, mode, data):
    return dict(name=b_name,
                mode=mode,
                backends=data)


def parse(data, unsupport_protocol):
    if not data:
        data = []
    open_ports = set()
    temp_data = {}
    wrapper_frontends = []
    wrapper_backends = []
    pem_files = {}
    for balancer in data:
        protocol = balancer.frontend.get('protocol', 'http')
        if protocol in unsupport_protocol:
            continue
        b_name = balancer.name

        parse_f = __parse_frontend(b_name, balancer.frontend)
        f_port = parse_f['port']
        open_ports.add(f_port)
        temp_data[f_port] = parse_f

        open_ports, temp_data, pems = __parse_entrypoints(
            b_name, open_ports, temp_data, balancer.entrypoints)
        pem_files.update(pems)
        wrapper_backends.append(
            __parse_backend(b_name, parse_f['mode'], balancer.backends))
    wrapper_frontends = temp_data.values()
    wrapper_frontends.sort(key=lambda frontend: frontend['port'])
    wrapper_backends.sort(key=lambda backends: backends['name'])
    conf = dict(wrapper_frontends=wrapper_frontends,
                wrapper_backends=wrapper_backends)
    return conf, pem_files
