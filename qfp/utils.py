from __future__ import division

import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.filters import maximum_filter, minimum_filter
from bisect import bisect_left
from collections import namedtuple
from heapq import nlargest

try:
    from itertools import izip
except ImportError:  # python 3.x
    izip = zip
    xrange = range


def stft(samples, framesize=1024, hopsize=32):
    """
    Short time fourier transform of audio
    Framesize of 1024 samples (128ms) and
    Hopsize of 32 samples (4ms) as per Sonnleitner/Widmer paper
    Returns: 2D numpy array of float64 values
    """
    window = np.hanning(framesize)
    samples = np.append(np.zeros(int(framesize / 2)), samples)
    cols = int(np.ceil((len(samples) - framesize) / float(hopsize)) + 1)
    samples = np.append(samples, np.zeros(framesize))
    strides = (samples.strides[0] * hopsize, samples.strides[0])
    frames = stride_tricks.as_strided(samples,
                                      shape=(cols, framesize),
                                      strides=strides).copy()
    frames *= window
    spec = np.fft.rfft(frames)
    with np.errstate(divide='ignore'):  # silences "divide by zero" error
        spec = 20. * np.log10(np.abs(spec) / 10e-6)  # amplitude to decibel
    spec[spec == -np.inf] = 0
    return spec


def find_peaks(spec, maxWidth, maxHeight, minWidth=3, minHeight=3):
    """
    Calculate peaks of spectrogram using maximum filter
    Local minima used to filter out uniform areas (e.g. silence)
    Returns: list of namedtuple Peaks
    """
    Peak = namedtuple('Peak', ['x', 'y'])
    maxFilterDimen = (maxWidth, maxHeight)
    minFilterDimen = (minWidth, minHeight)
    maxima = maximum_filter(spec, footprint=np.ones(
        maxFilterDimen, dtype=np.int8))
    minima = minimum_filter(spec, footprint=np.ones(
        minFilterDimen, dtype=np.int8))
    peaks = ((spec == maxima) == (maxima != minima))
    # todo: parabolic interpolation
    x, y = np.nonzero(peaks)
    namedpeaks = [Peak(p[0], p[1]) for p in izip(x, y)]
    return namedpeaks


def n_strongest(spec, quads, n):
    """
    Returns list of n strongest quads in each 1 second partition
    Strongest is calculated by magnitudes of C and D in quad
    """
    strongest = []
    partitions = _find_partitions(quads)
    key = lambda p: (spec[p.C.x][p.C.y] + spec[p.D.x][p.D.y])
    for i in xrange(1, len(partitions)):
        start = partitions[i - 1]
        end = partitions[i]
        strongest += nlargest(n, quads[start:end], key)
    return strongest


def _find_partitions(quads, l=250):
    """
    Returns list of indices where partitions of 250 (1 second) are
    """
    b_l = bisect_left
    last_x = quads[-1].A.x
    num_partitions = last_x // l
    # creates a tuple of same form as the Quad namedtuple for bisecting
    q = lambda x: ((x,), (), (), ())
    partitions = [b_l(quads, q(i * l)) for i in xrange(num_partitions)]
    partitions.append(len(quads))
    return partitions


def generate_hash(quad):
    """
    Compute translation- and scale-invariant hash from a given quad
    """
    A, C, D, B = quad
    B = (B.x - A.x, B.y - A.y)
    C = (C.x - A.x, C.y - A.y)
    D = (D.x - A.x, D.y - A.y)
    cDash = (C[0] / B[0], C[1] / B[1])
    dDash = (D[0] / B[0], D[1] / B[1])
    return cDash + dDash
