import unittest
import os
from functools import partial

from qfp import fingerprint
from qfp.audio import (
    load_audio
)
from qfp.utils import (
    stft,
    find_peaks
)
from qfp.exceptions import (
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)
from pydub import AudioSegment

dataDir = os.path.join(os.path.dirname(__file__), 'data')

class FingerprintTestCase(unittest.TestCase):
    def test_insufficient_audio_length(self):
        self.path = os.path.join(dataDir, 'short_audio_sample.mp3')
        self.assertRaises(InvalidAudioLength, fingerprint, self.path, k=497)
    def test_insufficient_peaks_found(self):
        self.path = os.path.join(dataDir, 'silence.mp3')
        self.assertRaises(TooFewPeaks, fingerprint, self.path, k=497)
    def test_no_quads_found(self):
        self.path = os.path.join(dataDir, 'few_peaks.mp3')
        self.assertRaises(NoQuadsFound, fingerprint, self.path, k=497, dbGate=220)

if __name__ == "__main__":
    unittest.main()