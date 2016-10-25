from .audio import load_audio
from .utils import stft, find_peaks, quad_hash
from .quads import root_quads

from .exceptions import (
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)

class fpType:
    Reference, Query = range(1, 3)

class Fingerprint:
    def __init__(self, path, fp_type=fpType.Reference):
        self.path = path
        if fp_type is fpType.Reference:
            self.q = 2
            self.r = 247
            self.n = 5
            self.k = 497
        elif fp_type is fpType.Query:
            self.q = 500
            self.r = 985
            self.n = 8
            self.k = 497

    def create(self, dbGate=150):
        """
        Returns quad hashes for a given audio file
        """
        samples = load_audio(self.path)
        spectrogram = stft(samples)
        if len(spectrogram) <= self.k:
            raise InvalidAudioLength(
                "'{file}' did not produce spectrogram of "
                "sufficient length for k value provided".format(file=self.path))
        peaks = find_peaks(spectrogram, dbGate=dbGate)
        if len(peaks) < 4:
            raise TooFewPeaks(
                "'{file}' contains too few peaks to form quads".format(file=self.path))
        quads = []
        for root in peaks:
            quads += root_quads(root, peaks, self.q, self.r, self.n, self.k)
        if len(quads) is 0:
            raise NoQuadsFound(
                "'{file}' produced no quads".format(file=self.path))
        hashes = []
        for quad in quads:
            hashes += quad_hash(quad)
        return hashes