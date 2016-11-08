import unittest
import os

from qfp.fingerprint import (
    fpType,
    Fingerprint,
    ReferenceFingerprint,
    QueryFingerprint
)

from qfp.audio import load_audio

from qfp.exceptions import (
    InvalidFpType,
    InvalidAudioLength,
    TooFewPeaks,
    NoQuadsFound
)

dataDir = os.path.join(os.path.dirname(__file__), 'data')

class FpTypeTests(unittest.TestCase):
    def test_query_parameters_are_greater(self):
        self.assertGreater(fpType.Query[0], fpType.Reference[0])
        self.assertGreater(fpType.Query[1], fpType.Reference[1])
        self.assertGreater(fpType.Query[2], fpType.Reference[2])
    def test_k_values_are_equal(self):
        self.assertEqual(fpType.Reference[3], fpType.Query[3])

class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.ins_audio_length_path = os.path.join(dataDir, 'short_audio_sample.mp3')
        self.ins_peaks_path = os.path.join(dataDir, 'silence.mp3')
        self.no_quads_path = os.path.join(dataDir, 'few_peaks.mp3')
    def test_k_too_large_for_provided_audio(self):
        ins_audio_length_fp = ReferenceFingerprint(self.ins_audio_length_path)
        self.assertRaises(InvalidAudioLength, ins_audio_length_fp.create)
    def test_too_few_peaks_to_form_quads(self):
        ins_peaks_fp = ReferenceFingerprint(self.ins_peaks_path)
        self.assertRaises(TooFewPeaks, ins_peaks_fp.create)
    def test_no_quads_found(self):
        no_quads_fp = ReferenceFingerprint(self.no_quads_path)
        self.assertRaises(NoQuadsFound, no_quads_fp.create, dbGate=220)
    def test_InvalidFpType(self):
        self.assertRaises(InvalidFpType, Fingerprint, self.no_quads_path, fp_type=[0])

class AudioTests(unittest.TestCase):
    def setUp(self):
        self.ten_seconds_path = os.path.join(dataDir, 'silence.mp3')
    def test_snip_greater_than_audio_length(self):
        self.assertRaises(InvalidAudioLength, load_audio, self.ten_seconds_path, snip=15)

if __name__ == "__main__":
    unittest.main()