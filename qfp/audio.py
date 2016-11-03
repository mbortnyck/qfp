from pydub import AudioSegment

from .exceptions import InvalidAudioLength

def load_audio(path, **kwargs):
    """
    Creates array of samples from input audio file
    snip = only return first n seconds of input
    """
    downsample = kwargs.pop("downsample", True)
    normalize = kwargs.pop("normalize", True)
    target_dBFS = kwargs.pop("target_dbFS", -20.0)
    snip = kwargs.pop("snip", None)
    audio = AudioSegment.from_file(path)
    if downsample:
        # if stereo, sample rate > 16kHz, or > 16-bit depth
        if (audio.channels > 1) \
          or (audio.frame_rate != 16000) \
          or (audio.sample_width != 2):
            audio = _downsample(audio)
    if normalize and audio.dBFS is not target_dBFS:
        audio = _normalize(audio, target_dBFS)
    if snip > audio.duration_seconds:
        raise InvalidAudioLength(
            "Provided snip length is longer than audio file")
    if snip is not None:
        milliseconds = snip * 1000
        audio = audio[:milliseconds]
    return audio.get_array_of_samples()

def _downsample(audio, numChannels=1, sampleRate=16000, bitDepth=2):
    """
    Returns downsampled AudioSegment
    """
    audio = audio.set_channels(numChannels)
    audio = audio.set_frame_rate(sampleRate)
    audio = audio.set_sample_width(bitDepth)
    return audio

def _normalize(audio, target_dBFS):
    """
    Normalizes loudness of AudioSegment
    """
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)