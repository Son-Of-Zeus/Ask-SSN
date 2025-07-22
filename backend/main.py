# This file will contain all the application logic and api endpoints

from fastapi import FastAPI
from models import ChatRequest, ChatResponse

app = FastAPI()

@app.post("/api/chat_completion/")
def main(query: ChatRequest):
    return ChatResponse(reponse="I am a humble ssn bot")