# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *
from future.utils import python_2_unicode_compatible

from .maps import Map, to_shape
from .projection import project, wgs84, MOLLWEIDE
from pyproj import Proj
import math
import multiprocessing
import pyprind
import time
import traceback


class BetterBar(pyprind.ProgBar):
    def finish(self):
        if self.cnt == self.max_iter:
            return
        else:
            self.cnt = self.max_iter
            self._finish()

    def update(self, index=None):
        if index is None:
            super(pyprind.ProgBar, self).update()
        else:
            self.cnt = index
            self._print()
            self._finish()


def chunker(iterable, chunk_size):
    for i in range(0, len(iterable), chunk_size):
        yield list(iterable[i:i + chunk_size])


def write_log_message(message):
    with open("matchstick.log", "a") as f:
        f.write(message + "\n")


def matchstick(from_map, from_objs, to_map, worker_id, verbose=True):
    """Multiprocessing worker for map matching"""
    if not from_objs:
        return

    if verbose:
        write_log_message("""Starting matchstick:
    from map: %s
    from objs: %s (%s to %s)
    to map: %s
    worker id: %s""" % (from_map, len(from_objs), min(from_objs), max(from_objs), to_map, worker_id))

    results = {}
    to_map = Map(to_map)

    if verbose:
        write_log_message("%s: Loaded to map. Vector? %s" % (worker_id, to_map.vector))

    rtree_index = to_map.create_rtree_index()
    from_map = Map(from_map)

    if verbose:
        write_log_message("%s: Loaded from map. Vector? %s" % (worker_id, from_map.vector))

    skip_projection = (from_map.crs == to_map.crs) or \
        (Proj(wgs84(from_map.crs)).is_latlong() and \
         Proj(wgs84(to_map.crs)).is_latlong())

    if from_objs:
        from_gen = zip(from_objs, from_map.select(from_objs))
    else:
        from_gen = enumerate(from_map)

    for task_index, (from_index, from_obj) in enumerate(from_gen):
        try:
            geom = to_shape(from_obj['geometry'])

            if not skip_projection:
                geom = project(geom, from_map.crs, to_map.crs)

            possibles = rtree_index.intersection(geom.bounds)
            for candidate_index in possibles:
                candidate = to_map[candidate_index]
                candidate_geom = to_shape(candidate['geometry'])
                if not geom.intersects(candidate_geom):
                    continue

                intersection = geom.intersection(candidate_geom)
                if not intersection.area:
                    continue

                results[(from_index, candidate_index)] = \
                    project(intersection, to_map.crs, MOLLWEIDE).area

        except:
            if verbose:
                write_log_message(traceback.format_exc())
            raise

    return results


def areal_calculation(from_map, from_objs, worker_id, verbose=True):
    """Multiprocessing worker for areas of each object in a map"""
    if not from_objs:
        return

    if verbose:
        write_log_message("""Starting areal calculation:
    from map: %s
    from objs: %s (%s to %s)
    worker id: %s""" % (from_map, len(from_objs), min(from_objs), max(from_objs), worker_id))

    results = {}

    from_map = Map(from_map)

    if verbose:
        write_log_message("%s: Loaded from map. Vector? %s" % (worker_id, from_map.vector))

    if from_objs:
        from_gen = zip(from_objs, from_map.select(from_objs))
    else:
        from_gen = enumerate(from_map)

    for task_index, (from_index, from_obj) in enumerate(from_gen):
        try:
            geom = to_shape(from_obj['geometry'])

            results[from_index] = \
                project(geom, from_map.crs, MOLLWEIDE).area

        except:
            if verbose:
                write_log_message(traceback.format_exc())
            raise

    return results


def matchmaker(from_map, to_map, from_objs=None, cpus=None):
    if from_objs:
        map_size = len(from_objs)
        ids = from_objs
    else:
        map_size = len(Map(from_map))
        ids = range(map_size)

    # Want a reasonable chunk size
    # But also want a maximum of 200 jobs
    # Both numbers picked more or less at random...
    chunk_size = int(max(20, map_size / 200))
    num_jobs = int(math.ceil(map_size / float(chunk_size)))

    bar = BetterBar(map_size)
    results = {}

    def areas_callback_func(data):
        results.update(data)
        bar.update(len(results))

    def intersections_callback_func(data):
        results.update(data)
        bar.update(len({key[0] for key in results}))

    if to_map is None:
        with multiprocessing.Pool(cpus or multiprocessing.cpu_count()) as pool:
            arguments = [
                (from_map, chunk, index)
                for index, chunk in enumerate(chunker(ids, chunk_size))
            ]

            function_results = []

            for argument_set in arguments:
                function_results.append(pool.apply_async(
                    areal_calculation,
                    argument_set,
                    callback=areas_callback_func
                ))
            for fr in function_results:
                fr.wait()

            if any(not fr.successful() for fr in function_results):
                raise ValueError("Couldn't complete Pandarus task")

    else:
        with multiprocessing.Pool(cpus or multiprocessing.cpu_count()) as pool:
            arguments = [
                (from_map, chunk, to_map, index)
                for index, chunk in enumerate(chunker(ids, chunk_size))
            ]

            function_results = []

            for argument_set in arguments:
                function_results.append(pool.apply_async(
                    matchstick,
                    argument_set,
                    callback=intersections_callback_func
                ))
            for fr in function_results:
                fr.wait()

            if any(not fr.successful() for fr in function_results):
                raise ValueError("Couldn't complete Pandarus task")

    bar.finish()

    return results
