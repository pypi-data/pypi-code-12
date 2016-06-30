# coding=utf-8
# Author: Tom Richter

# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import numpy as np
import os

from codamag.core import gmean, gerr, get_pair, collect_results


MS = mpl.rcParams['lines.markersize'] // 2

QUANTITIES = ('g0', 'lsc', 'Qsc', 'b', 'li', 'Qi', 'error')
QUANTITIES_EVENT = ('g0', 'lsc', 'Qsc', 'b', 'li', 'Qi', 'error', 'W', 'sds')
QLABELS = {'g0': r'g0 (m$^{-1}$)',
           'lsc': r'l$_{\mathrm{sc}}$ (km)',
           'Qsc': r'Q${_{\mathrm{sc}}}^{-1}$',
           'b': 'b (s$^{-1}$)',
           'li': r'l$_{\mathrm{i}}$ (km)',
           'Qi': r'Q${_{\mathrm{i}}}^{-1}$',
           'W': 'W (J/Hz)',
           'omM': r'$\omega$M (Nm)',
           'sds': r'$\omega$M (Nm)',
           'error': 'error'}

DEPMAP = {'g0': 'g0', 'lsc': 'g0', 'Qsc': 'g0',
          'b': 'b', 'li': 'b', 'Qi': 'b',
          'W': 'W', 'omM': 'omM', 'sds': 'omM', 'error': 'error'}


def calc_dependent(quantity, value, freq=None, v0=None):
    q = quantity
    val = np.array(value, dtype=float)
    if q in ('g0', 'b', 'W', 'omM', 'error'):
        return val
    elif q == 'lsc':
        return 1 / val / 1000
    elif q == 'Qsc':  # actually inverse of Qsc
        return val * v0 / (2 * np.pi * freq)
    elif q == 'li':
        return v0 / val / 1000
    elif q == 'Qi':  # actually inverse of Qi
        return val / (2 * np.pi * freq)


def freqlim(freq):
    return freq[0] ** 1.5 / freq[1] ** 0.5, freq[-1] ** 1.5 / freq[-2] ** 0.5


def savefig(fig, title=None, fname=None, dpi=None):
    if title:
        extra = (fig.suptitle(title),)
    else:
        extra = ()
    if fname:
        path = os.path.dirname(fname)
        if path != '' and not os.path.isdir(path):
            os.makedirs(path)
        plt.savefig(fname, bbox_inches='tight', bbox_extra_artists=extra,
                    dpi=dpi)
        plt.close(fig)


def set_gridlabels(ax, i, n, N, xlabel='frequency (Hz)', ylabel=None):
    if i % n != 0 and ylabel:
        plt.setp(ax.get_yticklabels(), visible=False)
    elif i // n == (n - 1) // 2 and ylabel:
        ax.set_ylabel(ylabel)
    if i < N - n and xlabel:
        plt.setp(ax.get_xticklabels(), visible=False)
    elif i % n == (n - 1) // 2 and i >= N - n - 1 and xlabel:
        ax.set_xlabel(xlabel)


def plot_energies(energies,
                  sonset_window=None, coda_window=None, downsample_to=None,
                  xlim_lin=None, xlim_log=None,
                  figsize=None, **kwargs):
    gs = gridspec.GridSpec(2 * len(energies), 2)
    gs.update(wspace=0.05)
    fig = plt.figure(figsize=figsize)
    sax1 = sax3 = None
    for i, tr in enumerate(energies):
        pair= get_pair(tr)
        otime = tr.stats.origintime
        if downsample_to is None:
            d = 1
        else:
            d = tr.stats.sampling_rate // downsample_to
        ts = np.arange(len(tr)) * tr.stats.delta
        ts = ts - (otime - tr.stats.starttime)
        c = 'k'
        ax2 = plt.subplot(gs[2 * i + 1, 0], sharex=sax1, sharey=sax1)
        ax1 = plt.subplot(gs[2 * i, 0], sharex=ax2)
        ax3 = plt.subplot(gs[2 * i:2 * i + 2, 1], sharex=sax3, sharey=sax3)
        ax1.annotate('%s' % pair[1], (1, 0.5), (-10, 0), 'axes fraction',
                     'offset points', size='small', ha='right', va='center')
        ax3.annotate('%s' % pair[0], (1, 1), (10, -5), 'axes fraction',
                     'offset points', size='small', ha='left', va='top')
        ax1.plot(ts[::d], tr.data[::d], color=c)
        ax2.semilogy(ts[::d], tr.data[::d], color=c)
        ax3.loglog(ts[::d], tr.data[::d], color=c)
        for ax in (ax1, ax2, ax3):
            plt.setp(ax.get_xticklabels(), visible=False)
            ax.set_yticklabels([])
            if 'ponset' in tr.stats:
                tponset = tr.stats.ponset - otime
                ax.axvline(tponset, color='green', alpha=0.5)
            if 'sonset' in tr.stats:
                tsonset = tr.stats.sonset - otime
                ax.axvline(tsonset, color='b', alpha=0.5)
        for ax in (ax2, ax3):
            if sonset_window and coda_window:
                c = ('b', 'k')
                wins = (sonset_window[pair], coda_window[pair])
                for i, win in enumerate(wins):
                    ax.axvspan(win[0] - otime, win[1] - otime,
                               0.05, 0.08, color=c[i], alpha=0.5)

        if sax1 is None:
            sax1 = ax2
            sax3 = ax3
    if xlim_lin:
        ax1.set_xlim(xlim_lin)
    if xlim_log:
        ax3.set_xlim(xlim_log)
    loglocator = mpl.ticker.LogLocator(base=100)
    ax2.yaxis.set_major_locator(loglocator)
    ax3.yaxis.set_major_locator(loglocator)
    ax2.yaxis.set_minor_locator(mpl.ticker.NullLocator())
    ax3.yaxis.set_minor_locator(mpl.ticker.NullLocator())
    plt.setp(ax2.get_xticklabels(), visible=True)
    plt.setp(ax3.get_xticklabels(), visible=True)
    savefig(fig, **kwargs)


def plot_lstsq(ts, Bc, b, tb=None, Bb=None, W=1, R=None,
               ax=None, fname=None, base=np.e):
    fig = None
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    N = len(Bc)
    tmin = min(ts[i][0] for i in range(N))
    tmax = max(ts[i][-1] for i in range(N))
    for i in range(N):
        Bci = Bc[i]
        if R is not None:
            Bci = Bci - np.log(R[i])  # + R0
        ax.plot(ts[i], Bci / np.log(base), color='gray')
        if tb is not None and len(Bb[i]) > 0:
            Bbi = Bb[i][0]
            tbi = tb[i][0]
            if R is not None:
                Bbi = Bbi - np.log(R[i])  # + R0
            ax.plot(tbi, Bbi / np.log(base), 'o', color='gray', mec='gray',
                    ms=MS)
            tmin = min(tmin, tbi)
    t = np.linspace(tmin, tmax, 100)
    ax.plot(t, (np.log(W) - b * t) / np.log(base), color='k')
    ax.set_xlim(right=tmax)
    if fig and fname:
        savefig(fig, fname=fname)


def plot_optimization(record, tc=None, tb=None,
                      num=7, fname=None, title=None):
    fig = plt.figure()
    if num > 1 and tc:
        n = (num + 1) // 2
        gs = gridspec.GridSpec(n, n)
        ax = plt.subplot(gs[1:, 0:-1])
        share = None
    else:
        ax = fig.add_subplot(111)
    if title:
        ax.annotate(title, (0, 1), (5, -5), 'axes fraction', 'offset points',
                    ha='left', va='top')
    g0s = set()
    i = 0
    j = 0
    for g0, err, b, W, R, Bc, Bb in record:
        if g0 in g0s:
            j += 1
            continue
        g0s.add(g0)
        if j == len(record) - 1:
            ax.loglog(g0, err, 'xb')
        else:
            ax.loglog(g0, err, 'xk')

        if num > 1 and (i < num - 1 or j == len(record) - 1) and tc:
            if i < n:
                gsp = gs[0, i]
                l = str(i + 1)
            elif i < num - 1:
                gsp = gs[i - n + 1, -1]
                l = str(i + 1)
            else:
                gsp = gs[n - 1, -1]
                l = 'best'
            ax2 = plt.subplot(gsp, sharex=share, sharey=share)
            plot_lstsq(tc, Bc, b, tb=tb, Bb=Bb, W=W, R=R, ax=ax2)
            ax2.annotate(l, (0, 1), (5, -5), 'axes fraction',
                         'offset points', ha='left', va='top')
            l2 = 'g$_0$=%.1e\nb=%.1e\nW=%.1e' % (g0, b, W)
            ax2.annotate(l2, (1, 1), (-5, -5), 'axes fraction',
                         'offset points', ha='right', va='top',
                         size='xx-small')
            if l != 'best':
                ax.annotate(l, (g0, err), (5, 5), 'data', 'offset points',
                            ha='left', va='bottom')
            if i == 0:
                share = ax2
                yl = (r'$\ln \frac{E_{\mathrm{obs}, ij}}'
                      r'{\mathrm{FS}\ G_{ij}R_i}$')
                ax2.set_ylabel(yl)
                plt.setp(ax2.get_xticklabels(), visible=False)
            elif l == 'best':
                ax2.set_xlabel(r'time ($\mathrm{s}$)')
                plt.setp(ax2.get_yticklabels(), visible=False)
            else:
                plt.setp(ax2.get_xticklabels(), visible=False)
                plt.setp(ax2.get_yticklabels(), visible=False)
        i += 1
        j += 1
    ax2.locator_params(axis='y', nbins=4)
    ax2.locator_params(axis='x', nbins=3)
    ax.set_xlabel(r'g$_0$ ($\mathrm{m}^{-1}$)')
    yl = (r'error $\mathrm{rms}\left(\ln\frac{E_{\mathrm{obs}, ij}}'
          r'{E_{\mathrm{mod}, ij}}\right)$')
    ax.set_ylabel(yl)
    savefig(fig, fname=fname)


def plot_optresult(event_station_pairs, tc, Eobsc, Gc, tb, Eobsb, Gb, b, W, R,
                   fname=None, title=None, distances=None):
    N = len(event_station_pairs)
    n = int(np.ceil(np.sqrt(N)))
    fig = plt.figure()
    gs = gridspec.GridSpec(n, n)
    share = None
    if b is None:
        b = 0
    for i, pair in enumerate(event_station_pairs):
        ax = plt.subplot(gs[i // n, i % n], sharex=share, sharey=share)
        plot = ax.semilogy
        plot(tc[i], np.exp(Eobsc[i]), color='gray')
        plot(tb[i][0], np.exp(Eobsb[i][0]), 'o',
             color='gray', mec='gray', ms=MS)
        Emod = Gc[i] + np.log(W * R[i]) - b * tc[i]
        plot(tc[i], np.exp(Emod), color='k')
        Emod = Gb[i] + np.log(W * R[i]) - b * tb[i][0]
        plot(tb[i][0], np.exp(Emod), 'o', color='k', ms=MS)
        l = '%s\n%s' % pair
        if distances:
            l = l + '\nr=%dkm' % (distances[pair] / 1000)
        ax.annotate(l, (1, 1), (-5, -5), 'axes fraction',
                    'offset points', ha='right', va='top', size='small')
        set_gridlabels(ax, i, n, N, xlabel='time (s)',
                      ylabel=r'E/FS (Jm$^{-3}$Hz$^{-1}$)')
        if share is None:
            share = ax
    ax.locator_params(axis='x', nbins=5, prune='upper')
    loglocator = mpl.ticker.LogLocator(base=100)
    ax.yaxis.set_major_locator(loglocator)
    ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())
    ax.autoscale()
    ax.set_xlim(left=0)
    savefig(fig, fname=fname, title=title)


def plot_sds(freq, omM, M0=None, M0_freq=None, ax=None, fname=None):
    freq = np.array(freq)
    omM = np.array(omM)
    fig = None
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    if M0_freq:
        ax.loglog(freq, omM, 'o-', color='gray', mec='gray')
        ax.loglog(freq[freq < M0_freq], omM[freq < M0_freq], 'o-k')
    else:
        ax.loglog(freq, omM, 'o-k')
    if M0:
        ax.axhline(M0, ls='--', color='k')
    if fig and fname:
        savefig(fig, fname=fname)


def plot_eventresult(result, v0=None, fname=None, title=None, M0_freq=None,
                     quantities=QUANTITIES_EVENT):
    freq = np.array(result['freq'])
    N = len(quantities)
    n = int(np.ceil(np.sqrt(N)))
    fig = plt.figure()
    gs = gridspec.GridSpec(n, n)
    share = None
    for i, q in enumerate(quantities):
        ax = plt.subplot(gs[i // n, i % n], sharex=share)
        if q == 'sds':
            plot_sds(freq, result['omM'], M0=result.get('M0'),
                     M0_freq=M0_freq, ax=ax)
        else:
            vals = calc_dependent(q, result[DEPMAP[q]], freq, v0)
            ax.loglog(freq, vals, 'o-k')
        ax.annotate(QLABELS[q], (1, 1), (-5, -5), 'axes fraction',
                    'offset points', ha='right', va='top')
        set_gridlabels(ax, i, n, N)
        if share is None:
            share = ax
    ax.set_xlim(freq[0], freq[-1])
    savefig(fig, fname=fname, title=title)


def plot_eventsites(result, fname=None, title=None):
    freq = np.array(result['freq'])
    R = result['R']
    N = len(R)
    n = int(np.ceil(np.sqrt(N)))
    fig = plt.figure()
    gs = gridspec.GridSpec(n, n)
    share = None
    allR = []
    for i, station in enumerate(sorted(R)):
        allR.extend(R[station])
        ax = plt.subplot(gs[i // n, i % n], sharex=share, sharey=share)
        ax.loglog(freq, np.array(R[station], dtype=np.float), 'o-k')
        l = station
        ax.annotate(l, (1, 1), (-5, -5), 'axes fraction',
                    'offset points', ha='right', va='top', size='small')
        set_gridlabels(ax, i, n, N, ylabel='site correction')
        if share is None:
            share = ax
    allR = np.array(allR, dtype=np.float)
    allR = allR[~np.isnan(allR)]
    if np.min(allR) != np.max(allR):
        ax.set_ylim(np.min(allR), np.max(allR))
    ax.set_xlim(freq[0], freq[-1])
    savefig(fig, fname=fname, title=title)


def plot_results(result, v0=None, fname=None, title=None,
                 quantities=QUANTITIES, fstd=1):
    freq = np.array(result['freq'])
    N = len(quantities)
    n = int(np.ceil(np.sqrt(N)))
    fig = plt.figure()
    gs = gridspec.GridSpec(n, n)
    share = None
    if v0 is None:
        v0 = result['config']['v0']
    g0, b, error, R = collect_results(result['events'])
    result = {'g0': g0, 'b': b, 'error': error, 'R': R}
    for i, q in enumerate(quantities):
        value = result[DEPMAP[q]]
        value = calc_dependent(q, value, freq, v0)
        means = gmean(value, axis=0)
        errs = gerr(value, axis=0)
        ax = plt.subplot(gs[i // n, i % n], sharex=share)
        freqs = np.repeat(freq[np.newaxis, :], value.shape[0], axis=0)
        ax.loglog(freqs, value, 'o', ms=MS, color='gray', mec='gray')
        ax.errorbar(freq, means, yerr=errs, marker='o',
                    mfc='k', mec='k', color='m', ecolor='m')
        ax.annotate(QLABELS[q], (1, 1), (-5, -5), 'axes fraction',
                    'offset points', ha='right', va='top')
        set_gridlabels(ax, i, n, N, ylabel=None)
        if share is None:
            share = ax
    ax.set_xlim(freqlim(freq))
    savefig(fig, fname=fname, title=title)


def plot_sites(result, fname=None, title=None, ylim=(1e-2, 1e2)):
    freq = np.array(result['freq'])
    g0, b, error, R = collect_results(result['events'])
    N = len(R)
    n = int(np.ceil(np.sqrt(N)))
    fig = plt.figure()
    gs = gridspec.GridSpec(n, n)
    share = None
    for i, station in enumerate(sorted(R)):
        ax = plt.subplot(gs[i // n, i % n], sharex=share, sharey=share)
        means = gmean(R[station], axis=0)
        errs = gerr(R[station], axis=0)
        freqs = np.repeat(freq[np.newaxis, :], R[station].shape[0], axis=0)
        ax.loglog(freqs, R[station], 'o', ms=MS, color='gray', mec='gray')
        ax.errorbar(freq, means, yerr=errs, marker='o', ms=MS,
                    mfc='k', mec='k', color='m', ecolor='m')
        ax.annotate(station, (1, 1), (-5, -5), 'axes fraction',
                    'offset points', ha='right', va='top', size='x-small')
        set_gridlabels(ax, i, n, N, ylabel='amplification factor')
        if share is None:
            share = ax
    ax.set_xlim(freqlim(freq))
    if ylim:
        ax.set_ylim(ylim)
    savefig(fig, fname=fname, title=title)


def plot_all_sds(result, M0_freq=None, fname=None, title=None, ylim=None):
    freq = np.array(result['freq'])
    if M0_freq is None:
        M0_freq = result.get('config', {}).get('M0_freq')
        from collections import OrderedDict
    result = result['events']
    N = len(result)
    n = int(np.ceil(np.sqrt(N)))
    fig = plt.figure()
    gs = gridspec.GridSpec(n, n)
    share = None
    for i, eventid in enumerate(sorted(result)):
        ax = plt.subplot(gs[i // n, i % n], sharex=share, sharey=share)
        plot_sds(freq, result[eventid]['omM'], M0=result[eventid].get('M0'),
                 M0_freq=M0_freq, ax=ax)
        ax.annotate(eventid, (0, 0), (5, 5), 'axes fraction',
                    'offset points', ha='left', va='bottom', size='x-small')
        set_gridlabels(ax, i, n, N, ylabel=r'$\omega$M (Nm)')
        if share is None:
            share = ax
    ax.autoscale()
    ax.set_xlim(ax.set_xlim(freqlim(freq)))
    if ylim:
        ax.set_ylim(ylim)
    savefig(fig, fname=fname, title=title)


def plot_mags(result, fname=None, title=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    Mcat, Mw = zip(*[(r['Mcat'], r['Mw']) for r in result['events'].values()
                     if r.get('Mcat') is not None and r.get('Mw') is not None])
    ax.plot(Mcat, Mw, 'ok', ms=MS)
    ax.set_xlabel('M from catalog')
    ax.set_ylabel('Mw from coda')
    savefig(fig, fname=fname, title=title)
