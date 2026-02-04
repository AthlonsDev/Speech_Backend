import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


def transcript_audio(file):

    pipe = remote_model()

    results = pipe(file, return_timestamps=True)

    return results

def remote_model():
    device = 0 if torch.cuda.is_available() else 'cpu'
    if torch.cuda.is_available:
        torch_dtype = torch.float16 # Use float16 for CUDA if available
    else:
        torch_dtype = torch.float32 #float32 for CPU

    model_id = "openai/whisper-tiny"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id)
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device
    )

    return pipe