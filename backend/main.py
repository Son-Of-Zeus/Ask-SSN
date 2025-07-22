# This file will contain all the application logic and api endpoints
from dotenv import load_dotenv
from fastapi import FastAPI
from models import ChatRequest, ChatResponse
from fastapi.middleware.cors import CORSMiddleware
from litellm import completion

load_dotenv()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat_completion/")
def main(query: ChatRequest):
    response = completion(
    model="gemini/gemma-3-27b-it", 
    messages=query.query
    )

    model_response = response['choices'][0]['message']['content']
    return ChatResponse(reponse=model_response)