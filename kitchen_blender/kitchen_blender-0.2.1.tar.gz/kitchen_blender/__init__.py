import subprocess
import argparse
import pika
import logging
import json
from kitchen_blender import files
from kitchen_blender import blender

args = {}
connection = None


def main():
    global args, connection
    parser = argparse.ArgumentParser(description="Blender render node")
    parser.add_argument('controller', help='hostname for the controller node')
    parser.add_argument('name', help='name for this render node')
    parser.add_argument('--username', '-u', default='guest')
    parser.add_argument('--password', '-p', default='guest')
    parser.add_argument('--vhost', '-v', default='')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    logging.info('Connecting to message queue')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.controller, virtual_host=args.vhost,
                                                                   credentials=pika.PlainCredentials(args.username,
                                                                                                     args.password)))
    channel = connection.channel()
    logging.info('Declaring task queue')
    channel.queue_declare(queue='tasks', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(process_task, queue='tasks')
    logging.info('Waiting for tasks')
    channel.start_consuming()


def render_progress(percentage):
    global connection

    # Process packets from the RabbitMQ server so the connection doesn't timeout
    connection.process_data_events()


def process_task(ch, method, properties, body):
    global args
    logging.info('Task received')
    task = json.loads(body.decode('utf-8'))

    logging.info('Making sure we have the blend file')
    blend_file = files.get_blend_file(args.controller, task['file_id'])

    files.notify_start(args.controller, task, args.name)

    logging.info('Generating a render script for the tile')
    render_script = generate_render_script(task)

    logging.info('Starting render')
    blender.render(blend_file, render_script, render_progress)

    logging.info('Uploading result')
    files.upload_result(args.controller, task)

    logging.info('Task completed. sending ACK')
    ch.basic_ack(delivery_tag=method.delivery_tag)


def generate_render_script(task):
    """
    :type task: dict
    :return:
    """
    tile_width = task['tile_width']
    tile_height = task['tile_height']
    tile_x = task['tile_x']
    tile_y = task['tile_y']

    left = tile_width * tile_x
    top = tile_height * tile_y
    right = left + tile_width
    bottom = top + tile_height

    script = [
        'import bpy',
        'scene=bpy.context.scene',
        'scene.render.filepath="{}"'.format(files.get_render_output_name(task)),
        'scene.cycles.seed={}'.format(task['seed']),
        'scene.cycles.tile_order="BOTTOM_TO_TOP"',
        'scene.render.use_border=True',
        'scene.render.border_min_x={}/{}'.format(left, task['size_x']),
        'scene.render.border_min_y={}/{}'.format(top, task['size_y']),
        'scene.render.border_max_x={}/{}'.format(right, task['size_x']),
        'scene.render.border_max_y={}/{}'.format(bottom, task['size_y']),
        'scene.render.use_crop_to_border=True',
        'scene.render.resolution_x={}'.format(task['size_x']),
        'scene.render.resolution_y={}'.format(task['size_y']),
        'scene.render.resolution_percentage=100'
    ]

    if task['ext'] == 'png':
        script.append('scene.render.image_settings.file_format="PNG"')
        script.append('scene.render.image_settings.color_mode="{}"'.format(task.get('color_mode', 'RGBA')))
        script.append('scene.render.image_settings.compression=100')
    elif task['ext'] == 'exr':
        script.append('scene.render.image_settings.file_format="OPEN_EXR"')
        script.append('scene.render.image_settings.exr_codec="ZIP"')
        script.append('scene.render.image_settings.use_zbuffer=True')
        script.append('scene.render.image_settings.color_depth=32')

    script.append('scene.frame_set({})'.format(task['frame']))
    script.append('scene.render.use_compositing=False')
    script.append('scene.render.use_sequencer=False')
    script.append('bpy.ops.render.render(write_still=True)')

    script = '\n'.join(script)
    return files.store_render_script(task, script)


def render(blend_file, render_script):
    subprocess.call(['blender', '-b', blend_file, '--python', render_script])


if __name__ == '__main__':
    main()
