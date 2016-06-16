# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2008-2014
from __future__ import division, with_statement, print_function

from glob import glob
from time import time
import Image
import math
import os

import ox

from .ffmpeg import Video


FPS = 25

class Timelines():

    def __init__(
        self, video_files, tile_path, cuts_path,
        points, modes, sizes, render_wide_tiles, log
    ):

        self.video_files = video_files
        self.video_i = 0
        self.video_n = len(self.video_files)

        self.tile_path = tile_path
        self.cuts_path = cuts_path
        self.detect_cuts = cuts_path != None

        self.points = points

        # modes can contain 'antialias', 'slitscan', 'keyframes', 'audio', 'cuts' and 'data'
        self.modes = modes
        self.render_antialias = 'antialias' in modes
        self.render_slitscan = 'slitscan' in modes
        self.render_keyframes = 'keyframes' in modes
        self.render_audio = 'audio' in modes
        self.render_cuts = 'cuts' in modes
        self.render_data = 'data' in modes
        self.render_video = len(modes) > 1 if self.render_audio else True

        if self.detect_cuts or self.render_cuts or self.render_keyframes:
            self.detect_cuts = True
            self.cuts = [0]
            self.no_cuts = []
            self.short_cut = None
            self.cut_frames = []
            self.max_cut_len = 15000 # 10 minutes
            self.max_distance = 64 * math.sqrt(3 * pow(255, 2))
        else:
            self.cuts = []

        self.full_tile_w = 1920
        self.large_tile_w = 1500
        self.large_tile_h = sizes[0]
        self.large_tile_image = {}
        self.render_small_tiles = False
        if len(sizes) == 2:
            self.small_tile_w = 3600
            self.small_tile_h = sizes[1]
            self.small_tile_image = {}
            self.render_small_tiles = True

        self.render_wide_tiles = render_wide_tiles

        if self.render_audio:
            self.volume = []

        self.log = log
        if log:
            self.profiler = Profiler()
            self.profiler.set_task('ffmpeg')

        ox.makedirs(self.tile_path)

    def render(self):

        if self.points:
            self.in_frame = int(self.points[0] * FPS)
            self.out_frame = int(self.points[1] * FPS)
            self.duration = self.points[1] - self.points[0]

        self.videos = []
        self.file_durations = []
        self.file_frame_n = []
        self.file_points = []
        offset = 0
        for video_file in self.video_files:
            video = Video(
                video_file, self.large_tile_h if self.render_video else 0,
                self.render_audio, self._video_callback, self._done_callback
            )
            duration = video.get_duration()
            points = None
            if self.points:
                in_point = None
                out_point = None
                if self.points[0] > offset and self.points[0] < offset + duration:
                    in_point = self.points[0] - offset
                if self.points[1] > offset and self.points[1] < offset + duration:
                    out_point = self.points[1] - offset
                if in_point or out_point:
                    points = [in_point or 0, out_point or duration]
            self.videos.append(video)
            self.file_durations.append(duration)
            self.file_frame_n.append(int(duration * FPS))
            self.file_points.append(points)
            offset += duration
            #input did not have any video, dont try to render video timelines
            if self.render_video and not video.video:
                self.modes = ['audio']
                self.render_antialias = \
                self.render_slitscan = \
                self.render_keyframes = \
                self.render_video = False

        if not self.points:
            self.in_frame = 0
            self.out_frame = sum(self.file_frame_n)
            self.duration = sum(self.file_durations)

        self.frame_n = self.out_frame - self.in_frame

        if self.render_video:
            frame_size = self.videos[0].get_size()
            self.frame_w = frame_size[0]
            self.frame_ratio = frame_size[0] / frame_size[1]
            self.frame_center = int(frame_size[0] / 2)

        self.large_tile_n = int(math.ceil(self.frame_n / self.large_tile_w))
        self.large_tile_last_w = self.frame_n % self.large_tile_w or self.large_tile_w
        if self.render_small_tiles:
            self.small_tile_n = int(math.ceil(self.duration / self.small_tile_w))
            self.small_tile_last_w =int(math.ceil(self.duration % self.small_tile_w)) or self.small_tile_w

        if self.render_antialias or self.render_audio:
            self._open_full_tile()
        if self.render_keyframes:
            self.large_keyframes_tile_i = -1
            if self.render_small_tiles:
                self.wide = FPS * self.small_tile_h / self.large_tile_h
                self.wide_frame_w = int(round(self.frame_w * self.wide))

        self.frame_i = 0
        self.frame_offset = 0
        self.log and self.profiler.set_task('ffmpeg')
        self.videos[0].decode(self.file_points[0])

        # remove tiles from previous run
        if not self.points:
            #for mode in filter(lambda m: m!= 'audio', self.modes):
            for mode in self.modes:
                type = 'png' if mode == 'data' else 'jpg'
                tiles = glob('%s/timeline%s%dp*.%s' % (self.tile_path, mode, self.large_tile_h, type))
                for f in ox.sorted_strings(tiles)[self.large_tile_i+2:]:
                    os.unlink(f)
                if self.render_small_tiles:
                    tiles = glob('%s/timeline%s%dp*.%s' % (self.tile_path, mode, self.small_tile_h, type))
                    for f in ox.sorted_strings(tiles)[self.small_tile_i+2:]:
                        os.unlink(f)

    def _video_callback(self, frame_image, timestamp):

        self.log and self.profiler.set_task('_video_callback()')
        '''
        if timestamp != None and self.frame_i != int(round(timestamp * FPS)):
            print('WARNING: i is', self.frame_i, 'timestamp is', timestamp, '(', int(round(timestamp * FPS)), ')')
        '''
        self.is_last_frame = self.frame_i == self.frame_n - 1
        large_tile_x = self.frame_i % self.large_tile_w

        # open large tile
        if large_tile_x == 0:
            self.large_tile_i = int(self.frame_i / self.large_tile_w)
            if self.large_tile_i < self.large_tile_n - 1:
                w = self.large_tile_w
            else:
                w = self.large_tile_last_w
            for mode in filter(lambda x: x in ['antialias', 'slitscan', 'cuts'], self.modes):
                self.large_tile_image[mode] = Image.new('RGB', (w, self.large_tile_h))
            if self.render_data:
                self.large_tile_image['data'] = Image.new('RGB', (w * 8, 8))
        paste = (large_tile_x, 0)

        # render antialias tile
        self.log and self.profiler.set_task('i.resize((1, h), Image.ANTIALIAS) # antialias timelines')
        if self.render_antialias or self.render_cuts:
            resize = (1, self.large_tile_h)
            antialias_image = frame_image.resize(resize, Image.ANTIALIAS)
        if self.render_antialias:
            self.large_tile_image['antialias'].paste(antialias_image, paste)

        # render slitscan tile
        self.log and self.profiler.set_task('i.crop((c, 0, c + 1, h)) # slitscan timelines')
        if self.render_slitscan:
            crop = (self.frame_center, 0, self.frame_center + 1, self.large_tile_h)
            self.large_tile_image['slitscan'].paste(frame_image.crop(crop), paste)
        self.log and self.profiler.unset_task()

        # render data tile
        if self.render_data or self.detect_cuts:
            self.log and self.profiler.set_task('i.resize((8, 8), Image.ANTIALIAS) # cut detection')
            data_image = frame_image.resize((8, 8), Image.ANTIALIAS)
            if self.render_data:
                self.large_tile_image['data'].paste(data_image, (large_tile_x * 8, 0))
            self.log and self.profiler.unset_task()

        # detect cuts
        if self.detect_cuts:
            self.log and self.profiler.set_task('# cut detection')
            frame_data = data_image.getdata()
            if self.frame_i == 0:
                is_cut = False
                self.previous_distance = 0
            else:
                if self.short_cut and self.frame_i - self.short_cut > 2:
                    self.cuts.append(self.short_cut)
                    self.short_cut = None
                distance = self._get_distance(self.previous_frame_data, frame_data)
                is_cut = distance > 0.08 or (distance > 0.04 and abs(distance - self.previous_distance) > 0.04)
                if is_cut:
                    if self.frame_i - (0 if not self.cuts else self.short_cut or self.cuts[-1]) < 3:
                        is_cut = False
                        self.short_cut = self.frame_i
                    else:
                        self.cuts.append(self.frame_i)
                elif len(self.cut_frames) == self.max_cut_len:
                    is_cut = True
                    self.cuts.append(self.frame_i)
                    self.no_cuts.append(self.frame_i)
                # render cuts tile
                if self.render_cuts:
                    self.log and self.profiler.set_task('# cuts timeline')
                    self.large_tile_image['cuts'].paste(antialias_image, paste)
                    y = self.large_tile_h - 1 - int(distance * self.large_tile_h)
                    rgb = (255, 0, 0) if is_cut else (0, 255, 0)
                    try:
                        self.large_tile_image['cuts'].putpixel((large_tile_x, y), rgb)
                    except:
                        print('ERROR x y rgb', large_tile_x, y, rgb)
                self.previous_distance = distance
            self.previous_frame_data = frame_data
            # render keyframes tile
            if self.render_keyframes:
                if is_cut:
                    self._render_keyframes()
                self.cut_frames.append(frame_image)
                if self.is_last_frame:
                    if not self.cuts or self.cuts[-1] != self.frame_n:
                        self.cuts.append(self.frame_n)
                    self._render_keyframes()

        # save large tile
        self.log and self.profiler.set_task('_video_callback()')
        if large_tile_x == self.large_tile_w - 1 or self.is_last_frame:
            for mode in filter(lambda x: x in ['antialias', 'slitscan', 'cuts', 'data'], self.modes):
                self._save_tile(mode, self.large_tile_i)
            if self.render_antialias:
                self._save_full_tile_image('antialias')
        self.frame_i += 1
        self.log and self.profiler.set_task('ffmpeg')

    def _render_keyframes(self):
        self.log and self.profiler.set_task('_render_keyframes() # keyframes timelines')
        cut_width = self.cuts[-1] - self.cuts[-2]
        modes = ['keyframes', 'keyframeswide'] if self.render_small_tiles else ['keyframes']
        for mode in modes:
            wide = 1 if mode == 'keyframes' else self.wide
            frame_ratio = self.frame_ratio * wide
            cut_images = int(math.ceil(cut_width / (frame_ratio * self.large_tile_h)))
            if cut_images == 0:
                print('ERROR division by zero', cut_width, cut_images)
                index = -1
            image_widths = self._divide(cut_width, cut_images)
            image_i = self.cuts[-2]
            large_keyframes_tile_i = self.large_keyframes_tile_i
            for image_w in image_widths:
                frame_image = self.cut_frames[image_i - self.cuts[-2]]
                #frame_image.save('deleteme.jpg')
                if mode == 'keyframeswide':
                    resize = (self.wide_frame_w, self.large_tile_h)
                    self.log and self.profiler.set_task('i,resize((w, h)) # keyframeswide timelines')
                    frame_image = frame_image.resize(resize, Image.ANTIALIAS)
                    self.log and self.profiler.unset_task()
                left = int((self.frame_w * wide - image_w) / 2)
                crop = (left, 0, left + image_w, self.large_tile_h)
                frame_image = frame_image.crop(crop)
                tile_indices = [int(image_i / self.large_tile_w)]
                tile_offsets = [image_i % self.large_tile_w]
                while tile_offsets[-1] + image_w > self.large_tile_w:
                    tile_indices.append(tile_indices[-1] + 1)
                    tile_offsets.append(tile_offsets[-1] - self.large_tile_w)
                for i, index in enumerate(tile_indices):
                    offset = tile_offsets[i]
                    if index > large_keyframes_tile_i:
                        large_keyframes_tile_i = index
                        if index > 0:
                            self._save_tile(mode, index - 1)
                        if index < self.large_tile_n - 1:
                            w = self.large_tile_w
                        else:
                            w = self.large_tile_last_w
                        self.large_tile_image[mode] = Image.new('RGB', (w, self.large_tile_h))
                    self.large_tile_image[mode].paste(frame_image, (offset, 0))
                image_i += image_w
            if self.is_last_frame and index > -1:
                self._save_tile(mode, index)

        self.large_keyframes_tile_i = large_keyframes_tile_i
        self.cut_frames = []
        self.log and self.profiler.unset_task()

    def _render_audio(self, volume):
        self.log and self.profiler.set_task('_render_audio()')
        channel_h = int(self.large_tile_h / 2)
        for self.frame_i, sample_v in enumerate(volume):
            sample_v = map(math.sqrt, sample_v)
            large_tile_x = self.frame_i % self.large_tile_w
            if large_tile_x == 0:
                large_tile_i = int(self.frame_i / self.large_tile_w)
                if large_tile_i < self.large_tile_n - 1:
                    w = self.large_tile_w
                else:
                    w = self.large_tile_last_w
                self.large_tile_image['audio'] = Image.new('L', (w, self.large_tile_h))
                image_data = self.large_tile_image['audio'].load()
            for channel, value in enumerate(sample_v):
                value = value * channel_h
                for pixel in range(channel_h):
                    if value <= pixel:
                        break
                    if value < pixel + 1:
                        color = int(round((value - int(value)) * 255))
                    else:
                        color = 255
                    y = channel_h - 1 - pixel if channel == 0 else channel_h + pixel
                    image_data[large_tile_x, y] = (color)
            is_last_tile = self.frame_i == self.frame_n - 1
            if large_tile_x == self.large_tile_w - 1 or is_last_tile:
                self._save_tile('audio', large_tile_i)
                if not self.render_video:
                    self._save_full_tile_image('audio')
        if not self.render_video:
            self.large_tile_i = large_tile_i

    def _divide(self, num, by):
        # divide(100, 3) -> [33, 33, 34]
        arr = []
        if by == 0:
            return arr
        div = int(num / by)
        mod = num % by
        for i in range(int(by)):
            arr.append(div + (i > by - 1 - mod))
        return arr

    def _get_distance(self, data0, data1):
        self.log and self.profiler.set_task('_get_distance() # cut detection')
        distance = 0
        for i in range(64):
            distance += math.sqrt(
                pow(data0[i][0] - data1[i][0], 2) +
                pow(data0[i][1] - data1[i][1], 2) +
                pow(data0[i][2] - data1[i][2], 2)
            )
        distance /= self.max_distance
        self.log and self.profiler.unset_task()
        return distance

    def _open_full_tile(self):
        if self.large_tile_n == 1:
            self.full_tile_widths = [self.full_tile_w]
        else:
            full_tile_w = self.full_tile_w
            full_tile_n = self.large_tile_n
            if self.large_tile_last_w < self.large_tile_w:
                factor = self.full_tile_w / self.frame_n
                last_w = int(round(self.large_tile_last_w * factor))
                full_tile_w -= last_w
                full_tile_n -= 1
            self.full_tile_widths = self._divide(full_tile_w, full_tile_n)
            if self.large_tile_last_w < self.large_tile_w:
                self.full_tile_widths.append(last_w)
        self.full_tile_offset = 0
        self.full_tile_image = Image.new('RGB', (self.full_tile_w, self.large_tile_h))

    def _save_full_tile_image(self, mode):
        resized = self.large_tile_image[mode].resize((
            self.full_tile_widths[0], self.large_tile_h
        ), Image.ANTIALIAS)
        self.full_tile_image.paste(resized, (self.full_tile_offset, 0))
        self.full_tile_offset += self.full_tile_widths[0]
        self.full_tile_widths = self.full_tile_widths[1:]

    def _save_full_tile(self, mode):
        self.log and self.profiler.set_task('_save_full_tile()')
        tile_file = '%stimeline%s%dp.jpg' % (
            self.tile_path, mode, self.large_tile_h
        )
        self.full_tile_image.save(tile_file)
        if self.log:
            print(tile_file)
        if self.render_small_tiles:
            resize = (self.full_tile_w, self.small_tile_h)
            self.full_tile_image = self.full_tile_image.resize(resize, Image.ANTIALIAS)
            tile_file = '%stimeline%s%dp.jpg' % (
                self.tile_path, mode, self.small_tile_h
            )
            self.full_tile_image.save(tile_file)
            if self.log:
                print(tile_file)
        self.log and self.profiler.unset_task()

    def _save_tile(self, mode, index):
        self.log and self.profiler.set_task('_save_tile()')
        # save large tile (or data tile)
        if mode != 'keyframeswide' or self.render_wide_tiles:
            height = 8 if mode == 'data' else self.large_tile_h
            type = 'png' if mode == 'data' else 'jpg'
            tile_file = '%stimeline%s%dp%d.%s' % (
                self.tile_path, mode, height, index, type
            )
            self.large_tile_image[mode].save(tile_file)
            if self.log:
                print(tile_file)
        if self.render_small_tiles and mode in ['antialias', 'slitscan', 'keyframeswide', 'audio']:
            small_mode = 'keyframes' if mode == 'keyframeswide' else mode
            small_tile_x = (index % 60) * 60
            # open small tile
            if small_tile_x == 0:
                image_mode = 'L' if mode == 'audio' else 'RGB'
                self.small_tile_i = small_tile_i = int(index / 60)
                if small_tile_i < self.small_tile_n - 1:
                    w = self.small_tile_w
                else:
                    w = self.small_tile_last_w
                self.small_tile_image[small_mode] = Image.new(image_mode, (w, self.small_tile_h))
            # render small tile
            if small_tile_x <= self.small_tile_image[small_mode].size[0] - 60:
                w = 60
            else:
                w = self.small_tile_last_w % 60 or 60
            resize = (w, self.small_tile_h)
            resized = self.large_tile_image[mode].resize(resize, Image.ANTIALIAS)
            paste = (small_tile_x, 0)
            self.small_tile_image[small_mode].paste(resized, paste)
            # save small tile
            if small_tile_x == self.small_tile_w - 60 or self.frame_i == self.frame_n - 1:
                small_tile_i = int(index / 60)
                tile_file = '%stimeline%s%dp%d.jpg' % (
                    self.tile_path, small_mode, self.small_tile_h, small_tile_i
                )
                self.small_tile_image[small_mode].save(tile_file)
                if self.log:
                    print(tile_file)
        self.log and self.profiler.unset_task()

    def _done_callback(self, volume):
        if self.render_audio:
            volume = volume[:self.file_frame_n[self.video_i]]
            if self.log and len(volume) < self.file_frame_n[self.video_i] - 1:
                print('WARNING: Only got', len(volume), 'of', self.file_frame_n[self.video_i], 'audio samples.')
            while len(volume) < self.file_frame_n[self.video_i]:
                volume.append((0, 0))
            self.volume += volume
        if self.render_video:
            if self.log and self.frame_i - self.frame_offset < self.file_frame_n[self.video_i]:
                print('WARNING: Only got', self.frame_i + 1 - self.frame_offset, 'of', self.file_frame_n[self.video_i], 'video samples.')
            while self.frame_i - self.frame_offset < self.file_frame_n[self.video_i]:
                self._video_callback(
                    Image.new('RGB', (self.frame_w, self.large_tile_h)), None
                )
        if self.video_i < self.video_n - 1:
            self.video_i += 1
            self.frame_offset = self.frame_i
            self.log and self.profiler.set_task('ffmpeg')
            self.videos[self.video_i].decode(self.file_points[self.video_i])
        else:
            if self.render_video:
                if self.render_antialias:
                    self._save_full_tile('antialias')
                if self.cuts_path:
                    # remove cuts at first and last frame and all cuts at max_cut_len
                    self.cuts = filter(lambda x: x not in [0, self.frame_n] + self.no_cuts, self.cuts)
                    with open(self.cuts_path, 'w') as f:
                        # avoid float rounding artefacts
                        f.write('[' + ', '.join(map(lambda x: '%.2f' % (x / FPS), self.cuts)) + ']')
            if self.render_audio:
                self._render_audio(self.volume)
                if not self.render_video:
                    self._save_full_tile('audio')
            if self.log:
                if self.render_video:
                    maximum = 0
                    for i in range(1, len(self.cuts)):
                        length = self.cuts[i] - self.cuts[i - 1]
                        if length > maximum:
                            maximum = length
                    print('Number of frames:', self.frame_n)
                    print('Number of cuts:', len(self.cuts) - 2)
                    print('Most frames per cut:', maximum)
                for task in self.profiler.get_profile():
                    print('%10.6f sec/hr' % (task['time'] / self.frame_n * 90000), task['task'])
                files = filter(lambda x: x.endswith('.jpg'), os.listdir(self.tile_path))
                size = sum(map(lambda x: os.path.getsize(self.tile_path + x), files))
                print('%10.6f MB/hr' % (size / self.frame_n * 90000 / 1000000), 'timeline tiles')


class Profiler():

    def __init__(self):
        self.task = ''
        self.times = {}

    def get_profile(self):
        tasks = []
        total = 0
        for task in self.times:
            tasks.append({'task': task, 'time': self.times[task]})
            total += self.times[task]
        tasks.append({'task': 'total', 'time': total})
        return sorted(tasks, key=lambda x: -x['time'])

    def set_task(self, task):
        now = time()
        if self.task:
            if not self.task in self.times:
                self.times[self.task] = 0
            else:
                self.times[self.task] += now - self.time
            self.previous_task = self.task
        self.task = task
        self.time = now

    def unset_task(self):
       self.set_task(self.previous_task)
