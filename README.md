# Ask-SSN

Ask-SSN helps students at SSN College of Engineering find answers in academic documents.

## About the project

Course requirements, semester subjects, and academic rules are spread across curriculum and regulation PDFs. Ask-SSN gives students one place to ask questions about those documents in plain language.

- Which subjects are in the first semester of the CSE curriculum?
- What are the credit requirements for my program?
- What do the academic regulations say about course prerequisites?

The assistant searches the PDFs in its knowledge base and uses the relevant passages to answer. The chat shows the source document, page label, and excerpt when available, so students can check the answer against the original text.

## How it works

- A Python script reads PDFs, creates embeddings with Ollama, and stores them in Qdrant through LlamaIndex.
- The FastAPI backend uses the chat history to route each message. For an academic question, it rewrites the question so it can stand alone and retrieves up to three passages for the answer. A separate path handles small talk.
- The Next.js frontend displays the answer and its citations.

## Run locally

Install [uv](https://docs.astral.sh/uv/), Node.js 20 or later, Docker, and Ollama. The backend uses Python 3.13 or later.

1. From the repository root, start Qdrant. Start Ollama and download the embedding model.

   ```sh
   docker run -d --name ask-ssn-qdrant -p 127.0.0.1:6333:6333 \
     -v ask-ssn-qdrant:/qdrant/storage qdrant/qdrant
   ollama pull mxbai-embed-large
   ```

2. Create `backend/.env` with the settings below. Replace `your-key` with a key from [Google AI Studio](https://aistudio.google.com/).

   ```dotenv
   GEMINI_API_KEY=your-key
   QDRANT_URL=http://127.0.0.1:6333
   QDRANT_COLLECTION_NAME=SSN_DOCS
   OLLAMA_BASE_URL=http://127.0.0.1:11434
   EMBED_MODEL_NAME=mxbai-embed-large
   LLM_MODEL_NAME=gemini/gemma-3-27b-it
   ```

3. Set up the backend and create the input folder.

   ```sh
   cd backend
   uv sync
   mkdir -p knowledge_base
   ```

   Copy at least one text-based college PDF into `backend/knowledge_base/`. From `backend/`, run the commands below. Choose `1` to index the PDFs, then `4` to exit. The script moves indexed PDFs to `processed_documents/`.

   ```sh
   uv run manage_knowledge_base.py
   uv run uvicorn main:app --reload
   ```

4. In a second terminal, run the frontend from the repository root.

   ```sh
   cd frontend
   npm ci
   npm run dev
   ```

Open [the chat](http://localhost:3000) and ask a question that your PDF covers. You can also try `POST /api/chat_completion/` in the [API docs](http://127.0.0.1:8000/docs).

See the [backend guide](backend/README.md) for more detail on managing the knowledge base.
