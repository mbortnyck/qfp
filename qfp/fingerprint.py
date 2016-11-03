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

    !! k must remain the same between reference/query
    """
    Reference = [2, 247, 5, 497]
    Query = [500, 985, 8, 497]

class Fingerprint:
    def __init__(self, path, fp_type=fpType.Reference):
        self.path = path
        if fp_type is not fpType.Reference and fp_type is not fpType.Query:
            raise InvalidFpType(
                "Fingerprint must be of type 'Reference' or 'Query'")
        else:
            self.params = fp_type

    def create(self, **kwargs):
        """
        Returns quad hashes for a given audio file
        """
        dbGate = kwargs.pop('dbGate', None)
        snip = kwargs.pop('snip', None)
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

    def store(self, **kwargs):
        """
        Stores fingerprint in database

        To-do:
        1.) store unnormalized quads into quadDB (binary file?)
        2.) fidindex -> 
        3.) reftree = rtree data structure
        4.) refpeaktrees -> two dimensional search trees for spectral peaks
        """
        idx = index.Rtree('rtree')
        for quad_hash in self.hashes:
            idx.insert(quadid, quad_hash)


















