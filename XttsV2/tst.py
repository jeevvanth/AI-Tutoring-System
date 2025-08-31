# import torch
# print("CUDA available:", torch.cuda.is_available())
# print("CUDA device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
import requests
import io
import sounddevice as sd
import soundfile as sf

text="""
The Microsoft C++ Build Tools provides MSVC toolsets via a scriptable, 
standalone installer without Visual Studio. Recommended if you build C++ libraries and applications targeting Windows from the command-line (e.g. as part of your continuous integration workflow). 
Includes tools shipped in Visual Studio 2015 Update 3, Visual Studio 2017, Visual Studio 2019, and latest version of Visual Studio 2022.
"""
resp = requests.post("http://127.0.0.1:8000/speak", json={"text":f"{text}"})
buffer = io.BytesIO(resp.content)

# Read WAV data
data, samplerate = sf.read(buffer)

# Play directly
sd.play(data, samplerate)
sd.wait()
