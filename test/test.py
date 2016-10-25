import unittest
import os

from qfp import Fingerprint

from qfp.exceptions import (
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)

dataDir = os.path.join(os.path.dirname(__file__), 'data')

class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.ins_audio_length_path = os.path.join(dataDir, 'short_audio_sample.mp3')
        self.ins_peaks_path = os.path.join(dataDir, 'silence.mp3')
        self.no_quads_path = os.path.join(dataDir, 'few_peaks.mp3')
    def test_InvalidAudioLength(self):
        ins_audio_length_fp = Fingerprint(self.ins_audio_length_path)
        self.assertRaises(InvalidAudioLength, ins_audio_length_fp.create)
    def test_TooFewPeaks(self):
        ins_peaks_fp = Fingerprint(self.ins_peaks_path)
        self.assertRaises(TooFewPeaks, ins_peaks_fp.create)
    def test_NoQuadsFound(self):
        no_quads_fp = Fingerprint(self.no_quads_path)
        self.assertRaises(NoQuadsFound, no_quads_fp.create, dbGate=220)

if __name__ == "__main__":
    unittest.main()