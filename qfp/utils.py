from __future__ import division

import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.filters import maximum_filter, minimum_filter
from bisect import bisect_left
from heapq import nlargest

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
    frames = stride_tricks.as_strided(samples, \
               shape=(cols, framesize), \
               strides=(samples.strides[0]*hopsize, samples.strides[0])).copy()
    frames *= window
    spec = np.fft.rfft(frames)
    with np.errstate(divide='ignore'): # silences "divide by zero" error
        spec = 20.*np.log10(np.abs(spec)/10e-6) # amplitude to decibel
    spec[spec == -np.inf] = 0
    return spec

def find_peaks(spec, maxWidth, maxHeight, minWidth=3, minHeight=3):
    """
    Calculate peaks of spectrogram using maximum filter
    Local minima used to filter out uniform areas (e.g. silence)
    Returns: list of int8 tuples of form (x, y)
    """
    maxFilterDimen = (maxWidth, maxHeight)
    minFilterDimen = (minWidth, minHeight)
    maxima = maximum_filter(spec, footprint=np.ones(maxFilterDimen, dtype=np.int8))
    minima = minimum_filter(spec, footprint=np.ones(minFilterDimen, dtype=np.int8))
    peaks = ((spec == maxima) == (maxima != minima))
    # todo: parabolic interpolation
    x, y = np.nonzero(peaks)
    positions = zip(x, y)
    return positions

def n_strongest(spec, quads, n):
    """
    Returns list of 9 strongest quads in each 1 second partition
    Strongest is calculated by magnitudes of C and D in quad
    """
    strongest = []
    partitions = _find_partitions(quads)
    key = lambda x: (spec[x[1][0]][x[1][1]] + spec[x[2][0]][x[2][1]])
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
    last_x = quads[-1][0][0]
    num_partitions = last_x // l
    partitions = [b_l(quads, [(i * l, None)]) for i in xrange(num_partitions)]
    partitions.append(len(quads))
    return partitions

def generate_hash(quad):
    """
    Compute translation- and scale-invariant hash from a given quad
    """
    A, C, D, B = quad
    B = (B[0] - A[0], B[1] - A[1])
    C = (C[0] - A[0], C[1] - A[1])
    D = (D[0] - A[0], D[1] - A[1])
    cDash = (C[0] / B[0], C[1] / B[1])
    dDash = (D[0] / B[0], D[1] / B[1])
    return cDash + dDash