# Backend for ASkSSN Bot

## Installation instructions
### Basic Setup
- Install uv in your computer
- Change to the backend folder
```
cd backend
```
- Install all the dependencies with uv
```
uv sync
```
- Create a .env file inside backend, with the following content.
```
GEMINI_API_KEY='<Your-Api-Key>'
QDRANT_URL="http://localhost:6333"
QDRANT_COLLECTION_NAME="SSN_DOCS"
OLLAMA_BASE_URL="http://localhost:11434"
EMBED_MODEL_NAME="mxbai-embed-large"
LLM_MODEL_NAME="gemini/gemma-3-27b-it"
```
> Obtain the api key from https://aistudio.google.com/
### Vector DB setup
- Install and setup docker in your computer. Make sure it's working properly before you proceed to the next step.
- Go into the **backend** directory
- Pull the latest qdrant image:
```
docker pull qdrant/qdrant
```
- Start the container in the background:
```
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    --name qdrant-dbserver \
    qdrant/qdrant
```

From now on, 
To see if the container is running you could run:
```
docker ps
```
To stop the container:
```
docker stop qdrant-dbserver
```
To start the container:
```
docker start qdrant-dbserver
```
### Ollama
- Install Ollama on your computer and make sure it's running in the background
- Install the embeddings model
```
ollama pull mxbai-embed-large
```

## Knowledge Base Setup Instructions
Knowledge Base refers to the documents (for now only pdf files) that our bot can know information about. These documents will then be ingested into the vector db, which can be later used to query when running the application. The ingestion of documents will take a while, but the querying is super fast ! Here are the steps you need to follow to get your document ingested:
- Create two new folders named "knowledge_base" and "processed_documents", the files put inside is automatically ignored by git:
```
mkdir knowledge_base
mkdir processed_documents
```
- Inside this directory place your pdf files (Like the regulation documents, curriculum documents, etc)
- Then run the manage_knowledge_base.py file:
```
uv run manage_knowledge_base.py
```
This simple script can help us manage the contents of the vector db. New files can be added and existing vector stores can be deleted !
- When the script starts up, select option 1. Now all the documents would be saved as vector embeddings inside the "qdrant_storage" directory. You will be able to see the progress. Be patient, it might take quite a while to finish. 
- After it is done notice that the document has been moved to a "processed_documents" folder. This is done to avoid duplicate vector embeddings created everytime.
- U can use the same file to list existing documents and Delete a document too.


> Please ensure that you have ingested atleast one document before you run the server

## Running the server.
> Please run a "uv sync" before you run the backend after update so that the newer dependencies are installed.
- Run the uvicorn server:
```
uv run uvicorn main:app --reload
```

To access the docs:
```
http://127.0.0.1:8000/docs/
```