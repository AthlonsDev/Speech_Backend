import io
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Tuple, Union, cast
import torch
import torchaudio
from whisper import load_model
from diarization import init_diarization


def _load_audio_input(
    source: Union[str, Path, os.PathLike, io.IOBase, Mapping, torch.Tensor],
    target_sample_rate: int = 16000,
) -> Tuple[torch.Tensor, int]:
    """Normalize a variety of audio input types to (waveform, sample_rate).

    Supported input forms:
    - str / Path / os.PathLike: path to audio file
    - file-like object with read() and seek()
    - Mapping with key 'audio' containing one of the above, and optional 'channel'
      e.g. {'audio': open('st.wav','rb'), 'channel': 0}
    - Mapping with keys 'waveform' (torch.Tensor) and 'sample_rate' (int)

    Returns waveform as Tensor (channels, samples) and sample_rate (int).
    """
    if isinstance(source, Mapping):
        if "waveform" in source and "sample_rate" in source:
            wf = source["waveform"]
            sr = int(source["sample_rate"])
            if not isinstance(wf, torch.Tensor):
                wf = torch.tensor(wf)
            return wf, sr

        if "audio" in source:
            audio_val = source["audio"]
            channel = source.get("channel", None)
            wf, sr = _load_audio_input(audio_val, target_sample_rate=target_sample_rate)
            if channel is not None:
                if wf.ndim == 1:
                    wf = wf.unsqueeze(0)
                wf = wf[int(channel) : int(channel) + 1, :]
            return wf, sr

    if isinstance(source, torch.Tensor):
        return source, target_sample_rate

    if isinstance(source, (str, Path, os.PathLike)):
        path = str(source)
        waveform, sample_rate = torchaudio.load(path)
    else:
        if hasattr(source, "read"):
            try:
                if hasattr(source, "seek"):
                    source.seek(0)
                data = source.read()
                bio = io.BytesIO(data)
                waveform, sample_rate = torchaudio.load(bio)
            except Exception:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
                    if hasattr(source, "seek"):
                        source.seek(0)
                    tf.write(data)
                    temp_name = tf.name
                try:
                    waveform, sample_rate = torchaudio.load(temp_name)
                finally:
                    try:
                        os.remove(temp_name)
                    except Exception:
                        pass
        else:
            raise ValueError(f"Unsupported audio input type: {type(source)}")

    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)
        sample_rate = target_sample_rate

    return waveform, int(sample_rate)


def combine(input_source: Any):
    segments = []
    d = init_diarization(input_source) #local/EC2 inference
    if d is None:
        print("Diarization failed")
        return

    print("diarization success!")
    waveform, sample_rate = _load_audio_input(input_source, target_sample_rate=16000)

    ann = getattr(d, "speaker_diarization", d)
    for segment, _, speaker in cast(Any, ann).itertracks(yield_label=True):
        start, end = segment.start, segment.end
        start_i = int(start * sample_rate)
        end_i = int(end * sample_rate)
        segment_audio = waveform[:, start_i:end_i]

        print(f"segments: {segment_audio.shape}")
        torchaudio.save("temp_seg.wav", segment_audio, sample_rate)

        print('start transcription...')
        w_pipe = load_model() # Local/EC2 Inference
        output = w_pipe("temp_seg.wav")
        t = output["text"]
        segments.append(f"{speaker}: {t}")

    # Return each segment on its own line
    return "\n".join(segments)
    # return "<br/>".join(segments)


def transcription(filename: str, model_type):
    """Public transcription entrypoint.

    # Accepts the same input forms documented earlier (path, file-like, mapping, waveform dict).
    """
    # Using Local or EC2 Inference 
    
    if model_type == "meeting":
        # print('using diarization...')
        result = combine(filename)
        # diarize_quick("temp_harvard.wav")
        return result
    else :
        # only use whisper
        whisper = load_model()
        result = whisper(filename, return_timestamps=True)
        result = result['text']
        return result
