from .audio import load_audio
from .utils import stft, peaks, quad_hash
from .quads import quads

def fingerprint(path):
    samples = load_audio(path)
    spec = stft(samples)
    peaks = peaks(spec)
    quads = []
    for root in peaks:
        quads += quads(root, peaks, 2, 247, 5)
    hashes = []
    for quad in quads:
        hashes += quad_hash(quad)
    return hashes