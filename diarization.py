from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pyannote.audio.telemetry import set_telemetry_metrics
import torch

def setup_pipeline():
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        token="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"
    )

    return pipeline

def run_dia(pipeline, input_file):
    # send pipeline to GPU (if available)
    pipeline.to(torch.device("cuda"))

    output = pipeline(input_file)
    return output
    # print the result
    # for turn, speaker in output.speaker_diarization:
    #     print(f"{speaker} speaks between t={turn.start:.3f}s and t={turn.end:.3f}s")

def init_diarization(input):
    pipeline = setup_pipeline()
    diarization = run_dia(pipeline, input)

    return diarization