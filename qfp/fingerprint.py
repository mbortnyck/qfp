from __future__ import division

from .audio import load_audio
from .utils import stft, find_peaks
from .quads import root_quads, quad_hash
from .storage import bulk_load

from .exceptions import (
    InvalidFpType,
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)

from rtree import index
from rtree.core import RTreeError

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
    idx = None

    def __init__(self, path, fp_type):
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

class ReferenceFingerprint(Fingerprint):
    def __init__(self, path):
        Fingerprint.__init__(self, path, fp_type=fpType.Reference)

    def create_and_store(self):
        self.create()
        self.store()

    def store(self, **kwargs):
        """
        Stores fingerprint in database

        To-do:
        1.) store unnormalized quads into quadDB (binary file?)
        2.) fidindex -> 
        3.) reftree = rtree data structure
        4.) refpeaktrees -> two dimensional search trees for spectral peaks
        """
        Fingerprint.idx = index.Index('rtree', bulk_load(self.hashes))

class QueryFingerprint(Fingerprint):
    epsilon = .008

    def __init__(self, path):
        Fingerprint.__init__(self, path, fp_type=fpType.Query)

    def create_and_lookup(self):
        self.create()
        self.lookup()

    def create(self):
        Fingerprint.create(self, snip=15)

    def lookup(self, **kwargs):
        for h in self.hashes:
            mini = (h[0]+self.epsilon, h[1]+self.epsilon, \
                    h[2]-self.epsilon, h[3]-self.epsilon)
            maxi = (h[0]-self.epsilon, h[1]-self.epsilon, \
                    h[2]+self.epsilon, h[3]+self.epsilon)
            # if bounds in original hash are closer than epsilon apart
            # coordinates of minimum bounds will "flip" and be invalid
            # until I can find a better solution, if only one (x or y) overlaps,
            # lookup will be skipped
            xcondition = ((mini[2] - mini[0]) <= 0)
            ycondition = ((mini[3] - mini[1]) <= 0)
            if xcondition and ycondition:
                results = set(Fingerprint.idx.intersection(maxi))
            elif xcondition:
                continue
            elif ycondition:
                continue
            else:
                maxi_hits = set(Fingerprint.idx.intersection(maxi))
                mini_hits = set(Fingerprint.idx.intersection(mini))
                results = maxi_hits - mini_hits
            print len(results)
















