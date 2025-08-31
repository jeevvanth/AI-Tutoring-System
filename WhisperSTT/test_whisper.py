# from faster_whisper import WhisperModel

# model_size = "medium.en"


# model = WhisperModel(model_size, device="cpu", compute_type="float32")



# segments, info = model.transcribe("audio1.mp3", beam_size=5)

# # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# for segment in segments:
#     # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
#     print(segment.text)

import requests

data={}
resp = requests.get("http://127.0.0.1:8001/transcribe")
if resp.status_code == 200:
    data = resp.json()
    text = data.get("text", "")
    if text:
        print("Transcribed:", text)
    else:
        print("No speech detected.")
else:
    print("Error:", resp.status_code, resp.text)
