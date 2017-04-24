from __future__ import division

from .audio import load_audio
from .utils import stft, find_peaks
from .quads import find_quads, generate_hash

class fpType:
    """
    Parameters for reference/query fingerprint types
    Presented in order [q, r, c, w, h]

    q = quads to create per root point (A)
    r = width of search window
    c = distance from root point to position window
    w = width of max filter
    h = height of max filter
    
    based on stft hop-size of 32 samples (4ms):
    ref.r = 800ms / 4ms = 200
    ref.c = 1375ms / 4ms = ~345
    que.r = 1300ms / 4ms = 325
    que.c = 1437.5ms / 4ms = ~360

    query filter height/width are calculated as:
    query.w = ref.w / (1 + .2) = 125
    query.h = ref.h * (1 - .2) = 60

    reference width changed from 151 to 150 so that
    result is an int for epsilon of .2 (20% change in speed/tempo)
    """
    Reference = [9, 200, 325, 150, 75]
    Query = [500, 345, 360, 125, 60]

class Fingerprint:
    def __init__(self, path, fp_type):
        self.path = path
        if fp_type is not fpType.Reference and fp_type is not fpType.Query:
            raise TypeError("Fingerprint must be of type 'Reference' or 'Query'")
        else:
            self.params = fp_type
    def create(self, snip=None):
        """
        Returns quad hashes for a given audio file
        """
        q, r, c, w, h = self.params
        samples = load_audio(self.path, snip=snip)
        self.spectrogram = stft(samples)
        """if len(self.spectrogram) <= k:
            raise InvalidAudioLength(
                "'{file}' did not produce spectrogram of "
                "sufficient length for c value provided".format(file=self.path))"""
        self.peaks = list(find_peaks(self.spectrogram, w, h))
        """if len(self.peaks) < 4:
            raise TooFewPeaks(
                "'{file}' contains too few peaks to form quads".format(file=self.path))"""
        self.quads = find_quads(self.peaks, r, c)
        """if len(self.quads) is 0:
            raise NoQuadsFound(
                "'{file}' produced no quads".format(file=self.path))"""
        self.hashes = []
        for quad in self.quads:
            self.hashes += generate_hash(quad)

class ReferenceFingerprint(Fingerprint):
    def __init__(self, path):
        Fingerprint.__init__(self, path, fp_type=fpType.Reference)

class QueryFingerprint(Fingerprint):
    def __init__(self, path):
        Fingerprint.__init__(self, path, fp_type=fpType.Query)
    def create(self):
        Fingerprint.create(self, snip=15)