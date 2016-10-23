from pydub import AudioSegment

def load_audio(path, downsample=True, normalize=True, target_dBFS=-20.0, snip=None):
    """
    Creates array of samples from input audio file
    snip = only return first n seconds of input
    """
    audio = AudioSegment.from_file(path)
    if downsample:
        # if stereo, sample rate > 16kHz, or > 16-bit depth
        if (audio.channels > 1) \
          or (audio.frame_rate != 16000) \
          or (audio.sample_width != 2):
            audio = _downsample(audio)
    if normalize and audio.dBFS is not target_dBFS:
        audio = _normalize(audio, target_dBFS)
    if snip is not None and audio.duration_seconds > snip:
        milliseconds = snip * 1000
        audio = audio[:milliseconds]
    return audio.get_array_of_samples()

def _downsample(audio, numChannels=1, sampleRate=16000, bitDepth=2):
    """
    returns downsampled AudioSegment
    """
    audio = audio.set_channels(numChannels)
    audio = audio.set_frame_rate(sampleRate)
    audio = audio.set_sample_width(bitDepth)
    return audio

def _normalize(audio, target_dBFS):
    """
    normalizes loudness of AudioSegment
    """
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)