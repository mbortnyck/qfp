from .audio import load_audio
from .utils import stft, find_peaks, quad_hash
from .quads import root_quads

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
    spec = stft(samples)
    # to-do: should check if spectrogram is sufficient
    # lenth for fingerprinting here
    peaks = find_peaks(spec)
    # raise exception if no peaks found
    quads = []
    for root in peaks:
        quads += root_quads(root, peaks, q, r, n, k)
    # raise exception if no quads found
    hashes = []
    for quad in quads:
        hashes += quad_hash(quad)
    return hashes