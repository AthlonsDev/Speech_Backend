from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse, PlainTextResponse
from speech_handler import transcription
from ConvertToDoc import convert_to_doc
import os
import time

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origins = ['http://localhost:8000', 'http://190.168.0.132']

app.add_middleware(
    CORSMiddleware,
#   allow_origins=[
#       'https://main.d2x1a5nxcjgsfv.amplifyapp.com',
#       'https://13.40.107.140:8000',
#       'https://scaling-eureka-7pw5xw7q9qxhrj5j-3000.app.github.dev'],
    allow_origins=['https://fall-unavailable-resistant-moving.trycloudflare.com', '*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request schema
class InputData(BaseModel):
    features: list[float]

class SpeechInputData(BaseModel):
    features: list[str]

class SearchInputData(BaseModel):
    features: list[str]

@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = filename
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_data = f.read()
        return PlainTextResponse(content=file_data, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/speech")
async def speech_recognition(file: UploadFile = File(...), model_type: str = Form(...)):

    # Save uploaded file to disk
    file_path = file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        print("Starting transcription...")
        print(model_type)
        result = transcription(file.filename, model_type=model_type)
        
        print(f"Transcription result type: {type(result)}")
        print(f"Transcription result: {result}")
        print("Converting to doc...")
        file_doc = file.filename.replace(".wav", ".docx").replace(".mp3", ".docx").replace(".m4a", ".docx")
        convert_to_doc(result, file_doc, model_type)

        os.remove(file_path)  # Clean up uploaded audio file

        return file_doc
    
    except Exception as e:
        print(f"Error details: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

# To run the app, use: uvicorn backend.main:app --reload
