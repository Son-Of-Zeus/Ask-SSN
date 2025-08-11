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


@app.post("/api/chat_completion/", response_model=ChatResponse)
def chat_completion(request: ChatRequest):
    if index is None:
        raise HTTPException(status_code=500, detail="RAG index is not available.")

    last_user_message = next((msg['content'] for msg in reversed(request.query) if msg['role'] == 'user'), None)

    if not last_user_message:
        raise HTTPException(status_code=400, detail="No user message found in the query.")

    tools = """
    [
        {"name": "rag_query_tool", "description": "Use this tool for specific questions about the SSN College of Engineering's curriculum, courses, electives, or academic rules."},
        {"name": "general_conversation_tool", "description": "Use this tool for greetings, small talk, chit-chat, or any question not related to the SSN curriculum."}
    ]
    """

    routing_prompt = f"""
    You are a routing agent of a chatbot designed to tackle questions related to SSN College of Engineering. Based on the user's query, select the single most appropriate tool from the following options.
    Respond with ONLY a JSON object containing the chosen tool's name. Example: {{"tool_name": "tool_name_here"}}

    Tools: {tools}
    User Query: "{last_user_message}"
    """
    
    router_response = Settings.llm.complete(routing_prompt)

    try:
        tool_choice = json.loads(str(router_response))
        chosen_tool = tool_choice.get("tool_name")
    except (json.JSONDecodeError, AttributeError):
        chosen_tool = "general_conversation_tool"


    if chosen_tool == "rag_query_tool":
        gemma_qa_prompt_str = """
            You are ASK-SSN, a professional and precise academic assistant for SSN College of Engineering.
            Your sole purpose is to answer questions based *strictly* on the context information provided below.
            If the answer cannot be found in the context, you must respond with exactly: 'The information is not available in my database. Please contact the college office to get the information.'\n\n
            Answer should be in the markdown format.
            CONTEXT:\n{context_str}\n\n"
            QUERY: {query_str}\n"
            ANSWER:
        """
        qa_template = PromptTemplate(gemma_qa_prompt_str)
        query_engine = index.as_query_engine(similarity_top_k=3, text_qa_template=qa_template)
        rag_response = query_engine.query(last_user_message)

        citations = []
        for node in rag_response.source_nodes:
            metadata = node.metadata or {}
            citations.append(
                Citation(
                    document_name=metadata.get('file_name', 'Unknown Document'),
                    page_number=metadata.get('page_label', 'Unknown Page'),
                    content=node.get_content(),
                )
            )
        return ChatResponse(response=str(rag_response), citations=citations)
    
    else: 
        general_prompt = f"""
       You are ASK-SSN, a professional and precise academic assistant for SSN College of Engineering.
        Your capabilities are:
        1. Engage in simple greetings and goodbyes.
        2. Explain your purpose, which is to answer questions about SSN College of Engineering's curriculum, courses, electives, or academic rules.

        Your limitations are:
        - For any question that is NOT a simple greeting, goodbye, or a query about your purpose, you MUST politely state that you cannot answer.
        - Examples of questions you cannot answer include: weather, news, jokes, personal opinions, or any topic outside of the SSN curriculum.

        User's message: "{last_user_message}"
        Your response:
        """
        
        general_response = Settings.llm.complete(general_prompt)

        return ChatResponse(
            response=str(general_response),
            citations=[]
        )