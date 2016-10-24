from .audio import load_audio
from .utils import stft, find_peaks, quad_hash
from .quads import root_quads

from .exceptions import (
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)

def fingerprint(path, q=2, r=247, n=5, k=497):
    """
    Returns quad hashes for a given audio file
    k should remain same between reference/query

    Suggested values for reference/quad parameters:
        Ref   Q = 2
              R = 247
              N = 5
        Query Q = 500
              R = 985
              N = 8
    """
    samples = load_audio(path)
    spectrogram = stft(samples)
    # to-do: should check if spectrogram is sufficient
    # lenth for fingerprinting here
    if len(spectrogram) < k:
        raise InvalidAudioLength(
            "'{file}' did not produce spectrogram of sufficient length for k value provided".format(file = path))
    peaks = find_peaks(spectrogram)
    if len(peaks) < 4:
        raise TooFewPeaks(
            "'{file}' contains too few peaks to form quads".format(file = path))
    quads = []
    for root in peaks:
        quads += root_quads(root, peaks, q, r, n, k)
    if len(quads) is 0:
        raise NoQuadsFound(
            "'{file}' produces no quads".format(file = path))
    hashes = []
    for quad in quads:
        hashes += quad_hash(quad)
    return hashes