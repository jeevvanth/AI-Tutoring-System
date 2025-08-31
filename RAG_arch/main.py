import dotenv
from langchain_groq import ChatGroq
from langchain.prompts import (
  PromptTemplate,
   SystemMessagePromptTemplate,
  HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uvicorn import run
import requests
import asyncio
from langchain.schema.runnable import RunnableLambda
import requests
import io
import sounddevice as sd
import soundfile as sf
from fastapi.middleware.cors import CORSMiddleware


dotenv.load_dotenv()

app=FastAPI()

chat_model = ChatGroq(
    model="llama3-70b-8192",  
    temperature=0
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5173"] for stricter
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

CHROMA_PATH = "chroma_pdf_data/"

system_template_str="""
You are an AI tutor in Machine Learning. 
Explain concepts step by step in exactly 25–30 words only. 
dont use simple language, examples, and Python snippets. 
End with a short understanding-check question for eg do you have any ml question.

Here is the context:
{context}

"""

system_prompt=SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=system_template_str
    )
)

human_prompt=HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],template="{question}"
    )
)

messages=[system_prompt,human_prompt]

prompt_template=ChatPromptTemplate(
    input_variables=["context","question"],
    messages=messages,
)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_model
)

retriever=vector_db.as_retriever(k=10)



chain=({"context":retriever,"question":RunnablePassthrough()} |
    prompt_template 
    | chat_model)


class UserInput(BaseModel):
    question:str

# response=requests.get("http://127.0.0.1:8001/transcribe")

# if response.status_code == 200:
#     data = response.json()
#     text = data.get("text", "")
# else:
#     print("Error:", response.status_code, response.text)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.post("/response")
def text_response(user_input: UserInput):
    try:
        question = user_input.question 
        print("DEBUG incoming question:", repr(question))
        response = chain.invoke(question)

        print("DEBUG chain.invoke result:", response)


        # If response is a dict, extract 'output' or 'answer' field
        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)

        print("response_text:",response_text)
        # try:
        #     resp = requests.post("http://127.0.0.1:8000/speak", json={"text":f"{response_text}"})
        #     if resp.status_code != 200:
        #       print("Server error:", resp.text)
        #     else:
        #       buffer = io.BytesIO(resp.content)
        #       print("Response size:", len(resp.content))
        #       data, samplerate = sf.read(buffer)
        #       sd.play(data, samplerate)
        #       sd.wait()
              
        # except Exception as e:
        #     print("Error forwarding:", e)

        return {"response": response_text}


    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Errors: {str(ex)}")

    



if __name__=="__main__":
   run("main:app",
       host="127.0.0.1",
       port=8002,
       reload=False  
   )