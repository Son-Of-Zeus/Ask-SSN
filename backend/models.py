# This file will contain the pydantic models for requests and responses.

from pydantic import BaseModel

class Citation(BaseModel):
    document_name: str
    page_number: str
    content: str

class ChatResponse(BaseModel):
    response: str
    citations: list[Citation]

class ChatRequest(BaseModel):
    query: list[dict[str, str]]