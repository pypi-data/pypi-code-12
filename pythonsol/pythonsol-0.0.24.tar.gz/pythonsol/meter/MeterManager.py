"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2014/2015 Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""
import glob
import logging
from threading import Lock

import os
from gevent import GreenletExit
import gevent

from pythonsol.SolBase import SolBase


logger = logging.getLogger("MeterManager")
lifecyclelogger = logging.getLogger("lifecycle")


class MeterManager(object):
    """
    Static meter manager.
    """

    # Global lock
    _static_lock = Lock()

    # Running flag
    _is_running = False

    # Hash of meters
    _hash_meter = dict()

    # Write directory
    _write_dir = "/tmp/"

    # Write interval in millis
    _write_interval_ms = 60000

    # Write greenlet
    _write_greenlet = None

    # Purge on start
    _purge_on_start = True

    # Purge on stop
    _purge_on_stop = True

    # =============================================
    # START & STOP
    # =============================================

    @classmethod
    def start(cls, write_dir, write_interval_ms, purge_on_start, purge_on_stop):
        """
        Start the manager
        :param write_dir: Write directory
        :type write_dir: str
        :param write_interval_ms: Write interval in millis
        :type write_interval_ms: int
        :param purge_on_start: Purge files on start (based on SolBase._compoName)
        :type purge_on_start: bool
        :param purge_on_stop: Purge files on stop (based on SolBase._compoName)
        :type purge_on_stop: bool
        :return Nothing
        """

        with cls._static_lock:
            try:
                lifecyclelogger.info("Start : starting")

                # Check
                if cls._is_running:
                    logger.warn("Already running, doing nothing")
                elif not os.path.isdir(write_dir):
                    raise Exception("Invalid write_dir={0}".format(write_dir))

                # Store
                cls._write_dir = write_dir
                cls._write_interval_ms = write_interval_ms
                cls._purge_on_start = purge_on_start
                cls._purge_on_stop = purge_on_stop

                # Start logs
                lifecyclelogger.info("Start : _write_dir=%s", cls._write_dir)
                lifecyclelogger.info("Start : _write_interval_ms=%s", cls._write_interval_ms)
                lifecyclelogger.info("Start : _purge_on_start=%s", cls._purge_on_start)
                lifecyclelogger.info("Start : _purge_on_stop=%s", cls._purge_on_stop)

                # Purge
                if cls._purge_on_start:
                    cls._purge_files()

                # Schedule next write now
                cls._write_greenlet = gevent.spawn_later(cls._write_interval_ms / 1000.0, cls._write_meters)

                # Signal
                cls._is_running = True
                lifecyclelogger.info("Start : started")
            except Exception as e:
                logger.error("e=%s", SolBase.extostr(e))

    @classmethod
    def stop(cls):
        """
        Stop the manager
        :return  Nothing
        """

        # Signal out of lock (may help greenlet to exit itself)
        cls._is_running = False

        with cls._static_lock:
            try:
                lifecyclelogger.info("Stop : stopping")
                # Kill the greenlet
                if cls._write_greenlet:
                    gevent.kill(cls._write_greenlet)
                    cls._write_greenlet = None

                lifecyclelogger.info("Stop : stopped")
            except Exception as e:
                logger.error("e=%s", SolBase.extostr(e))

    # =============================================
    # PURGE
    # =============================================

    @classmethod
    def _purge_files(cls):
        """
        Purge files
        :return Nothing
        """

        mask = "{0}{1}Meters.{2}.*.txt".format(cls._write_dir, os.sep, SolBase.get_compo_name())

        logger.info("Purging files : mask=%s", mask)
        for fn in glob.glob(mask):
            logger.info("Purging files, fn=%s", fn)
            try:
                os.remove(fn)
            except Exception as e:
                logger.warn("Purging files, fn=%s, e=%s", fn, SolBase.extostr(e))

    # =============================================
    # WRITE
    # =============================================

    @classmethod
    def _write_meters(cls):
        """
        Write meters
        :return Nothing
        """

        with cls._static_lock:
            try:
                # Check
                if not cls._is_running:
                    return

                # File to write to
                fname = "{0}{1}Meters.{2}.{3}.{4}.txt".format(cls._write_dir, os.sep, SolBase.get_compo_name(),
                                                              os.getppid(), os.getpid())

                # Buffer to write
                buf = "D={0}\n".format(SolBase.datecurrent())

                # Browse counters
                for k, meter in cls._hash_meter.iteritems():
                    # Go
                    try:
                        # Get it
                        d = meter.to_dict()

                        # Check it
                        if not isinstance(d, dict):
                            logger.warn("to_dict not returned a dict for k=%s, meter=%s, having=%s", k, meter, d)
                            continue

                        # Browse the dict
                        for name, val in d.iteritems():
                            buf += "{0}={1}\n".format(name, val)
                    except Exception as e:
                        logger.warn("Exception for k=%s, meter=%s, e=%s", k, meter, e)
                        continue

                # Write to file
                try:
                    with open(fname, "w") as f:
                        f.write(buf)
                except Exception as e:
                    logger.warn("Failed to write, fname=%s, e=%s", fname, e)

                # Schedule next write now
                if cls._is_running:
                    cls._write_greenlet = gevent.spawn_later(cls._write_interval_ms / 1000.0, cls._write_meters)
            except GreenletExit:
                pass
            except Exception as e:
                logger.error("e=%s", SolBase.extostr(e))

    # =============================================
    # METER STUFF
    # =============================================

    @classmethod
    def put(cls, meter):
        """
        Put a new meter.
        :param meter: A MeterBase derived class instance.
        :type meter: MeterBase
        :return True if instance has been added, False otherwise (case where the class is already registered)
        :rtype bool
        """

        # Get the key
        key = meter.__class__.__name__

        # Check
        if key in cls._hash_meter:
            logger.debug("key=%s already added, skipping", key)
            return False

        # Store
        cls._hash_meter[key] = meter
        return True

    @classmethod
    def get(cls, meter):
        """
        Get the meter for specified class
        :param meter: A MeterBase derived class (not an instance)
        :type meter: object
        :return MeterBase
        :rtype MeterBase
        """

        # Get
        m = cls._hash_meter.get(meter.__name__)
        if not m:
            logger.warn("Class not registered, key=%s", meter.__name__)
            return None
        return m











