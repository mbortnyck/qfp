from __future__ import division

from .audio import load_audio
from .utils import stft, find_peaks
from .quads import root_quads, quad_hash

from .exceptions import (
    InvalidFpType,
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)

class fpType:
    """
    Parameters for reference/query fingerprint types
    Presented in order [q, r, n, k]

    q = quads to create per root point (A)
    r = width of search window
    n = number of points to combinations from
    k = distance from root point to position window

    !! k must remain the same between reference/query
    """
    Reference = [2, 247, 5, 497]
    Query = [500, 985, 8, 497]

class Fingerprint:
    def __init__(self, path, fp_type):
        self.path = path
        if fp_type is not fpType.Reference and fp_type is not fpType.Query:
            raise TypeError("Fingerprint must be of type 'Reference' or 'Query'")
        else:
            self.params = fp_type

    def create(self, snip=None, dbGate=None):
        """
        Returns quad hashes for a given audio file
        """
        q, r, n, k = self.params
        samples = load_audio(self.path, snip=snip)
        self.spectrogram = stft(samples)
        if len(self.spectrogram) <= k:
            raise InvalidAudioLength(
                "'{file}' did not produce spectrogram of "
                "sufficient length for k value provided".format(file=self.path))
        self.peaks = list(find_peaks(self.spectrogram, dbGate=dbGate))
        if len(self.peaks) < 4:
            raise TooFewPeaks(
                "'{file}' contains too few peaks to form quads".format(file=self.path))
        self.quads = []
        for root in self.peaks:
            self.quads += root_quads(root, self.peaks, q, r, n, k)
        if len(self.quads) is 0:
            raise NoQuadsFound(
                "'{file}' produced no quads".format(file=self.path))
        self.hashes = []
        for quad in self.quads:
            self.hashes += quad_hash(quad)

class ReferenceFingerprint(Fingerprint):
    def __init__(self, path):
        Fingerprint.__init__(self, path, fp_type=fpType.Reference)

class QueryFingerprint(Fingerprint):
    epsilon = .008

    def __init__(self, path):
        Fingerprint.__init__(self, path, fp_type=fpType.Query)

    def create(self):
        Fingerprint.create(self, snip=15)
















