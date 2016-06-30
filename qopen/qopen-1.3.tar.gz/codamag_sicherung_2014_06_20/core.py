# coding=utf-8
# Author: Tom Richter
"""
Determining scattering parameters and seismic moment.

Based partly upon Sens-Schönfelder and Wegler (2006).
"""
# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import argparse
from argparse import SUPPRESS
from collections import defaultdict, OrderedDict
from copy import copy, deepcopy
import json
import logging
import logging.config
import functools
import os.path
from pkg_resources import resource_filename
import shutil
import time

import numpy as np
import obspy
import scipy

from codamag.rt import rt_3D_approx, integrate_t_rt_3D_approx

try:
    import joblib
    from joblib import Parallel, delayed
except ImportError:
    joblib = None
try:
    profile
except:
    def profile(f):
        return f

try:
    cache = functools.lru_cache(maxsize=512)
except AttributeError:
    def cache(f, ignore=None):
        """Caching decorator"""
        cache = {}

        @functools.wraps(f)
        def _f(*args, **kwargs):
            kws = tuple(sorted(kwargs.items()))
            key = args + kws
            try:
                return cache[key]
            except KeyError:
                cache[key] = result = f(*args, **kwargs)
                return result

        def cache_clear():
            _f.cache = {}
        _f.cache = cache
        _f.cache_clear = cache.clear
        return _f

DIRTY_HACK_PICKS = False

log = logging.getLogger('codamag')
log.addHandler(logging.NullHandler())

LOGLEVELS = {0: 'CRITICAL', 1: 'WARNING', 2: 'INFO', 3: 'DEBUG'}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'capture_warnings': True,
    'formatters': {
        'file': {
            'format': ('%(asctime)s %(module)-6s%(process)-6d%(levelname)-8s'
                       '%(message)s')
        },
        'console': {
            'format': '%(levelname)-8s%(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'level': None,
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'level': None,
            'filename': None,
        },
    },
    'loggers': {
        'codamag': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        }

    }
}

DUMP_CONFIG = ['v0', 'rho0', 'R0', 'free_surface', 'M0_freq', 'dt',
               'g0', 'freqs', 'filter',
               'sonset_window', 'coda_window', 'noise_windows',
               'weight', 'remove_noise',
               'adjust_sonset', 'adjust_sonset_options',
               'remove_response', 'correct_for_elevation', 'skip']

DUMP_ORDER = ['M0', 'Mw', 'Mcat', 'freq', 'g0', 'b', 'W', 'omM', 'error', 'R',
              'events', 'config']


def sort_dict(dict_, order=DUMP_ORDER):
    return OrderedDict(sorted(dict_.items(),
                       key=lambda t: order.index(t[0])))


@cache
def bandpass_width(freqmin, freqmax, sr, corners=2, zerophase=False,
                   type='bandpass'):
    """Integrate over the squared filter response"""
    fe = 0.5 * sr
    low = freqmin / fe
    high = freqmax / fe
    b, a = scipy.signal.iirfilter(corners, [low, high], btype='band',
                                  ftype='butter', output='ba')
    w, h = scipy.signal.freqz(b, a)
    df = (w[1] - w[0]) / 2 / np.pi * sr
    return (np.sum(np.abs(h) ** 2) * df) ** (zerophase + 1)


@cache
def get_freqs(max, min, step, width):
    """Determine frequency octave bands"""
    max_exp = int(np.log(max / min)
                  / step / np.log(2))
    exponents = step * np.arange(max_exp + 1)[::-1]
    cfreqs = max / 2 ** exponents
    df = 2 ** (0.5 * width)
    freq_bands = OrderedDict((f, (f / df, f * df)) for f in cfreqs)
    msg = 'central frequencies: (' + '%s, ' * (len(cfreqs) - 1) + '%s)'
    log.info(msg, *cfreqs)
    msg = ('freq bands: ' + '(%.3f, %.3f), ' * len(cfreqs))[:-2]
    log.info(msg, *np.array(sorted(freq_bands.values())).flat)
    return freq_bands


def gmean(data, axis=None):
    """Geometric mean"""
    return np.exp(np.mean(np.log(data), axis=axis))


def gerr(data, axis=None):
    """Lower and upper error of 'geometric standard deviation'"""
    lmean = np.mean(np.log(data), axis=axis)
    lstd = np.std(np.log(data), axis=axis)
    err1 = np.exp(lmean) - np.exp(lmean - lstd)
    err2 = np.exp(lmean + lstd) - np.exp(lmean)
    return err1, err2


def energy1c(data, rho):
    """Energy of one channel"""
    return rho * (data ** 2 + (scipy.fftpack.hilbert(data)) ** 2)


def observed_energy(stream, rho):
    """Return trace with total energy of three component stream"""
    data = [energy1c(tr.data, rho) for tr in stream]
    data = np.sum(data, axis=0)
    tr = obspy.core.Trace(data=data, header=stream[0].stats)
    tr.stats.channel = tr.stats.channel[:2] + 'X'
    return tr


def sds(W, f, v, rho):
    """
    Calculate source displacement spectrum ωM from spectral source energy W

    according to Sato & Fehler (2012, p.188)
    :param W: spectral source energy (J/Hz)
    :param f, v, rho: frequency, mean velocity, mean density
    :return: source displacement spectum (in Nm)
    """
    return np.sqrt(W * 2.5 / np.pi * rho * v ** 5 / f ** 2)


def seismic_moment(freq, omM, M0_freq):
    """
    Calculate seismic moment M0 from source displacement spectrum

    :param freq, omM: frequencies, source displacment spectrum (same length)
    :param M0_freq: corner frequency
    :return: seismic moment M0
    """
    M0 = [o for f, o in zip(freq, omM) if f < M0_freq]
    if len(M0) > 0:
        return gmean(M0)


def moment_magnitude(M0):
    """Moment magnitude Mw from seismic moment M0"""
    return 2 / 3 * np.log10(M0) - 6


def get_station(seedid):
    """Station name from seed id"""
    return seedid.rsplit('.', 2)[0]


def get_eventid(event):
    """Event id from event"""
    return str(event.resource_id).split('/')[-1]

def get_pair(tr):
    """Station and event id from trace"""
    return (tr.stats.eventid, get_station(tr.id))

def remove_stream(streams, pair):
    """Remove stream corresponding to (evid, sta) pair"""
    for stream in copy(streams):
        if get_pair(stream[0]) == pair:
            streams.remove(stream)

def get_picks(origin, station):
    """Picks for specific station from origin"""
    if DIRTY_HACK_PICKS:
        log.warning('USE DIRTY_HACK_PICKS')
        station = station[2:]
    picks = {}
    for arrival in origin.arrivals:
        phase = arrival.phase
        if DIRTY_HACK_PICKS and phase in ('Pg', 'Sg'):
            phase = phase[0]
        if phase not in 'PS':
            continue
        pick = arrival.pick_id.getReferredObject()
        seedid = pick.waveform_id.getSEEDString()
        if station == get_station(seedid):
            if phase in picks:
                msg = '%s, %s-onset: multiple picks'
                raise ValueError(msg % (station, phase))
            picks[phase] = pick.time
    return picks


def tw_utc(tw, onset, origin_time=None, noise_level=None, trace=None):
    """Convert time window with units (s, tt, SNR) to UTC time window"""
    tw_utc = []
    for i, t in enumerate(tw):
        if t.endswith('s'):
            t = onset + float(t[:-1])
        elif t.endswith('tt'):
            t = origin_time + float(t[:-2]) * (onset - origin_time)
        elif t.endswith('SNR'):
            assert i == 1
            tr = trace.slice(starttime=tw_utc[0])
            snr = float(t[:-3])
            try:
                index = np.where(tr.data < snr * noise_level)[0][0] - 1
            except IndexError:
                index = len(tr.data) - 1
            t = tr.stats.starttime + index * trace.stats.delta
        else:
            raise ValueError('Unexpected value for time window')
        tw_utc.append(t)
    return tw_utc


def collect_results(event_results):
    """Collect g0, b, error and R from results of multiple events"""
    g0, b, error, R = [], [], [], defaultdict(list)
    for eventid, res in event_results.items():
        g0.append(res['g0'])
        b.append(res['b'])
        error.append(res['error'])
        for sta, Rsta in res['R'].items():
            R[sta].append(Rsta)
    g0 = np.array(g0, dtype=np.float)
    b = np.array(b, dtype=np.float)
    error = np.array(error, dtype=np.float)
    R = dict(R)
    for sta in R:
        R[sta] = np.array(R[sta], dtype=np.float)
    return g0, b, error, R


@profile
def codamagf(freq_band, streams,
             filter, rho0, v0, R0, g0,
             noise_windows, sonset_window, coda_window, weight,
             free_surface=4,
             dt=None, remove_noise=False, skip={},
             adjust_sonset=None, adjust_sonset_options={},
             plot_energies=False, plot_energies_options={},
             plot_optimization=False, plot_optimization_options={},
             plot_optresult=False, plot_optresult_options={},
             ignore_network_code=False,
             label_eventid=True,
             borehole_stations=(),
             **kwargs):
    """
    Codamag function for given streams and a specific frequency band

    :param freq_band, streams, label_eventid, borehole_stations:
        are calculated in codamag function.
    All other options are described in the example configuration file.
    """
    msg = 'freq band (%.2fHz, %.2fHz): start optimization'
    log.debug(msg, *freq_band)
    if len(streams) == 0:
        msg = ('freq band (%.2fHz, %.2fHz): no data availlable '
               '-> skip frequency band')
        log.warning(msg, *freq_band)
        return
    #eventid = get_eventid(event)
    #origin_time = (event.preferred_origin() or event.origins[0]).time

    def _tw_utc2s(tw_utc, otime):
        tw = []
        for t in tw_utc:
            tw.append(t - otime)
        return '(%.2fs, %.2fs)' % tuple(tw)

    # Filter traces, normalize to preserve energy density
    # and calculate observed energy
    freqmin, freqmax = freq_band
    energies = []
    for stream in streams:
        pair = get_pair(stream[0])
        sr = stream[0].stats.sampling_rate
        if freqmax > 0.5 * sr:
            msg = '%s %s: High corner frequency is above Nyquist -> skip'
            log.warning(msg, *pair)
            continue
        stream.filter(freqmin=freqmin, freqmax=freqmax, **filter)
        if filter['type'] == 'bandpass':
            df = bandpass_width(freqmin, freqmax, sr, **filter)
            for tr in stream:
                tr.data /= df
        try:
            energies.append(observed_energy(stream, rho0))
        except Exception as ex:
            msg = '%s %s: cannot calculate ernergy (%s)'
            log.error(msg, pair[0], pair[1], str(ex))
    # HACK for data given as energy
#    for stream in streams:
#        tr = stream[0].copy()
#        tr.data = tr.data + stream[1].data + stream[2].data
#        energies[get_station(stream[0].id)] = tr
    # end HACK
    if len(energies) == 0:
        msg = ('freq band (%.2f, %.2f): no data availlable -> '
               'skip frequency band')
        log.warning(msg, *freq_band)
        return
    # Calculate time windows in UTC
    sonsetw = {}
    codaw = {}
    time_adjustments = []
    for energy in energies:
        # Calculate noise level
        pair = get_pair(energy)
        noise_levels = []
        otime = energy.stats.origintime
        ponset = energy.stats.ponset
        sonset = energy.stats.sonset
        distance = energy.stats.distance
        for i, nw in enumerate(noise_windows):
            noisew = tw_utc(nw, ponset, otime)
            tr_noisew = energy.slice(*noisew)
            if len(tr_noisew.data) and np.all(np.isfinite(tr_noisew.data)):
                noise_levels.append(np.mean(tr_noisew.data))
        if len(noise_levels) == 0:
            noise_level = None
            log.error('all noise windows outside requested data')
        else:
            energy.stats.noise_level = noise_level = np.min(noise_levels)
            log.debug('%s: noise level at %.1e', pair, noise_level)
        # Optionally remove noise
        if remove_noise:
            energy.data = energy.data - noise_level
            energy.data[energy.data < 0] = noise_level / 100
            energy.data[energy.data < noise_level / 100] = noise_level / 100
        # Optionally adjust S-onset
        wkwargs = {'noise_level': noise_level, 'trace': energy}
        if adjust_sonset == "maximum":
            try:
                max_window = adjust_sonset_options['window']
            except KeyError:
                msg = ('no window for maximum specified -> '
                       'taking original S-onset window')
                log.error(msg)
                max_window = sonset_window
            mw = tw_utc(max_window, sonset, otime, **wkwargs)
            energy.stats.sonset_old = sonset_old = sonset
            imax = np.argmax(energy.slice(*mw).data)
            energy.stats.sonset = sonset = mw[0] + imax * energy.stats.delta
            msg = '%s: adjust S-onset from %.2fs to %.2fs'
            ta = sonset - sonset_old
            vnew = distance / (sonset - otime)
            time_adjustments.append((ta, vnew))
            log.debug(msg, pair, sonset_old - otime, sonset - otime)
            # old method
# Calculate a 'better' S-onset by adjusting the S-onset defined by the
# above options.
# The routine searches for the maximum of the energy(t) function in the
# given time window (defined relative to preliminary S-onset, has to be
# defined in the same way as the following three windows).
# Then it looks for the minimum in consecutive time windows of length 'len'
# (in seconds) before the maximum. If the minimum is becoming larger again
# this procedure is stopped and the minimum is found. In the third step the
# algorithm goes again forward up to a level of 'min + level * (max - min)'.
# The obtained time is used as new S-onset
#            son_old = son
#            adjust_window = adjust_options['window']
#            adjust_window_len = adjust_options['len']
#            adjust_level = adjust_options['level']
# Go left from maximum and find minimum
#            adjustw = tw_utc(adjust_window, son, origin_time, **wkwargs)
#            data = Eobs.slice(*adjustw).data
#            samples = int(round(Eobs.stats.sampling_rate * adjust_window_len))
#            j = i = np.argmax(data)
#            mi = ma = data[i]
#            while i >= samples:
#                i = i - samples
#                if np.min(data[i:i + samples]) >= mi:
#                    break
#                j = i + np.argmin(data[i:i + samples])
#                mi = data[j]
# Go right from minimum and find level
#            if adjust_level:
#                level = mi + (ma - mi) * adjust_level
#                j = j + np.where(data[j:] >= level)[0][0]
#            sonset[station] = son = adjustw[0] + j * Eobs.stats.delta
#            msg = '%s: adjust S-onset from %.2fs to %.2fs'
#            ta = son - son_old
#            vnew = distances[station] / (son - origin_time)
#            time_adjustments.append((ta, vnew))
#            log.debug(msg, station, son_old - origin_time, son - origin_time)
        # Calculate S-onset and coda window
        sonsetw[pair] = tw_utc(sonset_window, sonset, otime, **wkwargs)
        codaw[pair] = tw_utc(coda_window, sonset, otime, **wkwargs)
        # Round beginning of coda window to dt
        if dt:
            t0 = codaw[pair][0] - sonset + 0.5 * dt
            codaw[pair][0] = sonset + round(t0 / dt) * dt - 0.5 * dt
        msg = '%s: S-onset window %s, coda window %s'
        log.debug(msg, pair, _tw_utc2s(sonsetw[pair], otime),
                  _tw_utc2s(codaw[pair], otime))
    if adjust_sonset and len(time_adjustments) > 0:
        ta, vnew = np.mean(time_adjustments, axis=0)
        msg = ('mean of time adjustments is %.2fs, corresponds to a velocity '
               'of %dkm/s')
        log.debug(msg, ta, vnew)
    # Optionally plot energies
    try:
        pass
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log.exception('error while creating a plot')
    # Start inversion
    # Bi = ln(Ei) - ln(Gji)
    # Ai = 1 0 0 0 0 -1
    # Solve |AC-B| -> min
    # Construct part of the linear equation system
    tc = []
    Eobsc = []
    tb = []
    Eobsb = []
    tbulkinterval = []
    remove_pairs = []
    distances = {}
    for energy in energies:
        evid, sta = pair = get_pair(energy)
        free_surface_corr = (sta in borehole_stations) or free_surface
        otime = energy.stats.origintime
        sonset = energy.stats.sonset
        distances[pair] = distance = energy.stats.distance
        sr = energy.stats.sampling_rate
        # Optionally skip some stations
        if skip and skip.get('coda_window'):
            cw = codaw[pair]
            val = skip['coda_window']
            if val and cw[1] - cw[0] < val:
                msg = ('%s: coda window of length %.1fs shorter than '
                       '%.1f -> skip')
                log.debug(msg, pair, cw[1] - cw[0], val)
                remove_pairs.append(pair)
                continue
        if skip and skip.get('distance'):
            val = skip['distance']
            if val and distance / 1000 > val:
                msg = '%s: distance %.1fkm larger than %.1fkm -> skip'
                log.debug(msg, pair, distance / 1000, val)
                remove_pairs.append(pair)
                continue
        if skip and skip.get('maximum'):
            max_window = skip['maximum']
            mw = tw_utc(max_window, sonset, otime, **wkwargs)
            imax = np.argmax(energy.data)
            tmax = energy.stats.starttime + imax / sr
            if not (mw[0] < tmax < mw[1]):
                msg = ('%s: maximum at %.1fs not in window around S-onset '
                       '(%.1fs, %.1fs) -> skip')
                log.debug(msg, pair, tmax - otime,
                          mw[0] - otime, mw[1] - otime)
                remove_pairs.append(pair)
                continue
        # Get coda data, optionally reduce data
        try:
            codaobs = energy.slice(*codaw[pair])
        except ValueError as ex:
            msg = '%s: cannot get coda window (%s) -> skip'
            log.warning(msg, pair, ex)
            remove_pairs.append(pair)
            continue
        Nc = len(codaobs.data)
        if dt is None:
            samples = 1
            codadata = np.log(codaobs.data / free_surface_corr)
        else:
            samples = int(round(dt * sr))
            Nc = Nc // samples
            if Nc == 0:
                msg = '%s: coda window shorter than %d samples -> skip'
                log.warning(msg, pair, samples)
                remove_pairs.append(pair)
                continue
            codadata = codaobs.data[:Nc * samples]
            codadata = codadata.reshape((Nc, samples))
            codadata = np.mean(np.log(codadata / free_surface_corr), axis=1)
        # Adjust tcoda to onset of Green's function
        tcoda = (0.5 * bool(dt) + np.arange(Nc)) / sr * samples
        tcoda = tcoda + distance / v0 + (codaw[pair][0] - sonset)
        if np.any(tcoda <= distance / v0):
            msg = '%s: selected coda window includes S-onset -> skip station'
            log.error(msg, pair)
            remove_pairs.append(pair)
            continue
        Eobsc.append(codadata)
        tc.append(tcoda)
        # Get bulk data, calculate mean and adjust weight
        try:
            bulkobs = energy.slice(*sonsetw[pair])
        except ValueError as ex:
            msg = '%s: cannot get S-onset window (%s) -> skip'
            log.warning(msg, pair, ex)
            remove_pairs.append(pair)
            Eobsc.pop(-1)
            tc.pop(-1)
            continue
        Nb = len(bulkobs.data)
        tbulk = np.arange(Nb) / sr + distance / v0 + (sonsetw[pair][0] - sonset)
        tbulkinterval.append((tbulk[0], tbulk[-1]))
        if weight[1] == 'codawindow':
            Nb = Nc
        elif weight[1] == 'samples':
            Nb = 1
        else:
            Nb = max(1, Nb // samples)
        Nb = max(1, int(round(weight[0] * Nb)))
        bulkmean = np.log(np.mean(bulkobs.data) / free_surface_corr)
        tbulkmean = np.sum(bulkobs.data * tbulk) / np.sum(bulkobs.data)
        Eobsb.append(np.ones(Nb) * bulkmean)
        tb.append(np.ones(Nb) * tbulkmean)


    if len(Eobsc) == 0:
        msg = ('freq band (%.2f, %.2f): no pairs left -> '
               'skip frequency band')
        log.warning(msg, *freq_band)
        return
    event_station_pairs = [get_pair(energy) for energy in energies
                           if get_pair(energy) not in remove_pairs]
    eventids, stations = zip(*event_station_pairs) # TODO create matrix for more than one event
    As = []
    for i, B in enumerate(Eobsc + Eobsb):
        A = np.zeros((len(stations) + 1, len(B)))
        A[i % len(stations), :] = 1
        As.append(A)
    A = np.hstack(As)
    A[-1, :] = -np.hstack(tc + tb)
    A = np.transpose(A)
    record = []
    max_record = 11
    # Define error for optimization

    def lstsq(g0, opt=False):
        if opt and g0 <= 0:
            return np.inf
        Gc = []
        Gb = []
        for i, pair in enumerate(event_station_pairs):
            assert len(Eobsb[i]) > 0
            r = distances[pair]
            Gcoda = np.log(rt_3D_approx(r, tc[i], v0, 1 / g0))
            Gc.append(Gcoda)
        for i, pair in enumerate(event_station_pairs):
            r = distances[pair]
            t1, t2 = tbulkinterval[i]
            t = r / v0 + t2 - t1
            Gbulk, _Gbulkerr = integrate_t_rt_3D_approx(r, t, v0, 1 / g0)
            Gbulk = np.log(Gbulk / (t2 - t1))
            Gb.append(Gbulk)
        Bc = [Eobsc[i] - Gc[i] for i in range(len(stations))]
        Bb = [Eobsb[i] - Gb[i] for i in range(len(stations))]
        B = np.hstack(Bc + Bb)
        C, _residual, _rank, _singular_values = scipy.linalg.lstsq(A, B)
        b = C[-1]  # intrinsic attenuation
        err = 0
        for i in range(len(stations)):
            err += np.sum((Bc[i] - C[i] + b * tc[i]) ** 2)
        for i in range(len(stations)):
            err += np.sum((Bb[i] - C[i] + b * tb[i]) ** 2)
        err = (err / A.shape[0]) ** 0.5  # normalize to one data point
        W = np.exp(np.mean(C[:-1])) / R0  # spectral source energy
        R = np.exp(C[:-1]) / W  # amplification factors
        if plot_optimization and (len(record) < max_record or not opt):
            record.append((g0, err, b, W, R, Bc, Bb))
        if opt:
            return err
        else:
            return b, W, R, err, Gc, Gb
    # Optimize g0
    optimize = scipy.optimize.minimize_scalar
    opt = optimize(lstsq, args=(True,), method='golden', **g0)
    g0opt = opt.x
    b, W, R, err, Gc, Gb = lstsq(g0opt)
    if b < 0:
        log.warning('b<0 detected -> set to null/nan')
        b = None
    msg = ('optimization solved %d equations with %d unknowns %d times, '
           'minimal error: %.1e')
    log.debug(msg, A.shape[0], A.shape[1], opt.nfev, err)
    if len(kwargs) > 0:
        log.error('unused kwargs: %s', json.dumps(kwargs))
    if ignore_network_code:  # hack for undocumented option
        stations = [st.split('.', 1)[1] for st in stations]
    # Arrange result
    R_result = {station: Ri for station, Ri in zip(stations, R)}
    result = {'g0': g0opt, 'b': b, 'W': W, 'R': R_result, 'error': err}
    msg = 'freq band (%.2fHz, %.2fHz): optimization result is %s'
    log.debug(msg, freq_band[0], freq_band[1], json.dumps(result))
    # Optionally plot result of optimization routine
    def fname_and_title(fname, evtotitle=False):
        part1 = '%05.2fHz-%05.2fHz' % freq_band
        title = 'filter: (%.2fHz, %.2fHz)' % freq_band
        if label_eventid:
            eventid = energies[0].stats.eventid
            part1 = '%s_%s' % (eventid, part1)
            if evtotitle:
                title = 'event: %s  %s' % (eventid, title)
        return (fname % part1), title
    try:
        if plot_energies and len(energies) > 0:
            pkwargs = copy(plot_energies_options)
            fname = pkwargs.pop('fname', 'energies_%s.pdf')
            fname, title = fname_and_title(fname, True)
            pkwargs.update({'sonset_window': sonsetw, 'coda_window': codaw})
            from codamag.imaging import plot_energies
            plot_energies(energies, fname=fname, title=title, **pkwargs)
            log.debug('create energies plot at %s', fname)
        if plot_optimization:
            pkwargs = copy(plot_optimization_options)
            fname = pkwargs.pop('fname', 'optimization_%s.pdf')
            fname, title = fname_and_title(fname)
            from codamag.imaging import plot_optimization
            plot_optimization(record, tc=tc, tb=tb, fname=fname, title=title,
                              **pkwargs)
            log.debug('create optimization plot at %s', fname)
        if plot_optresult:
            pkwargs = copy(plot_optresult_options)
            fname = pkwargs.pop('fname', 'optresult_%s.pdf')
            fname, title = fname_and_title(fname)
            from codamag.imaging import plot_optresult
            plot_optresult(event_station_pairs, tc, Eobsc, Gc, tb, Eobsb,
                           Gb, b, W, R,
                           title=title, fname=fname, distances=distances)
            log.debug('create optresult plot at %s', fname)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log.exception('error while creating a plot')
    return g0opt, b, W, err, R_result


@profile
def codamag(events, inventory, get_waveforms,
            request_window, freqs,
            vp, vs, rho0,
            remove_response=None, use_picks=False,
            correct_for_elevation=False,
            M0_freq=None, parallel=False, njobs=1,
            plot_eventresult=False, plot_eventresult_options={},
            plot_eventsites=False, plot_eventsites_options={},
            **kwargs):
    """
    Codamag function for one event and a specific frequency band

    :param event, inventory, get_waveforms: are calculated in main function
    :param warned: dictionary to remeber warnings
    All other options are described in the example configuration file.
    """
    if joblib and parallel:
        log.debug('use %d cores for parallel computation', njobs)
    elif parallel:
        log.warning('install joblib to use parallel option')
    # Get origins and magnitudes of event
    origins = {}
    magnitudes = {}
    for event in events:
        try:
            origin = event.preferred_origin() or event.origins[0]
        except IndexError:
            msg = 'event %s: no associated origin -> skip event'
            log.error(msg, get_eventid(event))
            continue
        origins[get_eventid(event)] = origin
        try:
            mag = event.preferred_magnitude() or event.magnitudes[0]
        except IndexError:
            magnitudes[get_eventid(event)] = None
        magnitudes[get_eventid(event)] = mag.mag

    origins = OrderedDict(sorted(origins.items(), key=lambda o: o[1].time))
    # Get freqeuencies
    freq_bands = get_freqs(**freqs)
    # Get stations
    channels = inventory.get_contents()['channels']
    stations = list(set(get_station(ch) for ch in channels))
    one_channel = {get_station(ch): ch for ch in channels}
    event_station_pairs = [(evid, sta) for evid in origins
                           for sta in stations]
    # Start processing
    # Calculate distances
    def _get_coordinates(station, time=None):
        return inventory.get_coordinates(one_channel[station], datetime=time)

    borehole_stations = set()

    @cache
    def _get_distance(evid, sta):
        ori = origins[evid]
        c = _get_coordinates(sta, time=ori.time)
        args = (c['latitude'], c['longitude'], ori.latitude, ori.longitude)
        hdist = obspy.core.util.geodetics.gps2DistAzimuth(*args)[0]
        vdist = (ori.depth + c['elevation'] * correct_for_elevation -
                 c['local_depth'])
        if c['local_depth'] > 0:
            borehole_stations.add(sta)
        return np.sqrt(hdist ** 2 + vdist ** 2)

    distances = {}
    for pair in copy(event_station_pairs):
        try:
            distances[pair] = _get_distance(*pair)
        except:
            msg = '%s %s: exception while determining distances -> skip'
            log.exception(msg, *pair)
            event_station_pairs.remove(pair)
        else:
            # hack for undocumented option
            if kwargs.get('ignore_network_code'):
                new_key = (pair[0], pair[1].split('.', 1)[1])
                distances[new_key] = distances[pair]
    # Sort stations by distance
    event_station_pairs = sorted(
        event_station_pairs, key=lambda p: (origins[p[0]].time, distances[p]))
    # Calculate onsets
    def _get_onsets(evid, sta):
        ori = origins[evid]
        if use_picks:
            onsets = get_picks(ori, sta)
        else:
            onsets = {'P': ori.time + _get_distance(evid, sta) / vp,
                      'S': ori.time + _get_distance(evid, sta) / vs}
        return onsets

    try:
        onsets = {'P': {}, 'S': {}}
        for pair in copy(event_station_pairs):
            ons = _get_onsets(*pair)
            try:
                onsets['P'][pair] = ons['P']
                onsets['S'][pair] = ons['S']
            except KeyError:
                log.debug('%s %s: no pick/onset -> skip', *pair)
                event_station_pairs.remove(pair)
    except Exception as ex:
        log.exception('exception while determining onsets -> skip all')
        return
    log.debug('origin station distances: %s', distances)
    log.debug('onsets: %s', onsets)
    if len(borehole_stations) > 0:
        msg = 'identified borehole stations: %s'
        log.debug(msg, ' '.join(borehole_stations))

    # Retrieve data
    streams = []
    for pair in copy(event_station_pairs):
        evid, sta = pair
        seedid = one_channel[sta][:-1] + '?'
        net, sta, loc, cha = seedid.split('.')
        t1 = origins[evid].time + request_window[0]
        t2 = origins[evid].time + request_window[1]
        kwargs2 = {'network': net, 'station': sta, 'location': loc,
                   'channel': cha, 'starttime': t1, 'endtime': t2}
        stream = get_waveforms(**kwargs2)
        if stream:
            stream.merge()
        if stream is None:
            event_station_pairs.remove((evid, sta))
        elif len(stream) != 3:
            seedid = one_channel[sta][:-1] + '?'
            msg = 'channel %s: number of traces is not 3 -> discard'
            log.debug(msg, seedid)
            event_station_pairs.remove((evid, sta))
        else:
            for tr in stream:
                tr.stats.eventid = evid
                tr.stats.origintime = origins[evid].time
                tr.stats.ponset = onsets['P'][pair]
                tr.stats.sonset = onsets['S'][pair]
                tr.stats.distance = distances[pair]
            streams.append(stream)
    msg = 'succesfully requested %d streams for %d stations and %d events'
    log.info(msg, len(streams), len(stations), len(origins))
    # Remove instrument response
    if remove_response:
        for stream in copy(streams):
            pair = get_pair(stream[0])
            fail = stream.attach_response(inventory)
            if len(fail) > 0:
                msg = '%s %s: no instrument response availlable -> skip'
                log.error(msg, *pair)
                streams.remove(stream)
                event_station_pairs.remove(pair)
                continue
            try:
                if remove_response == 'full':
                    stream.remove_response()
                else:
                    for tr in stream:
                        sens = tr.stats.response.instrument_sensitivity
                        tr.data = tr.data / sens.value
            except Exception as ex:
                msg = ('%s %s: removing response/sensitivity failed (%s)'
                       '-> skip')
                log.error(msg, pair[0], pair[1], ex)
                streams.remove(stream)
                event_station_pairs.remove(pair)
                continue
        msg = ('instrument correction finished for %d streams of %d stations'
               ' and %d events')
        log.info(msg, len(streams), len(stations), len(origins))

    # Start codamagf function
    if joblib and parallel:
        rlist = Parallel(n_jobs=njobs, pre_dispatch='1.5*n_jobs')(
            delayed(codamagf)(fb, deepcopy(streams), rho0=rho0,
                              borehole_stations=borehole_stations, **kwargs)
            for fb in freq_bands.values())
    else:
        rlist = [codamagf(fb, deepcopy(streams), rho0=rho0,
                          borehole_stations=borehole_stations, **kwargs)
                 for fb in freq_bands.values()]
    if kwargs.get('ignore_network_code'):  # hack for undocumented option
        stations = [st.split('.', 1)[1] for st in stations]
    # Re-sort results
    result = defaultdict(list)
    result['R'] = defaultdict(list)
    for (cfreq, freq_band), res in zip(freq_bands.items(), rlist):
        if res is None:
            msg = 'freq band (%.2f, %.2f): no result'
            log.warning(msg, *freq_band[0])
            g0, b, W, error, R, omM = 6 * (None,)
        else:
            g0, b, W, error, R = res
            omM = sds(W, cfreq, kwargs.get('v0'), rho0)
        result['freq'].append(cfreq)
        result['g0'].append(g0)
        result['b'].append(b)
        result['W'].append(W)
        result['omM'].append(omM)
        result['error'].append(error)
        for st in stations:
            result['R'][st].append(R.get(st))
    for st in stations:
        if np.all(np.isnan(np.array(result['R'][st], dtype=np.float))):
            result['R'].pop(st)
    result['R'] = dict(result['R'])
    result = dict(result)
    if 'freq' not in result:
        log.error('no result')
        return
    # Calculate M0 and Mw
    if M0_freq:
        M0 = seismic_moment(result['freq'], result['omM'], M0_freq)
        if M0 is not None:
            Mw = moment_magnitude(M0)
            result['M0'] = M0
            result['Mw'] = Mw
            mag = magnitudes[get_eventid(events[0])] # TODO
            if mag is not None:
                result['Mcat'] = mag
    result = sort_dict(result)
    msg = 'result is %s'
    log.debug(msg, json.dumps(result))
    # Optionally plot stuff
    try:
        plot_(result, event=event, v0=kwargs.get('v0'), M0_freq=M0_freq,
              plot_eventresult=plot_eventresult,
              plot_eventresult_options=plot_eventresult_options,
              plot_eventsites=plot_eventsites,
              plot_eventsites_options=plot_eventsites_options
              )
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log.exception('error while creating a plot')
    return result


@profile
def codamags(events,
             plot_results=False, plot_results_options={},
             plot_sites=False, plot_sites_options={},
             plot_sds=False, plot_sds_options={},
             plot_mags=False, plot_mags_options={},
             **kwargs):
    """Codamag function for a list or Catalog of events"""
    # Start processing
    result = {'events': {}, 'R': {}}
    for i, event in enumerate(events):
        msg = 'event %s (no %d of %d): %s processing'
        log.info(msg, get_eventid(event), i + 1, len(events), 'start')
        res = codamag([event], **kwargs)
        log.info(msg, get_eventid(event), i + 1, len(events), 'end')
        if res:
            result['freq'] = res.pop('freq')
            result['events'][get_eventid(event)] = res
    if len(result['events']) == 0:
        log.error('codamag did not produce any result')
        return
    g0, b, error, R = collect_results(result['events'])
    result['g0'] = gmean(g0, axis=0).tolist()
    result['b'] = gmean(b, axis=0).tolist()
    result['error'] = gmean(error, axis=0).tolist()
    for st, Rst in R.items():
        result['R'][st] = gmean(Rst, axis=0).tolist()
    result['config'] = {k: kwargs[k] for k in DUMP_CONFIG if k in kwargs}
    result['config'] = sort_dict(result['config'], order=DUMP_CONFIG)
    result = sort_dict(result)
    # Optionally plot stuff
    try:
        plot_(result, plot_results=plot_results,
              plot_results_options=plot_results_options,
              plot_sites=plot_sites, plot_sites_options=plot_sites_options,
              plot_sds=plot_sds, plot_sds_options=plot_sds_options,
              plot_mags=plot_mags, plot_mags_options=plot_mags_options)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log.exception('error while creating a plot')
    return result


def plot_(result, event=None, v0=None, M0_freq=None,
          plot_results=False, plot_results_options={},
          plot_sites=False, plot_sites_options={},
          plot_sds=False, plot_sds_options={},
          plot_mags=False, plot_mags_options={},
          plot_eventresult=False, plot_eventresult_options={},
          plot_eventsites=False, plot_eventsites_options={},
          **kwargs
          ):
    if event is None:
        if plot_results:
            pkwargs = copy(plot_results_options)
            fname = pkwargs.pop('fname', 'results.pdf')
            from codamag.imaging import plot_results
            plot_results(result, fname=fname, **pkwargs)
            log.debug('create results plot at %s', fname)
        if plot_sites:
            pkwargs = copy(plot_sites_options)
            fname = pkwargs.pop('fname', 'sites.pdf')
            from codamag.imaging import plot_sites
            plot_sites(result, fname=fname, **pkwargs)
            log.debug('create sites plot at %s', fname)
        if plot_sds:
            pkwargs = copy(plot_sds_options)
            fname = pkwargs.pop('fname', 'sds.pdf')
            from codamag.imaging import plot_all_sds
            plot_all_sds(result, fname=fname, **pkwargs)
            log.debug('create sds plot at %s', fname)
        temp = result['events'].values()[0]
        if plot_mags and 'Mw' in temp and 'Mcat' in temp:
            pkwargs = copy(plot_mags_options)
            fname = pkwargs.pop('fname', 'mags.pdf')
            from codamag.imaging import plot_mags
            plot_mags(result, fname=fname, **pkwargs)
            log.debug('create mags plot at %s', fname)
    else:
        if isinstance(event, obspy.core.event.Event):
            eventid = get_eventid(event)
        else:
            v0 = result['v0']
            eventid = event
            try:
                result = result['events'][eventid]
            except KeyError:
                raise ParseError('No event with this id in results')
            M0_freq = result.get('config', {}).get('M0_freq')
        if plot_eventresult:
            pkwargs = copy(plot_eventresult_options)
            fname = pkwargs.pop('fname', 'eventresult_%s.pdf')
            fname = fname % (eventid,)
            title = 'event %s' % (eventid,)
            from codamag.imaging import plot_eventresult
            plot_eventresult(result, v0=v0, M0_freq=M0_freq, title=title,
                             fname=fname)
            log.debug('create eventresult plot at %s', fname)
        if plot_eventsites:
            pkwargs = copy(plot_eventsites_options)
            fname = pkwargs.pop('fname', 'eventsites_%s.pdf')
            fname = fname % (eventid,)
            title = 'event %s' % (eventid,)
            from codamag.imaging import plot_eventsites
            plot_eventsites(result, title=title, fname=fname)
            log.debug('create eventsites plot at %s', fname)


def init_data(s, client_options=None, plugin=None, cache_waveforms=False):
    """Return appropriate get_waveforms function"""
    if client_options is None:
        client_options = {}
    if s == 'arclink':
        from obspy.arclink import Client
        client = Client(**client_options)
        get_waveforms = client.getWaveform
    elif s == 'fdsn':
        from obspy.fdsn import Client
        client = Client(**client_options)
        get_waveforms = client.get_waveforms
    elif s == 'seishub':
        from obspy.seishub import Client
        client = Client(**client_options)
        get_waveforms = client.getWaveform
    elif s == 'plugin':
        modulename, funcname = plugin.split(':')
        import sys
        from importlib import import_module
        sys.path.append(os.path.curdir)
        module = import_module(modulename.strip())
        get_waveforms = getattr(module, funcname.strip())
    else:
        from obspy import read
        stream = read(s)

        def get_waveforms(network, station, location, channel,
                          starttime, endtime):
            st = stream.select(network=network, station=station,
                               location=location, channel=channel)
            st = st.slice(starttime, endtime)
            return st

    def wrapper(**kwargs):
        try:
            return get_waveforms(**kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            seedid = '.'.join((kwargs['network'], kwargs['station'],
                               kwargs['location'], kwargs['channel']))
            msg = 'channel %s: error while retireving data: %s'
            log.debug(msg, seedid, ex)

    temp = s in ('arclink', 'fdsn', 'seishub', 'plugin')
    if cache_waveforms and joblib and temp:
        log.info('use waveform cache in %s', cache_waveforms)
        memory = joblib.Memory(cachedir=cache_waveforms, verbose=0)
        return memory.cache(wrapper)
    elif cache_waveforms and temp:
        log.warning('install joblib to use cache_waveforms option')
    return wrapper


class ConfigJSONDecoder(json.JSONDecoder):

    """Strip lines from comments"""

    def decode(self, s):
        s = '\n'.join(l.split('#', 1)[0] for l in s.split('\n'))
        return super(ConfigJSONDecoder, self).decode(s)


class ParseError(Exception):
    pass


def main(conf=None, create_config=None, tutorial=False, eventid=None,
         get_waveforms=None, plot=None, **args):
    """
    Main entry point for a direct function call

    Example call: main(conf='conf.json')

    :param args: All args correspond to the respective command line and
        configuration options.
        See the example configuration file for help and possible arguments.
        Options in args can overwrite the configuration from the file.
    Exceptions:
    :param events: can be filename or ObsPy Catalog object
    :param stations: can be filename or ObsPy Inventory object
    :param get_waveforms: function, if given the data option will be ignored.
        get_waveforms will be called as described in the example configuration
        file
    """
    time_start = time.time()
    # Copy example files if create_config
    if create_config:
        srcs = ['conf.json']
        dest_dir = os.path.dirname(create_config)
        dests = [create_config]
        if tutorial:
            example_files = ['example_events.xml', 'example_inventory.xml',
                             'example_data.mseed']
            srcs.extend(example_files)
            for src in example_files:
                dests.append(os.path.join(dest_dir, src))
        for src, dest in zip(srcs, dests):
            src = resource_filename('codamag', 'example/%s' % src)
            shutil.copyfile(src, dest)
        return
    if tutorial:
        msg = '--tutorial flag can only be used with --create_config'
        raise ParseError(msg)
    # Parse config file
    if conf:
        try:
            with open(conf) as f:
                conf = json.load(f, cls=ConfigJSONDecoder)
        except ValueError as ex:
            print('Error while parsing the configuration: %s' % ex)
            return
        except IOError as ex:
            print(ex)
            return
        # Populate args with conf, but prefer args
        conf.update(args)
        args = conf
    # Optionally plot
    if plot:
        with open(plot) as f:
            result = json.load(f)
        plot_(result, event=eventid, **args)
        return
    # Configure logging
    loggingc = args.pop('logging', None)
    if loggingc is None:
        loggingc = deepcopy(LOGGING)
        verbose = args.pop('verbose', 0)
        if verbose > 3:
            verbose = 3
        loggingc['handlers']['console']['level'] = LOGLEVELS[verbose]
        loglevel = args.pop('loglevel', 3)
        logfile = args.pop('logfile', None)
        if logfile is None or loglevel == 0:
            del loggingc['handlers']['file']
            loggingc['loggers']['codamag']['handlers'] = ['console']
            loggingc['loggers']['py.warnings']['handlers'] = ['console']
        else:
            loggingc['handlers']['file']['level'] = LOGLEVELS[loglevel]
            loggingc['handlers']['file']['filename'] = logfile
    logging.config.dictConfig(loggingc)
    logging.captureWarnings(loggingc.get('capture_warnings', False))
    try:
        # Read events
        events = args.pop('events')
        if not isinstance(events, (list, obspy.core.event.Catalog)):
            events = obspy.readEvents(events)
            log.info('read %d events', len(events))
        # Read inventory
        inventory = args.pop('inventory')
        if not isinstance(inventory, obspy.station.Inventory):
            inventory = obspy.read_inventory(inventory)
            channels = inventory.get_contents()['channels']
            stations = list(set(get_station(ch) for ch in channels))
            log.info('read inventory with %d stations', len(stations))
        # Initialize get_waveforms
        keys = ['client_options', 'plugin', 'cache_waveforms']
        tkwargs = {k: args.pop(k, None) for k in keys}
        if get_waveforms is None:
            data = args.pop('data')
            get_waveforms = init_data(data, **tkwargs)
            log.info('init data from %s', data)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log.exception('cannot read events/stations or initalize data')
        return
    # Optionally select event
    if eventid:
        elist = []
        elist = [ev for ev in events if get_eventid(ev) == eventid]
        if len(elist) == 0:
            msg = ('Did not find any event with id %s.\n'
                   'Example id from file: %s')
            raise ParseError(msg % (eventid, str(ev.resource_id)))
        log.debug('use only event with id %s', eventid)
        events = obspy.core.event.Catalog(elist)
    # Start main routine with remaining args
    log.debug('start codamag routine with parameters %s', json.dumps(args))
    args['inventory'] = inventory
    args['get_waveforms'] = get_waveforms
    args['events'] = events
    output = args.pop('output', None)
    indent = args.pop('indent', None)
    result = codamags(**args)
    # Output and return result
    log.debug('final results: %s', json.dumps(result))
    if output == 'stdout':
        print(json.dumps(result))
    elif output is not None:
        with open(output, 'wb') as f:
            json.dump(result, f, indent=indent)
    time_end = time.time()
    log.debug('used time: %.1fs', time_end - time_start)
    return result


def main_cmdline(args=None):
    """Main entry point from the command line"""
    # Define command line arguments
    p = argparse.ArgumentParser(description=__doc__)
    msg = 'Configuration file to load (default: conf.json)'
    p.add_argument('-c', '--conf', default='conf.json', help=msg)
    msg = 'Process only event with this id'
    p.add_argument('-e', '--eventid', help=msg)
    msg = ('Plot results from given json file (no processing). Can be used '
           'together with -e to plot event results from the given evnt')
    p.add_argument('-p', '--plot', help=msg)
    msg = 'Set chattiness on command line. Up to 3 -v flags are possible'
    p.add_argument('-v', '--verbose', help=msg, action='count',
                   default=SUPPRESS)
    g1 = p.add_argument_group('create example config')
    msg = ('Create example configuration in specified file '
           '(default: conf.json if option is invoked without parameter)')
    g1.add_argument('--create-config', help=msg, nargs='?',
                    const='conf.json', default=SUPPRESS)
    msg = "Only for option '--create-config': Add example data files"
    g1.add_argument('--tutorial', help=msg, action='store_true',
                    default=SUPPRESS)
    msg = ('Use these flags to overwrite values in the config file. '
           'See the example configuration file for a description of '
           'these options')
    g2 = p.add_argument_group('optional codamag arguments', description=msg)
    features = ('events', 'inventory', 'data', 'output')
    for f in features:
        g2.add_argument('--' + f, default=SUPPRESS)
    features = ('plot_energies', 'plot_optimization', 'plot_optresult',
                'plot_eventresult', 'plot_eventsites')
    for f in features:
        g2.add_argument('--' + f.replace('_', '-'), dest=f,
                        action='store_true', default=SUPPRESS)
        g2.add_argument('--no-' + f.replace('_', '-'), dest=f,
                        action='store_false', default=SUPPRESS)
    # Get command line arguments and start main routine
    args = vars(p.parse_args(args))
    try:
        main(**args)
    except ParseError as ex:
        p.error(ex)


if __name__ == '__main__':
    main_cmdline()
