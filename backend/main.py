import os
import qdrant_client
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import Settings, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.litellm import LiteLLM
from llama_index.core import PromptTemplate
from models import ChatRequest, ChatResponse, Citation

load_dotenv()
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    Settings.llm = LiteLLM(model=os.getenv("LLM_MODEL_NAME"))
    Settings.embed_model = OllamaEmbedding(
        model_name=os.getenv("EMBED_MODEL_NAME"),
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )
    Settings.chunk_size = 512
    qdrant_client = qdrant_client.QdrantClient(url=os.getenv("QDRANT_URL"))
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
    )
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
except Exception as e:
    print(f"Failed to initialize LlamaIndex components: {e}")
    index = None


def format_chat_history(history: list[dict[str, str]]) -> str:
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])


@app.post("/api/chat_completion/", response_model=ChatResponse)
def chat_completion(request: ChatRequest):
    if index is None:
        raise HTTPException(status_code=500, detail="RAG index is not available.")
    
    chat_history_str = format_chat_history(request.query)

    if not chat_history_str:
        raise HTTPException(status_code=400, detail="No user message found in the query.")

    router_prompt_template = """
    You are a routing controller for an academic assistant for SSN College of Engineering.
Your knowledge base contains the full text of:
- SSN College of Engineering - Regulation 2021
- Computer Science & Engineering (CSE) Syllabus - 2021

Your job:
1) Analyze the latest user message in the chat history.
2) Decide which tool to use:
   - "rag_query_tool": Use this ONLY if the message asks a specific, factual question that can be answered by consulting the Regulation 2021, CSE Syllabus 2021. This includes questions about course codes, credits, prerequisites, grading policies, attendance rules, examination procedures, and lists of subjects per semester for CSE.
   - "general_conversation_tool": Use this for all other cases, including greetings, follow-up conversations, or questions outside the scope of the specified documents.
3) If you choose "rag_query_tool", you MUST reformulate ONLY the latest user message into a single, self-contained question for the knowledge base.

Rules:
- Respond with JSON only. No prose, no code fences, no explanations.
- If the latest message is ambiguous, a greeting, or not a direct question about the documents, choose "general_conversation_tool".
- Do NOT invent or assume any details.
- Do NOT include any keys beyond those specified.

Chat History:
{chat_history}

Output format (choose exactly one):
For RAG:
{{
  "tool_name": "rag_query_tool",
  "query_for_rag": "<self-contained question about SSN regulations or CSE/ECE syllabus>"
}}

For general conversation:
{{
  "tool_name": "general_conversation_tool"
}}
"""
    
    routing_prompt = router_prompt_template.format(chat_history=chat_history_str)
    router_response = Settings.llm.complete(routing_prompt)
    print(f"Router response: {router_response}")
    try:
        cleaned_response = str(router_response).strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:-3].strip()
        
        tool_choice = json.loads(cleaned_response)
        chosen_tool = tool_choice.get("tool_name")
    except (json.JSONDecodeError, AttributeError):
        chosen_tool = "general_conversation_tool"

    if chosen_tool == "rag_query_tool":
        rag_query = tool_choice.get("query_for_rag")
        if not rag_query:
            raise HTTPException(status_code=500, detail="Router decided on RAG but failed to generate a query.")
        
        gemma_qa_prompt_str = gemma_qa_prompt_str = """
You are ASK-SSN Bot, an academic assistant for SSN College of Engineering.
Follow these rules strictly:
- Answer ONLY using the provided CONTEXT. Treat the CONTEXT as the single source of truth.
- If the answer is not explicitly present in CONTEXT, state that you do not know based on the available context and ask a brief, specific clarification question if appropriate.
- Do NOT assume, guess, generalize, or infer beyond the CONTEXT.
- If the user’s question is unclear or underspecified, ask a concise clarifying question instead of answering.
- Always format your response in valid Markdown.
- Keep the answer precise, factual, and minimal; avoid verbosity and speculation.
- Do NOT include external links, policies, or references not present in CONTEXT.
- If there are multiple possible interpretations, list them and ask which one applies, without choosing on your own.
- Do NOT EVER include references to page numbers in the response.
- Never fabricate page numbers, document titles, data points, dates, or regulations.

CONTEXT:
{context_str}

USER QUESTION:
{query_str}

Produce a concise Markdown response now:
"""

        qa_template = PromptTemplate(gemma_qa_prompt_str)
        query_engine = index.as_query_engine(similarity_top_k=3, text_qa_template=qa_template)
        
        rag_response = query_engine.query(rag_query)

        citations = []
        for node in rag_response.source_nodes:
            metadata = node.metadata or {}
            citations.append(
                Citation(
                    document_name=metadata.get('file_name', 'Unknown Document'),
                    page_number=str(metadata.get('page_label', 'Unknown Page')),
                    content=node.get_content(),
                )
            )

        print(f"RAG response: {rag_response}\nCitation: {citations}\n")
        return ChatResponse(response=str(rag_response), citations=citations)
    
    else:
        general_prompt_template = fgeneral_prompt_template = f"""
You are ASK-SSN Bot, a friendly and professional assistant restricted to SSN College of Engineering topics (curriculum, regulations, academic rules).
Strict rules:
- Stay on SSN academic topics only; if the request is off-scope (e.g., news, weather, personal opinions), politely decline and suggest asking about SSN topics.
- Never assume or invent facts.
- If the user’s request is ambiguous or lacks specifics, ask a brief, targeted clarification question before answering.
- Always respond in valid Markdown.
- Be concise and factual.

Chat History:
{chat_history_str}

assistant:
"""

        
        general_response = Settings.llm.complete(general_prompt_template)

        print(f"General response: {general_response}")
        return ChatResponse(
            response=str(general_response),
            citations=[]
        )