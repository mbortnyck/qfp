import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.morphology import generate_binary_structure, iterate_structure
from scipy.ndimage.filters import maximum_filter, minimum_filter
from pydub import AudioSegment
from multiprocessing import Pool

def _load(path, normalize=True, snip=None):
    """
    Creates array of samples from input audio file
    snip = only return first n seconds of input
    """
    audio = AudioSegment.from_file(path)
    # downsample if stereo, sample rate > 16kHz, or > 16-bit depth
    if (audio.channels > 1) \
    or (audio.frame_rate != 16000) \
    or (audio.sample_width != 2):
        audio = _downsample(audio)
    if normalize:
        audio = _normalize(audio)
    if snip is not None:
        audio = audio[:(snip * 1000)]
    return audio.get_array_of_samples()

def _downsample(audio):
    """
    Downsamples audio to monoaural, 16kHz sample rate, 16-bit depth
    Values defined by QFP paper
    """
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio = audio.set_sample_width(2)
    return audio

def _normalize(audio, target_dBFS=-20.0):
    """
    Normalizes loudness of audio segment
    """
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)

def _stft(samples):
    """
    Short time fourier transform of audio
    """
    framesize = 1024 # defined in QFP paper
    hopsize = 128    # also defined
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
    spec[spec == -np.inf] = 0 # infinite values to zero
    return spec

def _peaks(spec):
    """
    Calculate peaks of spectrogram using maximum filter
    Local minima used to filter out uniform areas (e.g. silence)
    """
    maxFilterDimen = (91, 65)
    minFilterDimen = (3, 3)
    maxima = maximum_filter(spec, footprint=np.ones(maxFilterDimen, dtype=np.int8))
    minima = minimum_filter(spec, footprint=np.ones(minFilterDimen, dtype=np.int8))
    peaks = ((spec == maxima) == (maxima != minima)).astype(int)
    return peaks

def _pos(peaks):
    """
    Returns list of peak positions
    """
    list = []
    for i in range(len(peaks)):
        for j in range(len(peaks[0])):
            if peaks[i][j] == 1:
                list.append((i, j))
    return list

def _quads(peaks, r, n, k=10):
    """
    finds valid quads of a given set of peak positions
    k should be same between ref/query
    r and n should be smaller for ref, larger for query [1]
    """
    rate = 124
    i = 0
    while len(quads) < n:
        a = peaks[i]
        i += 1
    return quads

def fingerprint(path):
    samples = _load(path)
    spec = _stft(samples)
    peaks = _peaks(spec)
    pos = _pos(peaks)
    #quads = _quads(pos)
    return pos

def test(path):
    peaks = _peaks(_stft(_load(path, snip=15)))
    return peaks
