# qfp
Qfp is a python library for creating audio fingerprints that are robust to changes in pitch and tempo. It is based on an academic paper by Reinhard Sonnleitner and Gerhard Widmer [1].

## Quickstart

Create a fingerprint from your reference audio

```python
from qfp import ReferenceFingerprint

fp_r = ReferenceFingerprint("prince_-_kiss.mp3")
fp_r.create()
```

... or a query fingerprint from an unidentified audio clip.

```python
from qfp import QueryFingerprint

fp_q = QueryFingerprint("unknown_audio.wav")
fp_q.create()
```

## Dependencies

pydub - [https://github.com/jiaaro/pydub](https://github.com/jiaaro/pydub)<br>
ffmpeg - [https://github.com/FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg)<br>
numpy - [https://github.com/numpy/numpy](https://github.com/numpy/numpy)<br>
scipy - [https://github.com/scipy/scipy](https://github.com/scipy/scipy)<br>
bitstring - [https://github.com/scott-griffiths/bitstring](https://github.com/scott-griffiths/bitstring)<br>

## Progress
#### Feature Extraction
- [x] Load audio as array of samples
- [x] Create STFT spectrogram from samples
- [x] Calculate peaks of spectrogram

#### Quad Creation
- [x] For each peak, create all possible quads
- [x] Validate quads
- [x] Create hashes for valid quads

#### Storage
- [x] Pack valid quads into binary strings
- [ ] Store binary strings in QuadDB
- [x] Store hashes in spatial database

#### Recognition
- [ ] Lookup query hashes in spatial database
- [ ] Filter results that fall outside of scale tolerance bounds
- [ ] Estimate time/frequency scaling
- [ ] Validate results / filter out false positives

***
*<sub>[1]	R. Sonnleitner and G. Widmer, "Robust quad-based audio fingerprinting," IEEE/ACM Transactions on Audio, Speech and Language Processing (TASLP), vol. 24, no. 3, pp. 409–421, Jan. 2016. [Online]. Available: [http://ieeexplore.ieee.org/abstract/document/7358094/](http://ieeexplore.ieee.org/abstract/document/7358094/). Accessed: Nov. 15, 2016.<sub>*
