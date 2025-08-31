from fastapi import FastAPI
from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import queue
import time
import asyncio
import httpx
from uvicorn import run
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


model_size = "medium.en"
model = WhisperModel(model_size, device="cuda", compute_type="float32")

# Audio settings
sample_rate = 16000
block_duration = 0.5   
chunk_duration = 2     
channel = 1
silence_threshold = 0.01  
silence_timeout = 15       # stop after silence (secs)

frame_per_block = int(sample_rate * block_duration)
frame_per_chunk = int(sample_rate * chunk_duration)


@app.get("/transcribe")
async def transcribe_from_mic():
    audio_queue = queue.Queue()
    audio_buffer = []
    last_spoke_time = time.time()
    results = []

    def audio_callback(indata, frames, time_info, status):
        nonlocal last_spoke_time
        if status:
            print(status)

        # Check volume for silence detection
        volume_norm = np.linalg.norm(indata) / len(indata)
        if volume_norm > silence_threshold:
            last_spoke_time = time.time()

        audio_queue.put(indata.copy())

    # Recorder (blocking, but wrapped in executor later)
    def record_audio():
        with sd.InputStream(samplerate=sample_rate,
                            channels=channel,
                            callback=audio_callback,
                            blocksize=frame_per_block):

            print("Listening... Speak now (auto stops after silence)")
            while True:
                if time.time() - last_spoke_time > silence_timeout:
                    print("Silence detected. Stopping recording.")
                    break
                time.sleep(0.1)

        
        while not audio_queue.empty():
            audio_buffer.append(audio_queue.get())

    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, record_audio)

    if not audio_buffer:
        return {"text": ""}

    audio_data = np.concatenate(audio_buffer).flatten().astype(np.float32)

   
    def run_whisper():
        segments, info = model.transcribe(audio_data, language="en", beam_size=1)
        return [seg.text for seg in segments]

    results = await loop.run_in_executor(None, run_whisper)
    text = " ".join(results)

    
    # async with httpx.AsyncClient() as client:
    #     try:
    #         resp = await client.post(
    #             "http://127.0.0.1:8002/response",
    #             json={"question": text},
    #             timeout=60.0
    #         )
    #         print(" Forwarded to 8002:", resp.json())
    #     except Exception as e:
    #         print("Error forwarding:", e)

    return {"text": text}


if __name__ == "__main__":
    run("main:app", host="127.0.0.1", port=8001, reload=False)
