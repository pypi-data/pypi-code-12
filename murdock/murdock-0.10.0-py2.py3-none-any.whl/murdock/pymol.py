# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Module :mod:`murdock.pymol`
---------------------------

This module handles PyMOL scripts. It provides the class :class:`PyMOLPicture`
used in the :mod:`~murdock.report.report` module to include PyMOL pictures of
molecular structures. Also, it provides the class :class:`PyMOLVideo` used to
create PyMOL videos of conformational searches.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import logging
import os
import subprocess
import sys

import murdock.misc

log = logging.getLogger('pymol')


class PyMOLMaster(object):

    def __init__(self, workdir=None):
        self.load_cgos = ''
        self.workdir = workdir

    def init_cgos(self):
        self.load_cgos += 'from cgo import COLOR, SPHERE\n'

    def add_sphere(self, name, coords, radius, color):
        cgo_args = '[COLOR, %s, SPHERE, %s, %.3f]' % (
            ', '.join(['%.3f' % _c for _c in color]),
            ', '.join(['%.3f' % _x for _x in coords]), radius)
        self.load_cgos += 'cmd.load_cgo(%s, "%s")\n' % (cgo_args, name)


class PyMOLPicture(PyMOLMaster):

    def __init__(self, scriptpath, workdir=None):
        self.workdir = workdir
        if self.workdir is None:
            self.workdir = os.path.split(scriptpath)[0]
        super(PyMOLPicture, self).__init__(self.workdir)
        self.scriptpath = scriptpath
        self.script = None
        self.changed = True

    def run_script(
            self, pymolexec, filepath, overwrite=True, num_threads=None):
        filepath = os.path.abspath(filepath)
        if not overwrite and os.path.exists(filepath):
            return True
        logpath = '%s.log' % os.path.splitext(self.scriptpath)[0]
        script = self.script
        if num_threads is not None:
            script = '%sset max_threads, %d\n' % (script, num_threads)
        script = '%spng %s\n' % (script, filepath)
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        cmd = [pymolexec, '-c', '-d', script]
        with open(logpath, 'w') as f:
            try:
                subprocess.call(cmd, stderr=f, stdout=f, cwd=self.workdir)
            except OSError:
                log.error(
                    'PNG picture `%s` could not be created using the PyMOL '
                    'executable `%s`: %s', filepath, pymolexec, sys.exc_value)
                return False
        if not os.path.exists(filepath):
            log.error(
                'PNG picture `%s` could not be created using the PyMOL '
                'executable `%s`. Check the log file `%s` for details.',
                filepath, pymolexec, logpath)
            return False
        return True

    def write_script(
            self, rec_filepath, lig_filepaths, width, height,
            ref_filepaths=None, colors=None, ref_color='green', overwrite=True,
            res_colors=None, include_script=None, residuals_filepath=None,
            draw_res_sticks=False):
        if rec_filepath is None:
            recname = ''
            loadrec = ''
            showrec = ''
            colorrec = ''
        else:
            recname = os.path.splitext(os.path.basename(rec_filepath))[0]
            loadrec = 'load %s\n' % rec_filepath
            showrec = 'show cartoon, %s\nshow surface, %s\n' % (
                recname, recname)
            colorrec = 'color gray, %s\n' % recname
            if res_colors is not None:
                if draw_res_sticks:
                    colorrec += ''.join([
                        '%s%s' % (
                            _colorstr_c(_val, recname, _res),
                            _stickstr(recname, _res)) for _res, _val
                        in res_colors.iteritems()])
                else:
                    colorrec += ''.join([
                        '%s' % _colorstr_c(_val, recname, _res) for _res,
                        _val in res_colors.iteritems()])
        if ref_filepaths is None:
            loadrefs = ''
            showrefs = ''
            colorrefs = ''
        else:
            refnames = [
                os.path.splitext(os.path.basename(_fp))[0] for _fp in
                ref_filepaths]
            loadrefs = ''.join([
                'load %s, reflig%02d\n' % (_fp, _i + 1) for
                _i, _fp in enumerate(ref_filepaths)])
            showrefs = ''.join([
                'show sticks, reflig%02d\nset stick_radius, 0.2, reflig%02d\n'
                % (_i + 1, _i + 1) for _i, _ln in enumerate(refnames)])
            if ref_color is None:
                colorrefs = ''
            else:
                colorrefs = ''.join([
                    'color %s, reflig%02d\n' % (ref_color, _i + 1) for _i, _ln
                    in enumerate(refnames)])
        if not rec_filepath and not lig_filepaths and not ref_filepaths:
            return False
        if residuals_filepath is not None:
            add_residuals = 'load %s\n' % residuals_filepath
            resname = os.path.splitext(os.path.basename(residuals_filepath))[0]
            add_residuals += 'hide everything, %s\n' % resname
            add_residuals += 'show surface, %s\n' % resname
            add_residuals += 'set surface_color, 9, %s\n' % resname
            add_residuals += 'set transparency, 0.4, %s\n' % resname
        else:
            add_residuals = ''
        if lig_filepaths:
            lignames = [
                os.path.splitext(os.path.basename(_fp))[0] for _fp in
                lig_filepaths]
            loadligs = ''.join(['load %s\n' % _fp for _fp in lig_filepaths])
            showligs = ''.join(['show sticks, %s\n' % _ln for _ln in lignames])
        else:
            lignames = []
            loadligs = ''
            showligs = ''
        if colors is None:
            colorligs = ''
        else:
            colorligs = ''.join([
                _colorstr_c(colors[_fp], _ln) for _fp, _ln in
                zip(lig_filepaths, lignames) if colors[_fp] is not None])
        include_script_str = ''
        if include_script is not None:
            try:
                with codecs.open(include_script, 'r', encoding='utf-8') as f:
                    s = f.read()
            except IOError:
                log.error('PyMOL script `%s` can not be read.', include_script)
            else:
                copypath = os.path.abspath(os.path.join(
                    os.path.dirname(self.scriptpath),
                    os.path.basename(include_script)))
                if not os.path.exists(copypath):
                    with codecs.open(copypath, 'w', encoding='utf-8') as f:
                        f.write(s)
                include_script_str = 'run %s' % copypath
        self.script = PIC_SCRIPT.format(
            load_receptor=loadrec, load_references=loadrefs,
            load_ligands=loadligs, show_receptor=showrec,
            color_receptor=colorrec, show_references=showrefs,
            color_references=colorrefs, add_residuals=add_residuals,
            show_ligands=showligs, color_ligands=colorligs, width=width,
            height=height, include_script=include_script_str)
        self.changed = True
        if not overwrite and os.path.exists(self.scriptpath):
            self.changed = False
            return True
        if os.path.exists(self.scriptpath):
            with codecs.open(self.scriptpath, 'r', encoding='utf-8') as f:
                existing = f.read()
            if existing == self.script:
                self.changed = False
                return True
        with codecs.open(self.scriptpath, 'w', encoding='utf-8') as f:
            f.write(self.script)
        return True


PIC_SCRIPT = r"""
viewport {width}, {height}
set depth_cue, 1
set ray_trace_fog, 0
set stick_radius, 0.1
set ray_shadows, 0
set surface_quality, 0
set surface_color, gray
set transparency, 0.7
set antialias, 0
bg_color white
{load_references}
{load_receptor}
orient
{load_ligands}
hide all
{show_receptor}{show_references}{show_ligands}
{color_references}{color_ligands}{color_receptor}
{add_residuals}
hide sticks, hydro
zoom complete=1, buffer=2
{include_script}

"""


class PyMOLVideo(PyMOLMaster):

    def __init__(self, outdir, prefix, workdir=None):
        self.workdir = workdir
        if self.workdir is None:
            self.workdir = outdir
        super(PyMOLVideo, self).__init__(self.workdir)
        self.outdir = outdir
        self.prefix = prefix
        self.staticdir = os.path.join(self.outdir, 'static')
        if not os.path.exists(self.staticdir):
            os.makedirs(self.staticdir)
        self.framedir = os.path.join(self.outdir, 'frames')
        if not os.path.exists(self.framedir):
            os.makedirs(self.framedir)
        self.pngdir = os.path.join(self.outdir, 'png')
        if not os.path.exists(self.pngdir):
            os.makedirs(self.pngdir)
        self.script = None
        self.scriptpath = None
        self.static = collections.OrderedDict()
        self.frames = collections.OrderedDict()

    def add_frame(self, root):
        for child in root.children:
            obj_name = murdock.misc.cleanup_filename(child.name)
            if child.static:
                continue
            f = child.atoms[0].source_atom.source.source
            f.coords_from_molstruct(child.dynamic_atoms())
            ext = os.path.splitext(f.filepath)[1]
            if obj_name not in self.frames:
                self.frames[obj_name] = []
            filepath = os.path.join(self.framedir, '%s-%s-%05d%s' % (
                self.prefix, obj_name, len(self.frames[obj_name]), ext))
            self.frames[obj_name].append(filepath)
            f.write(filepath, overwrite=True)
        return True

    def add_static(self, root):
        for child in root.children:
            obj_name = murdock.misc.cleanup_filename(child.name)
            if not child.static:
                continue
            f = murdock.misc.original_source(child.atoms[0])[0]
            ext = os.path.splitext(f.filepath)[1]
            filepath = os.path.join(self.staticdir, '%s%s' % (obj_name, ext))
            f.write(filepath, overwrite=True)
            self.static[obj_name] = filepath
        return True

    def write_script(self, width=1280, height=720):
        loadstatic = ''.join([
            'load %s, %s\n' % (_fp, _name) for _name, _fp in
            self.static.iteritems()])
        showstatic = ''.join([
            'show cartoon, %s\n' % _name for _name in self.static])
        blocks = []
        for name, fps in self.frames.iteritems():
            blocks.extend([
                'load %s, %s; remove hydrogens\n' % (_fp, name) for _fp in
                fps])
            blocks.append('\n')
        loadframes = ''.join(blocks)
        showframes = ''.join(
            ['show sticks, %s\n' % _name for _name in self.frames])
        try:
            lastframe = max(len(_fps) for _fps in self.frames.itervalues())
        except ValueError:
            lastframe = 1
        camera = 'mset 1 -%d x151\n\n' % lastframe
        camera += (
            'scene 001, store, view=0, color=0, active=0, rep=1, frame=0\n\n')
        i = 1
        while True:
            if i > lastframe:
                i = lastframe
            camera += (
                'frame %d\norient state=%d\nzoom state=%d, complete=1, '
                'buffer=5\nmview store, scene=001\n\n' % (i, i, i))
            if i == lastframe:
                break
            i += 100
        i += 50
        camera += (
            'frame %d\nzoom complete=1, buffer=5\nmview store, '
            'scene=001\n\n' % i)
        i += 1
        camera += 'frame %d\n' % i
        for name in self.static:
            camera += 'as surface, %s\n' % name
        camera += (
            'scene 002, store, view=0, color=0, active=0, rep=1, frame=0\n'
            'mview store, scene=002\n\n')
        i += 50
        camera += (
            'frame %d\nturn x, 180\nzoom state=1, complete=1, buffer=5\nmview '
            'store, scene=002\n\n' % i)
        i += 50
        camera += (
            'frame %d\nturn z, 180\nzoom state=1, complete=1, buffer=5\nmview '
            'store, scene=002\n\n' % i)
        camera += 'mview reinterpolate, power=3, wrap=0\n'
        writevideo = 'mpng %s-frame' % os.path.join(self.pngdir, self.prefix)
        self.script = VIDEO_SCRIPT.format(
            width=width, height=height, loadstatic=loadstatic,
            loadframes=loadframes, load_cgos=self.load_cgos,
            showstatic=showstatic, showframes=showframes,
            writevideo=writevideo, camera=camera)
        self.scriptpath = os.path.join(self.outdir, '%s.pml' % self.prefix)
        with codecs.open(self.scriptpath, 'w', encoding='utf-8') as f:
            f.write(self.script)
        return True

VIDEO_SCRIPT = r"""
set depth_cue, 0
set ray_trace_fog, 0
set stick_radius, 0.2
set ray_trace_frames, 1
set antialias, 0
set surface_quality, 0
set cache_frames, 0
bg_color white
viewport {width}, {height}

{loadstatic}
{loadframes}
hide all
{load_cgos}
{showstatic}
{showframes}
{camera}
{writevideo}

"""


def _colorscale_c(value):
    return int(90 + 70 * value)


def _colorstr_c(value, name, residue_str=None):
    if isinstance(value, basestring):
        s = 'color %s, %s' % (value, name)
    else:
        s = 'color c%03d, %s' % (_colorscale_c(value), name)
    if residue_str is not None:
        s += ' and resi %s' % residue_str
    return s + '\n'


def _stickstr(name, residue_str):
    sel = '%s and resi %s' % (name, residue_str)
    s = 'show sticks, %s\n' % sel
    s += 'set stick_radius, 0.2, %s\n' % sel
    return s
