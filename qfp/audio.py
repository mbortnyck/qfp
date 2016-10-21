from pydub import AudioSegment

def load_audio(path, downsample=True, normalize=True, snip=None):
    """
    Creates array of samples from input audio file
    snip = only return first n seconds of input
    """
    audio = AudioSegment.from_file(path)
    if downsample:
        # downsample if stereo, sample rate > 16kHz, or > 16-bit depth
        if (audio.channels > 1) \
          or (audio.frame_rate != 16000) \
          or (audio.sample_width != 2):
            audio = _downsample(audio)
    if normalize:
        audio = _normalize(audio)
    if snip is not None:
        milliseconds = snip * 1000
        audio = audio[:milliseconds]
    return audio.get_array_of_samples()

def _downsample(audio, numChannels=1, sampleRate=16000, bitDepth=2):
    """
    Downsamples audio to monoaural, 16kHz sample rate, 16-bit depth
    """
    audio = audio.set_channels(numChannels)
    audio = audio.set_frame_rate(sampleRate)
    audio = audio.set_sample_width(bitDepth)
    return audio

def _normalize(audio, target_dBFS=-20.0):
    """
    Normalizes loudness of audio segment
    """
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)