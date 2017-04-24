import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.filters import maximum_filter, minimum_filter

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
    """if dbGate is not None:
        spec[spec < dbGate] = 0"""
    maxFilterDimen = (maxWidth, maxHeight)
    minFilterDimen = (minWidth, minHeight)
    maxima = maximum_filter(spec, footprint=np.ones(maxFilterDimen, dtype=np.int8))
    minima = minimum_filter(spec, footprint=np.ones(minFilterDimen, dtype=np.int8))
    peaks = ((spec == maxima) == (maxima != minima))
    # todo: parabolic interpolation
    x, y = np.nonzero(peaks)
    positions = zip(x, y)
    return positions

def partition_quads(quads):
    last_x = quads[-1][0][0]
    num_partitions = last_x // 250
    for i in xrange(num_partitions):
        partitions.append(bisect_left(quads, ))