# encoding: utf-8
import json
import re

def parse_top(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    headers = stdout_lines[0]
    content = stdout_lines[1:]

    headers = headers.split()
    rows = [line.split(None, len(headers) - 1) for line in content]
    return {'Titles': headers, "Processes": rows }

def parse_ps(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    headers = stdout_lines[0]
    content = stdout_lines[1:]
    rows = [line.split() for line in content]
    return [{'Id': row[0],
             'Image': row[1],
             'Name': row[-1]} for row in rows if row]

def parse_build(stdout_raw):
    #TODO: adjust output
    stdout_lines = filter(None, stdout_raw.split('\n'))
    last_line = stdout_lines[-1]
    success_search = r'Successfully built ([0-9a-f]+)'
    match = re.search(success_search, last_line)
    return {'Id': match.group(1) if match else None}

def parse_id(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    return {'Id': stdout_lines[0]}

def parse_name(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    return {'Name': stdout_lines[0]}

def parse_port(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    if not stdout_lines:
        return None

    if len(stdout_lines[0].split('->')) == 1: # only host ip and port
        return _parse_ip_port(stdout_lines[0])

    port_map = {}
    for line in stdout_lines:
        cnt_port, host_ip_port = line.split('->')
        port_map[cnt_port.strip()] = _parse_ip_port(host_ip_port)

    return port_map

def _parse_ip_port(line):
    ip, port = line.strip().split(':')
    return {'HostIp': ip, 'HostPort': port}

def parse_images(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    headers = stdout_lines[0]
    content = stdout_lines[1:]
    rows = [line.split() for line in content]
    items = [{'repository': row[0],
             'tag': row[1],
             'digest': row[2] if 'DIGEST' in headers else None,
             'id': row[3] if 'DIGEST' in headers else row[2]} for row in rows if row]

    images = {}
    for item in items:
        if images.get(item['id']):
            images[item['id']]['RepoTags'].append(item['repository'] + ':' + item['tag'])
            images[item['id']]['RepoDigests'].append((item['repository'] + '@' + item['digest']) if item['digest'] else None)
        else:
            images[item['id']] = {
                'Id': item['id'],
                'RepoTags': [item['repository'] + ':' + item['tag']],
                'RepoDigests': [(item['repository'] + '@' + item['digest']) if item['digest'] else None]
            }

    images_list = []
    for id, image in images.iteritems():
        image['RepoDigests'] = filter(None, image['RepoDigests'])
        image['RepoTags'] = filter(None, image['RepoTags'])
        images_list.append(image)

    return images_list

def parse_history(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    headers = stdout_lines[0]
    content = stdout_lines[1:]
    rows = [line.split() for line in content]
    return [{'Id': row[0]} for row in rows if row]

def parse_inspect(stdout_raw):
    return json.loads(stdout_raw)

def parse_diff(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    result = list()
    for line in stdout_lines:
        kind, path = line.split(None, 1)
        result.append({"Path": path, "Kind": {'C': 0, 'A': 1, 'D': 2}[kind]})
    return result or None

def parse_colon(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    result = dict()
    for line in stdout_lines:
        key, val = line.split(':', 1)
        result[key.strip()] = val.strip()
    return result or None

def parse_version(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    first_line = stdout_lines[0]
    key, val = first_line.split(':', 1)
    if key == 'Client': #new 1.8.0 output
        return _parse_version_1_8_0(stdout_raw)
    else:
        return _parse_version_old(stdout_raw)

def _parse_version_1_8_0(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    parsed = {"Client": {}, "Server": {}}
    glines = (line for line in stdout_lines)
    for line in glines:
        key, val = line.split(':', 1)
        if key == 'Client': continue
        if key == 'Server': break
        parsed['Client'][key.strip()] = val.strip()
    for line in glines:
        key, val = line.split(':', 1)
        parsed['Server'][key.strip()] = val.strip()

    def get_result(parsed):
        os_arch = parsed.get("OS/Arch")
        os, arch = os_arch.split('/') if os_arch else (None, None)
        return {
            "ApiVersion": parsed.get("API version"),
            "Version": parsed.get("Version"),
            "GitCommit": parsed.get("Git commit"),
            "GoVersion": parsed.get("Go version"),
            "Built": parsed.get("Built"),
            "Os": os,
            "Arch": arch
        }

    client, server = None, None
    client = get_result(parsed['Client'])
    server = get_result(parsed['Server'])
    return { "Client": client, "Server": server }

def _parse_version_old(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    parsed = dict()
    for line in stdout_lines:
        key, val = line.split(':', 1)
        parsed[key.strip()] = val.strip()
    client, server = None, None

    os_arch = parsed.get("OS/Arch (client)")
    os, arch = os_arch.split('/') if os_arch else (None, None)
    client = {
        "ApiVersion": parsed.get("Client API version"),
        "Version": parsed.get("Client version"),
        "GitCommit": parsed.get("Git commit (client)"),
        "GoVersion": parsed.get("Go version (client)"),
        "Os": os,
        "Arch": arch
    }

    server = {
        "ApiVersion": parsed.get("Server API version"),
        "Version": parsed.get("Server version"),
        "GitCommit": parsed.get("Git commit (server)"),
        "GoVersion": parsed.get("Go version (server)"),
    }

    return { "Client": client, "Server": server}

def parse_wait(stdout_raw):
    try:
        status_code =  int(stdout_raw)
    except ValueError:
        status_code =  None
    return {'StatusCode': status_code}

def parse_network_ls(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    headers = stdout_lines[0]
    content = stdout_lines[1:]
    rows = [line.split() for line in content]
    return [{'Id': row[0],
             'Name': row[1],
             'Driver': row[2]} for row in rows if row]

def parse_volume_ls(stdout_raw):
    stdout_lines = filter(None, stdout_raw.split('\n'))
    headers = stdout_lines[0]
    content = stdout_lines[1:]
    rows = [line.split() for line in content]
    return [{'Driver': row[0],
             'Name': row[1]} for row in rows if row]


#TODO: хелперы а-ля парсеры для работы с stdout в режиме _interact(ex., logs_stream, stats_stream)
