import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import joblib



def load_model():
    if torch.cuda.is_available():
        torch_dtype = torch.float16
    else:
        torch_dtype = torch.float32 #float 16 for cuda but not available
    device = "cuda" if torch.cuda.is_available() else "cpu"
        # model_id = "openai/whisper-large-v3"

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


# def save_model(pipe, filename="whisper_model.pt"):
#     torch.save(pipe, filename)

# def save_model_pkl(pipe, filename="whisper_model.pkl"):
#     joblib.dump(pipe, filename)

# def main():
#     pipe = load_model()
#     # save_model(pipe)
#     save_model_pkl(pipe)
# main()

# The speech recognition tool is mostly done, I just need to port it to the AWS environment to be publicly available.
# About the Biurbs application
# I will also add a system to allow for new data to be added dynamically.
# This will allow the model to learn from new data and improve its performance over time.
