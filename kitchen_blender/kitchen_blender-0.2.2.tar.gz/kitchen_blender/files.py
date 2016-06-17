import os
import requests

workdir = '/var/tmp/blender'

if not os.path.isdir(workdir):
    os.makedirs(workdir)


def get_blend_file(host, task):
    local = os.path.join(workdir, 'blend-' + task + '.blend')
    if not os.path.isfile(local):
        with open(local, 'wb') as local_file:
            response = requests.get('http://{}/static/blend/{}.blend'.format(host, task))
            local_file.write(response.content)
    return local


def store_render_script(task, script):
    name = os.path.join(workdir, 'script-{file_id}.py'.format(**task))
    with open(name, 'w') as script_file:
        script_file.write(script)
    return name


def get_render_output_name(task):
    return os.path.join(workdir, 'tile-{file_id}-{tile_x}-{tile_y}.{ext}'.format(**task))

def notify_start(host, task, name):
    payload = {
        'task': task['file_id'],
        'x': task['tile_x'],
        'y': task['tile_y'],
        'node': name
    }

    requests.post('http://{}/api/tile/start'.format(host), data=payload)

def upload_result(host, task):
    local = get_render_output_name(task)
    files = {
        'tile': open(local, 'rb')
    }
    payload = {
        'task': task['file_id'],
        'x': task['tile_x'],
        'y': task['tile_y'],
        'ext': task['ext']
    }
    requests.post('http://{}/api/tile/done'.format(host), files=files, data=payload)
