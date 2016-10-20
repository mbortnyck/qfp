import itertools
import numpy as np
from numpy.lib import stride_tricks
from scipy.ndimage.filters import maximum_filter, minimum_filter
from pydub import AudioSegment

def _load(path, downsample=True, normalize=True, snip=None):
    """
    Creates array of samples from input audio file
    snip = only return first n seconds of input
    """
    audio = AudioSegment.from_file(path)
    if downsample:
        # downsample if stereo, sample rate > 16kHz, or > 16-bit depth
        if (audio.channels > 1) \
          or (audio.frame_rate != 16000) \
          or (audio.sample_width != 2):
            audio = _downsample(audio)
    if normalize:
        audio = _normalize(audio)
    if snip is not None:
        milliseconds = snip * 1000
        audio = audio[:milliseconds]
    return audio.get_array_of_samples()

def _downsample(audio, numChannels=1, sampleRate=16000, bitDepth=2):
    """
    Downsamples audio to monoaural, 16kHz sample rate, 16-bit depth
    """
    audio = audio.set_channels(numChannels)
    audio = audio.set_frame_rate(sampleRate)
    audio = audio.set_sample_width(bitDepth)
    return audio

def _normalize(audio, target_dBFS=-20.0):
    """
    Normalizes loudness of audio segment
    """
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)

def _stft(samples, framesize=1024, hopsize=128):
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
    spec[spec == -np.inf] = 0 # infinite values to zero
    return spec

def _peaks(spec, maxWidth=91, maxHeight=65, minWidth=3, minHeight=3):
    """
    Calculate peaks of spectrogram using maximum filter
    Local minima used to filter out uniform areas (e.g. silence)
    Returns list of tuples
    """
    maxFilterDimen = (maxWidth, maxHeight)
    minFilterDimen = (minWidth, minHeight)
    maxima = maximum_filter(spec, footprint=np.ones(maxFilterDimen, dtype=np.int8))
    minima = minimum_filter(spec, footprint=np.ones(minFilterDimen, dtype=np.int8))
    peaks = ((spec == maxima) == (maxima != minima))
    x, y = np.nonzero(peaks)
    positions = zip(x, y)
    return positions

def _create_quads(peaks, q, r, n, k=497):
    """
    finds valid quads for each peak
    k should be same between ref/query
    r and n should be smaller for ref, larger for query
    
    Suggested values for reference/quad parameters:
        Ref   Q = 2
              R = 247
              N = 5
        Query Q = 500
              R = 985
              N = 8
    """
    quads = []
    endOfTrack = peaks[-1][0]
    for A in peaks:
        windowStart = A[0] + k - (r / 2)
        if windowStart > endOfTrack:
            break
        windowEnd = windowStart + r
        filtered = [x for x in peaks if x[0] >= windowStart and x[0] <= windowEnd]
        if filtered is None:
            continue
        offset = 0
        validQuads = []
        while (len(validQuads) < q) and (offset + n < len(filtered)): # check boundaries
            take = filtered[offset : offset + n]
            combs = list(itertools.combinations(take, 3))
            for comb in combs:
                # note that B is defined as point farthest from A
                B, C, D = (comb[2], comb[0], comb[1])
                if _validate_quad(A, B, C, D, validQuads):
                    validQuads += [[A, B, C, D]]
                if len(validQuads) >= q:
                    break
            offset += 1
        if validQuads:
            quads += validQuads
    return quads

def _validate_quad(A, B, C, D, quads):
    """
    evaluates:
          Ax < Bx
          Ay < By
      Ax < Cx,Dx <= Bx
      Ay < Cy,Dy <= By

    then checks if quad is a duplicate
    assumes list of combinations is sorted
    """
    if A[0] is B[0] or A[0] is C[0]:
        return False
    elif A[1] >= B[1] or A[1] >= C[1] or A[1] >= D[1]:
        return False
    elif C[1] > B[1] or D[1] > B[1]:
        return False
    for quad in quads:
        if [A, B, C, D] == quad:
            return False
    return True

def _hash(quad):
    hashed = ()
    A = quad[0]
    B = quad[1]
    for point in quad[2:4]:
        xDash = (point[0] - A[0]) * (1.0 / (B[0] - A[0]))
        yDash = (point[1] - A[1]) * (1.0 / (B[1] - A[1]))
        hashed += (xDash, yDash)
    return [hashed]

def fingerprint(path):
    samples = _load(path)
    spec = _stft(samples)
    peaks = _peaks(spec)
    quads = _create_quads(peaks, 2, 247, 5)
    hashes = []
    for quad in quads:
        hashes += _hash(quad)
    return hashes