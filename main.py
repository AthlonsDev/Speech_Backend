import time

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse, PlainTextResponse
from speech_handler import transcription
from ConvertToDoc import convert_to_doc, get_date, meetings_assistant
from aws_client import upload_doc
import requests
from fastapi.middleware.cors import CORSMiddleware

n_jobs = 0
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request schema
class SpeechInputData(BaseModel):
    features: list[str]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Speech Recognition API!"}

# Important!: Stop the instance once the processing and uploading is complete, otherwise the cost will quickly rise
def stopEC2Instance():
    print("Stopping EC2 instance...")
    res = requests.post("https://m67kummn2c.execute-api.eu-west-2.amazonaws.com/test1/stop")# Call API that calls Lambda function that stops the instance
    if res.status_code == 200:
        print("EC2 instance stopped successfully.")
        return True
    else:
        time.sleep(5) # Wait for 5 seconds before retrying to stop the instance.
        stopEC2Instance() # If stopping the instance fails, we can call the function again to retry, as sometimes the API call can fail due to network issues or other transient problems. This way we can ensure that the instance is stopped and we don't incur unnecessary costs.
        print(f"Failed to stop EC2 instance. Status code: {res.status_code}, Response: {res.text}")
        return False

@app.post("/speech")
async def speech_recognition(file: UploadFile = File(...), model_type: str = Form(...)):

    # Save uploaded file to disk
    file_path = file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        n_jobs += 1
        print("Starting transcription...")
        print(model_type)
        # call model based on audio type, simple notes model or more complex meeting minutes model
        result = transcription(file.filename, model_type=model_type)
        
        print(f"Transcription result type: {type(result)}")
        print(f"Transcription result: {result}")
        print("Converting to doc...")
        # fix name of the file from .wav/.mp3/.m4a to .docx for the generated document
        file_doc = file.filename.replace(".wav", ".docx").replace(".mp3", ".docx").replace(".m4a", ".docx")
        # Depending on the model type, call the appropriate function to generate the doc
        if model_type == "notes": #simpler text output, no json formatting
            doc = convert_to_doc(result, file_doc, model_type)
        else: #more complex, multiple speakers, json formatting, minute meeting structure
            doc = meetings_assistant(result, file_doc)
        # AI process is complete, upload doc to s3
        upload_doc(doc, f"Transcription_{get_date()}.docx")
        # Model has done processing, the doc has been generated and uploaded - kill instance
        n_jobs -= 1
        if n_jobs == 0: # Only stop the instance if there are no more jobs being processed, otherwise we might stop the instance while it's still processing other requests, which would lead to errors and a bad user experience. This way we can ensure that the instance is only stopped when it's truly idle and not processing any requests.
            if stopEC2Instance():
                return file_doc
    
    except Exception as e:
        print(f"Error details: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

# To run the app, use: uvicorn backend.main:app --reload
