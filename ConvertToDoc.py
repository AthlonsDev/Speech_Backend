api_key = 'AIzaSyCoOw-xfas4_coDHFbo3nKyPHtSDk7HdGU'
import time
from google import genai
from docx import Document
models = [
    "gemini-2.5-flash",
    "gemma-3-27b-it", 
    "gemini-2.0-flash",
    "gemini-3-flash-preview"
]
client = genai.Client(api_key=api_key)

def get_date():
    return time.strftime("%d-%m-%Y")

def convert_to_doc(text, output_filename, type):
    doc = Document() #document object
    doc.add_heading('Transcription', level=0) #Title of the document
    doc.add_heading('document info', level=2) #Subtitle of the document
    doc.add_paragraph(f'date: {get_date()} \ntype of document: {type}') #Intro paragraph
    doc.add_heading('Transcribed Text', level=2) #Heading for transcribed text
    doc.add_paragraph(text) #First paragraph of the document
    doc.add_heading('Summary', level=1) #Summary heading
    doc.add_paragraph(doc_assistant(text)) #Summary paragraph
    save_path = "c:\\Users\\athlo\\Desktop\\GenDoc"
    # good to save as a backup. But since the frontend looks for the file in the project dir
    # It should be saved here as well. Or use a cloud storage solution.
    # Possibly connect to Onedrive to automatically send it there? Check if needed.
    # For now save it in the project directory as well.
    doc.save(output_filename)

    return output_filename

text=" The mute muffled the high tones of the horn. The gold ring fits only a pierced ear. The old pan was covered with hard fudge. Watch the log float in the wide river. The node on the stock of wheat grew daily. The heap of fallen leaves was set on fire. Right fast, if you want to finish early. His shirt was clean, but one button was gone. The barrel of beer was a brew of malt and hops. Tin cans are absent from store shelves."
output_filename = f"Transcription - {get_date()}.docx"
def doc_assistant(text):
    prompt = f"Summarize the following text in concise paragraph:\n\n{text}"
    response = client.models.generate_content(
        model=models[1],
        contents=prompt,
        config={
            'response_mime_type': 'text/plain',
        }
    )
    print("Assistant Response:", response.candidates[0].content.parts[0].model_dump()['text'])
    # return response.candidates[0].content.parts[0].model_dump()['text']
    summary = response.candidates[0].content.parts[0].model_dump()['text']

    return summary

# convert_to_doc(text, output_filename, type="Notes")
