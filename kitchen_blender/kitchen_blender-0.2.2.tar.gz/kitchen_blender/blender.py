import subprocess


def render(blend_file, render_script, callback):
    process = subprocess.Popen(['blender', '-b', blend_file, '--python', render_script, '-noaudio'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in iter(process.stdout.readline, ''):
        if 'Remaining:' in line:
            frame, time, remaining, memory, scene, status = line.split(' | ')
            words = status.split(' ')
            progress, total = words[3].split('/')
            if ',' in total:
                sample_progress, sample_total = words[5].strip().split('/')
                total = int(total[:-1])
                progress = int(progress)
                sample_progress = int(sample_progress)
                sample_total = int(sample_total)

                scene_samples = total * sample_total
                sample_tile_done = progress * sample_total + sample_progress
                percent = sample_tile_done / scene_samples * 100.0
            else:
                percent = int(progress) / int(total) * 100.0
            callback(percent)


if __name__ == "__main__":
    script = ['import bpy', 'scene=bpy.context.scene', 'scene.render.filepath="//tmp"', 'scene.cycles.seed=0',
              'scene.cycles.tile_order="BOTTOM_TO_TOP"', 'scene.render.resolution_x=1024',
              'scene.render.resolution_y=1024', 'scene.render.resolution_percentage=100',
              'scene.render.image_settings.file_format="PNG"', 'scene.render.image_settings.color_mode="RGBA"',
              'scene.render.image_settings.compression=100', 'bpy.ops.render.render(write_still=True)']

    script = '\n'.join(script)

    with open('/tmp/script.py', 'w') as script_handle:
        script_handle.write(script)


    def progress(percentage):
        print("Progress: {}%".format(percentage))


    render('/workspace/test.blend', '/tmp/script.py', progress)
