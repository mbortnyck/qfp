import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.filters import maximum_filter, minimum_filter

def stft(samples, framesize=1024, hopsize=128):
    """
    Short time fourier transform of audio
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

def find_peaks(spec, dbGate=None, maxWidth=91, maxHeight=65, minWidth=3, minHeight=3):
    """
    Calculate peaks of spectrogram using maximum filter
    Local minima used to filter out uniform areas (e.g. silence)
    Returns list of tuples
    """
    if dbGate is not None:
        spec[spec < dbGate] = 0
    maxFilterDimen = (maxWidth, maxHeight)
    minFilterDimen = (minWidth, minHeight)
    maxima = maximum_filter(spec, footprint=np.ones(maxFilterDimen, dtype=np.int8))
    minima = minimum_filter(spec, footprint=np.ones(minFilterDimen, dtype=np.int8))
    peaks = ((spec == maxima) == (maxima != minima))
    x, y = np.nonzero(peaks)
    positions = zip(x, y)
    return positions

def quad_hash(quad):
    """
    Compute translation- and scale-invariant hash from a given quad
    """
    hashed = ()
    A = quad[0]
    D = quad[3]
    for point in quad[1:3]:
        xDash = (point[0] - A[0]) * (1.0 / (D[0] - A[0]))
        yDash = (point[1] - A[1]) * (1.0 / (D[1] - A[1]))
        hashed += (xDash, yDash)
    return [hashed]