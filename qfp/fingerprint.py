from __future__ import division

from .audio import load_audio
from .utils import stft, find_peaks, quad_hash
from .quads import root_quads

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

    !! k must remain the same between reference/query !!
    """
    Reference = [2, 247, 5, 497]
    Query = [500, 985, 8, 497]

class Fingerprint:
    def __init__(self, path, fp_type=fpType.Reference):
        self.path = path
        if fp_type is fpType.Reference:
            self.params = fp_type
        elif fp_type is fpType.Query:
            self.params = fp_type
        else:
            raise InvalidFpType(
                "Fingerprint must be type 'Reference' or 'Query'")

    def create(self, dbGate=150):
        """
        Returns quad hashes for a given audio file
        """
        q, r, n, k = self.params
        samples = load_audio(self.path)
        spectrogram = stft(samples)
        if len(spectrogram) <= k:
            raise InvalidAudioLength(
                "'{file}' did not produce spectrogram of "
                "sufficient length for k value provided".format(file=self.path))
        peaks = list(find_peaks(spectrogram, dbGate=dbGate))
        if len(peaks) < 4:
            raise TooFewPeaks(
                "'{file}' contains too few peaks to form quads".format(file=self.path))
        self.quads = []
        for root in peaks:
            self.quads += root_quads(root, peaks, q, r, n, k)
        if len(self.quads) is 0:
            raise NoQuadsFound(
                "'{file}' produced no quads".format(file=self.path))
        self.hashes = []
        for quad in self.quads:
            self.hashes += quad_hash(quad)