import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
import sounddevice as sd
import torchaudio
from fastapi import FastAPI,Body,HTTPException
from fastapi.responses import StreamingResponse
from uvicorn import run
# import simpleaudio as sa
# import numpy as np
import soundfile as sf
import io
from pydantic import BaseModel 
import requests
from fastapi.middleware.cors import CORSMiddleware
# import subprocess

# torch.serialization.add_safe_globals([XttsConfig])

app=FastAPI()

_real_torch_load = torch.load

def torch_load_wrapper(*args, **kwargs):
    kwargs["weights_only"] = False  # force disable weights_only
    return _real_torch_load(*args, **kwargs)

torch.load = torch_load_wrapper




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5173"] for stricter
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)


device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)


print(TTS().list_models())


tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)

# text="""
# The Microsoft C++ Build Tools provides MSVC toolsets via a scriptable, 
# standalone installer without Visual Studio. Recommended if you build C++ libraries and applications targeting Windows from the command-line (e.g. as part of your continuous integration workflow). 
# Includes tools shipped in Visual Studio 2015 Update 3, Visual Studio 2017, Visual Studio 2019, and latest version of Visual Studio 2022.
# """

# wav = tts.tts(text=text, speaker_wav="audio.mp3", language="en")

# sd.play(wav, samplerate=22050)
# sd.wait()

class LLMResponse(BaseModel):
    text:str= Body(..., embed=True)




@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.post("/speak")
def text_to_speech(response:LLMResponse):
    try:
         text=response.text
         print(text)
         wav=tts.tts(text=text,speaker_wav="audio.mp3",language="en")

         buffer = io.BytesIO()
         sf.write(buffer, wav, 22050, format="WAV")
         buffer.seek(0)
         return StreamingResponse(buffer, media_type="audio/wav")
    except Exception as ex:
         raise HTTPException(status_code=400,detail=f"{str(ex)}")


    



if __name__=="__main__":
    run("main:app",
        host="127.0.0.1",
        port=8000,
        reload=False)



