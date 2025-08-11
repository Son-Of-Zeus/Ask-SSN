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
    You are a master routing agent for an academic chatbot. Based on the entire chat history, you must perform two tasks:
    1. Decide which tool to use: 'rag_query_tool' for specific questions about SSN College of Engineering, or 'general_conversation_tool' for small talk.
    2. If you choose 'rag_query_tool', you MUST reformulate the user's latest query into a standalone, detailed question that can be understood without the chat history.

    **Chat History:**
    {chat_history}

    **Your Task:**
    Analyze the history. If the latest user query is a specific question about SSN, formulate a clear, self-contained question for the RAG system. If it's small talk, just select the general tool.

    Respond with ONLY a JSON object with the following format.

    For specific questions:
    {{
        "tool_name": "rag_query_tool",
        "query_for_rag": "A self-contained, reformulated question based on the history."
    }}

    For general conversation:
    {{
        "tool_name": "general_conversation_tool"
    }}

    Example:
    - History: "user: Tell me about the IT department\\nassistant: Here is the information about the IT department.\\nuser: what about for ECE?"
    - Your JSON Response: {{"tool_name": "rag_query_tool", "query_for_rag": "Tell me about the curriculum for the ECE department."}}
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
        
        gemma_qa_prompt_str = """
            You are ASK-SSN Bot, a professional and precise academic assistant for SSN College of Engineering.
            Your sole purpose is to answer questions based *strictly* on the context information provided below.Here are some intructions to be followed:
            - Use markdown to format your answer.
            - If the question isn't clear, ask users clarifying questions. 
            - If the answer cannot be found in the context, you must respond saying you don't know the answer.

            You are provided with context from a RAG Tool that pulled in releavant information according to the user query

            CONTEXT:
            {context_str}

            QUERY: {query_str}
            ANSWER:
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
        general_prompt_template = f"""
        You are ASK-SSN bot, a friendly and professional conversational AI assistant for SSN College of Engineering.
        Your purpose is to answer questions about SSN's curriculum, regulations and academic rules.
        Engage in a natural conversation based on the history. Politely decline any questions outside your scope (like news, weather, or personal opinions).

        Maintain your persona and continue the conversation below.

        **Chat History:**
        {chat_history_str}
        
        assistant:
        """
        
        general_response = Settings.llm.complete(general_prompt_template)

        print(f"General response: {general_response}")
        return ChatResponse(
            response=str(general_response),
            citations=[]
        )