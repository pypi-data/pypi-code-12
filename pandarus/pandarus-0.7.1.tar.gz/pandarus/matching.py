# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *
from future.utils import python_2_unicode_compatible

from .maps import Map, to_shape
from .projection import project, wgs84, MOLLWEIDE
from logging.handlers import QueueHandler, QueueListener
from pyproj import Proj
from shapely.geos import TopologicalError
import datetime
import logging
import math
import multiprocessing
import pyprind
import time


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


def logger_init():
    # Adapted from http://stackoverflow.com/a/34964369/164864
    logging_queue = multiprocessing.Queue()
    # this is the handler for all log records
    filename = "{}-{}.log".format(
        'pandarus-worker', datetime.datetime.now().strftime("%d-%B-%Y-%I-%M%p")
    )
    handler = logging.FileHandler(
        filename,
        encoding='utf-8',
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(lineno)d %(message)s"))

    # queue_listener gets records from the queue and sends them to the handler
    queue_listener = QueueListener(logging_queue, handler)
    queue_listener.start()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return queue_listener, logging_queue


def worker_init(logging_queue):
    # Needed to pass logging messages from child processes to a queue
    # handler which in turn passes them onto queue listener
    queue_handler = QueueHandler(logging_queue)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(queue_handler)


def intersection_worker(from_map, from_objs, to_map, worker_id):
    """Multiprocessing worker for map matching"""
    if not from_objs:
        return

    logging.info("""Starting intersection worker:
    from map: {}
    from objs: {} ({} to {})
    to map: {}
    worker id: {}""".format(from_map, len(from_objs), min(from_objs),
                            max(from_objs), to_map, worker_id))

    results = {}
    to_map = Map(to_map)

    rtree_index = to_map.create_rtree_index()
    from_map = Map(from_map)

    logging.info("Worker {}: Loaded to map. Format: {}".format(
        worker_id, "Vector" if to_map.vector else "Raster")
    )
    logging.info("Worker {}: Loaded from map. Format: {}".format(
        worker_id, "Vector" if from_map.vector else "Raster")
    )

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

            if not geom.is_valid:
                geom = geom.buffer(0)

            if not skip_projection:
                geom = project(geom, from_map.crs, to_map.crs)

            possibles = rtree_index.intersection(geom.bounds)
            for candidate_index in possibles:
                candidate = to_map[candidate_index]
                candidate_geom = to_shape(candidate['geometry'])
                if not candidate_geom.is_valid:
                    candidate_geom = candidate_geom.buffer(0)
                if not geom.intersects(candidate_geom):
                    continue

                intersection = geom.intersection(candidate_geom)
                if not intersection.is_valid:
                    intersection = intersection.buffer(0)
                if not intersection.area:
                    continue
                results[(from_index, candidate_index)] = \
                    project(intersection, to_map.crs, MOLLWEIDE).area

        except TopologicalError:
            logging.exception("Skipping topological error.")
            continue
        except:
            logging.exception("Intersection worker failed.")
            raise

    return results


def areal_worker(from_map, from_objs, worker_id):
    """Multiprocessing worker for areas of each object in a map"""
    if not from_objs:
        return

    logging.info("""Starting areal worker:
    from map: {}
    from objs: {} ({} to {})
    worker id: {}""".format(from_map, len(from_objs), min(from_objs),
                            max(from_objs), worker_id))

    results = {}

    from_map = Map(from_map)

    logging.info("Worker {}: Loaded from map. Format: {}".format(
        worker_id, "Vector" if from_map.vector else "Raster")
    )

    if from_objs:
        from_gen = zip(from_objs, from_map.select(from_objs))
    else:
        from_gen = enumerate(from_map)

    for task_index, (from_index, from_obj) in enumerate(from_gen):
        try:
            geom = to_shape(from_obj['geometry'])
            if not geom.is_valid:
                geom = geom.buffer(0)

            results[from_index] = \
                project(geom, from_map.crs, MOLLWEIDE).area

        except TopologicalError:
            logging.exception("Skipping topological error.")
            continue
        except:
            logging.exception("Areal worker failed.")
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

    queue_listener, logging_queue = logger_init()
    logging.info("""Starting matchmaker calculation.
    From map: {}
    To map: {}
    Map size: {}
    Chunk size: {}
    Number of jobs: {}""".format(from_map, to_map, map_size, chunk_size,
                                 num_jobs))

    bar = BetterBar(map_size)
    results = {}

    def areas_callback_func(data):
        results.update(data)
        bar.update(len(results))

    def intersections_callback_func(data):
        results.update(data)
        bar.update(len({key[0] for key in results}))

    if to_map is None:
        with multiprocessing.Pool(
                    cpus or multiprocessing.cpu_count(),
                    worker_init,
                    [logging_queue]
                ) as pool:
            arguments = [
                (from_map, chunk, index)
                for index, chunk in enumerate(chunker(ids, chunk_size))
            ]

            function_results = []

            for argument_set in arguments:
                function_results.append(pool.apply_async(
                    areal_worker,
                    argument_set,
                    callback=areas_callback_func
                ))
            for fr in function_results:
                fr.wait()

            if any(not fr.successful() for fr in function_results):
                raise ValueError("Couldn't complete Pandarus task")

    else:
        with multiprocessing.Pool(
                    cpus or multiprocessing.cpu_count(),
                    worker_init,
                    [logging_queue]
                ) as pool:
            arguments = [
                (from_map, chunk, to_map, index)
                for index, chunk in enumerate(chunker(ids, chunk_size))
            ]

            function_results = []

            for argument_set in arguments:
                function_results.append(pool.apply_async(
                    intersection_worker,
                    argument_set,
                    callback=intersections_callback_func
                ))
            for fr in function_results:
                fr.wait()

            if any(not fr.successful() for fr in function_results):
                raise ValueError("Couldn't complete Pandarus task")

    queue_listener.stop()
    bar.finish()

    logging.info("""Finished matchmaker calculation.
    From map: {}
    To map: {}
    Map size: {}
    Chunk size: {}
    Number of jobs: {}""".format(from_map, to_map, map_size, chunk_size,
                                 num_jobs))

    return results
