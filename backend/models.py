# This file will contain the pydantic models for requests and responses.

from pydantic import BaseModel

class ChatResponse(BaseModel):
    reponse: str

class ChatRequest(BaseModel):
    query: list[dict[str, str]]