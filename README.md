# qfp
Qfp is a python library for creating audio fingerprints that are robust to alterations in pitch and speed. This method is ideal for ID'ing music from recordings such as DJ sets where the tracks are commonly played at a different pitch or speed than the original recording. Qfp is an implementation of the audio fingerprinting/recognition algorithms detailed in a 2016 academic paper by Reinhard Sonnleitner and Gerhard Widmer [1].

## Quickstart
Install using pip

```
pip install --upgrade https://github.com/mbortnyck/qfp/tarball/master
```

... or clone the repository.

```
git clone https://github.com/mbortnyck/qfp/
```

You can create a fingerprint from your reference audio

```python
from qfp import ReferenceFingerprint

fp_r = ReferenceFingerprint("Prince_-_Kiss.mp3")
fp_r.create()
```

... or a query fingerprint from an audio clip that you wish to identify.

```python
from qfp import QueryFingerprint

fp_q = QueryFingerprint("unknown_audio.wav")
fp_q.create()
```

Qfp currently accepts recordings in [any format that ffmpeg can handle](http://www.ffmpeg.org/general.html#File-Formats).

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
- [x] Calculate peaks (local maxima) of spectrogram

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
