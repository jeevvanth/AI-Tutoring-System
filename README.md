#   AI TUTOR 

# Frontend 
React + Vite is used as a frontend front to develop the mascot and Mainly for the interaction with the Ai tutor

## installation setup
```bash
npm install
npm run dev #to run
```

# Backend Fastapi

Using fastapi developed 3 different services ie, like an Microservice Architecture 
-- RAG_arch
-- WhisperSTT
--XTTSV2

so whisperSTT is the first stage of  Speech to Text using faster-whisper model and second stage Rag Architecture for retrival of information to answer the question using langchain framework and third Stage is Text to Speech using xttsv2 model


## installation setup
```bash
#windows
python -m venv env
env/Scripts/activate

#Linux
python3 -m venv env
env/Scripts/activate

pip install -r requirements.txt

```



