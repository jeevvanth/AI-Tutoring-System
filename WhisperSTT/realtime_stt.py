import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel
import time


sample_rate=16000
block_duration=0.5
chunk_duration=2
channel=1


silence_threshold = 0.01   # adjust this (lower = more sensitive)
silence_timeout = 20  


frame_per_block=int(sample_rate*block_duration)
frame_per_chunck=int(sample_rate * chunk_duration)


audio_queue=queue.Queue()
audio_buffer=[]

model_size="medium.en"

model = WhisperModel(model_size, device="cuda", compute_type="float32")

# def audio_callback(indata,frames,time,status):
#     if status:
#         print(status)
#     audio_queue.put(indata.copy())

# def recorder():
#     with sd.InputStream(samplerate=sample_rate, channels=channel,callback=audio_callback,blocksize=frame_per_block):
#         print("Listenning... press ctrl + c to stop")
#         while True:
#             pass


last_spoke_time = time.time()

def audio_callback(indata, frames, time_info, status):
    global last_spoke_time
    if status:
        print(status)

    # calculate volume
    volume_norm = np.linalg.norm(indata) / len(indata)
    if volume_norm > silence_threshold:
        last_spoke_time = time.time()  # update when user speaks

    audio_queue.put(indata.copy())

def recorder():
    global last_spoke_time
    with sd.InputStream(samplerate=sample_rate, channels=channel,
                        callback=audio_callback, blocksize=frame_per_block):
        print("Listening... (auto stops after silence)")
        while True:
            # break if silence detected for too long
            if time.time() - last_spoke_time > silence_timeout:
                print("Silence detected. Stopping recording.")
                break
            time.sleep(0.1)

def transcriber():
    global audio_buffer
    while True:

        try:
            block = audio_queue.get(timeout=1)
        except queue.Empty:
            break
        # block=audio_queue.get()
        audio_buffer.append(block)

        total_frames=sum(len(b) for b in audio_buffer)

        if total_frames >= frame_per_chunck:
            audio_data=np.concatenate(audio_buffer)[:frame_per_chunck]
            audio_buffer=[]

            audio_data=audio_data.flatten().astype(np.float32)

            segments,info=model.transcribe(
                audio_data,
                language="en",
                beam_size=1
            )

            for segment in segments:
                print(f"{segment.text}")

import torch
print("CUDA available:", torch.cuda.is_available())
print("CUDA version expected by PyTorch:", torch.version.cuda)


threading.Thread(target=recorder,daemon=True).start()
transcriber()   