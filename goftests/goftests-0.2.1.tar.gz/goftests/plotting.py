# Copyright (c) 2014, Salesforce.com, Inc.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of Salesforce.com nor the names of its contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from itertools import izip
import numpy
from matplotlib import pyplot
from sklearn.neighbors import NearestNeighbors
from goftests import volume_of_sphere
import parsable


def get_dim(value):
    if isinstance(value, float):
        return 1
    else:
        return len(value)


def get_samples(model, EXAMPLE, sample_count):
    shared = model.Shared.from_dict(EXAMPLE['shared'])
    values = EXAMPLE['values']
    group = model.Group.from_values(shared, values)

    # This version seems to be broken
    # sampler = model.Sampler()
    # sampler.init(shared, group)
    # ...
    # for _ in xrange(sample_count):
    #     value = sampler.eval(shared)

    samples = []
    probs = []
    for _ in xrange(sample_count):
        value = group.sample_value(shared)
        samples.append(value)
        score = group.score_value(shared, value)
        probs.append(score)

    return numpy.array(samples), numpy.array(probs)


def get_edge_stats(samples, probs):
    if not hasattr(samples[0], '__iter__'):
        samples = numpy.array([samples]).T
    neighbors = NearestNeighbors(n_neighbors=2).fit(samples)
    distances, indices = neighbors.kneighbors(samples)
    return {'lengths': distances[:, 1], 'probs': probs}


@parsable.command
def plot_edges(sample_count=1000, seed=0):
    '''
    Plot edges of niw examples.
    '''
    seed_all(seed)
    fig, axes = pyplot.subplots(
        len(niw.EXAMPLES),
        2,
        sharey='row',
        figsize=(8, 12))

    model = niw
    for EXAMPLE, (ax1, ax2) in izip(model.EXAMPLES, axes):
        dim = get_dim(EXAMPLE['shared']['mu'])
        samples, probs = get_samples(model, EXAMPLE, sample_count)
        edges = get_edge_stats(samples, probs)

        edge_lengths = numpy.log(edges['lengths'])
        edge_probs = edges['probs']
        edge_stats = [
            numpy.exp((s - d) / dim)
            for d, s in izip(edge_lengths, edge_probs)
        ]

        ax1.set_title('NIW, dim = {}'.format(dim))
        ax1.scatter(edge_lengths, edge_probs, lw=0, alpha=0.5)
        ax1.set_ylabel('log(edge prob)')

        ax2.scatter(edge_stats, edge_probs, lw=0, alpha=0.5)
        ax2.yaxis.set_label_position('right')

    ax1.set_xlabel('log(edge length)')
    ax2.set_ylabel('statistic')
    fig.tight_layout()
    fig.subplots_adjust(wspace=0)
    pyplot.show()


def cdf_to_pdf(Y, X, bandwidth=0.1):
    assert len(Y) == len(X)
    shift = max(1, int(round(len(Y) * bandwidth)))
    Y = (1.0 / shift) * (Y[shift:] - Y[:-shift])
    X = 0.5 * (X[shift:] + X[:-shift])
    return Y, X


def plot_cdfs(examples):
    '''
    Plot test statistic cdfs based on the Nearest Neighbor distribution.
    '''
    seed_all(seed)

    fig, (ax1, ax2) = pyplot.subplots(2, 1, sharex=True, figsize=(8, 10))
    ax1.plot([0, 1], [0, 1], 'k--')
    ax2.plot([0, 1], [1, 1], 'k--')

    for example in model.examples:
        sample_count = len(example['samples'])
        dim = get_dim(example['samples'][0])
        samples, probs = get_samples(model, EXAMPLE, sample_count)
        edges = get_edge_stats(example['samples'], example['probs'])
        radii = edges['lengths']
        intensities = sample_count * numpy.array(edges['probs'])

        cdf = numpy.array([
            1 - numpy.exp(-intensity * volume_of_sphere(dim, radius))
            for intensity, radius in izip(intensities, radii)
        ])
        cdf.sort()
        X = numpy.arange(0.5 / sample_count, 1, 1.0 / sample_count)

        pdf, Xp = cdf_to_pdf(cdf, X)
        pdf *= sample_count

        error = 2 * (sum(cdf) / sample_count) - 1
        if abs(error) < 0.05:
            status = 'PASS'
            linestyle = '-'
        else:
            status = 'FAIL'
            linestyle = '--'
        label = '{} {}({}) error = {:.3g}'.format(status, name, dim, error)
        ax1.plot(X, cdf, linestyle=linestyle, label=label)
        ax2.plot(Xp, pdf, linestyle=linestyle, label=label)

    ax1.set_title('GOF of Nearest Neighbor Statistic')
    ax1.legend(loc='best', prop={'size': 10}, fancybox=True, framealpha=0.5)
    ax1.set_ylabel('CDF')
    ax2.set_ylabel('PDF')
    pyplot.tight_layout()
    fig.subplots_adjust(hspace=0)
    pyplot.show()


def neighbor_scatter(samples, probs, title='nearest neighbor'):
    '''
    Plot nearest neighbor statistic cdf for all datatpoints in a 2d dataset.
    '''
    sample_count = len(samples)
    assert sample_count
    dim = len(samples[0])
    assert dim == 2, dim

    pyplot.figure()
    cmap = pyplot.get_cmap('bwr')

    edges = get_edge_stats(samples, probs)
    radii = edges['lengths']
    intensities = sample_count * numpy.array(edges['probs'])

    cdf = numpy.array([
        1 - numpy.exp(-intensity * volume_of_sphere(dim, radius))
        for intensity, radius in izip(intensities, radii)
    ])
    error = 2 * (sum(cdf) / sample_count) - 1

    X = [value[0] for value in samples]
    Y = [value[1] for value in samples]
    colors = cdf

    pyplot.title('{} error = {:0.3g}'.format(title, error))
    pyplot.scatter(X, Y, 50, alpha=0.5, c=colors, cmap=cmap)
    pyplot.axis('equal')

    pyplot.tight_layout()
    pyplot.show()
