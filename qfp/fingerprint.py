from .audio import load_audio
from .utils import stft, find_peaks, quad_hash
from .quads import root_quads

def fingerprint(path):
    samples = load_audio(path)
    spec = stft(samples)
    peaks = find_peaks(spec)
    quads = []
    for root in peaks:
        quads += root_quads(root, peaks, 2, 247, 5)
    hashes = []
    for quad in quads:
        hashes += quad_hash(quad)
    return hashes