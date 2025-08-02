import os
import qdrant_client
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.readers.file import UnstructuredReader
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from qdrant_client.http import models as rest

console = Console()

def setup_environment():
    """Loads environment variables and configures LlamaIndex settings."""
    load_dotenv()

    Settings.embed_model = OllamaEmbedding(
        model_name=os.getenv("EMBED_MODEL_NAME"),
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )

def get_vector_store() -> QdrantVectorStore:
    """Initializes and returns the Qdrant vector store."""
    client = qdrant_client.QdrantClient(url=os.getenv("QDRANT_URL"))
    return QdrantVectorStore(
        client=client, collection_name=os.getenv("QDRANT_COLLECTION_NAME")
    )

def ingest_documents():
    """Ingests documents from the 'knowledge_base' directory."""
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    data_dir = "knowledge_base"
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        console.print(f"[bold yellow]Warning:[/bold yellow] The '{data_dir}' directory is empty. No documents to ingest.")
        return

    console.print(f"[bold green]Ingesting documents from '{data_dir}'...[/bold green]")

   # 1. Define a file extractor that maps the .pdf extension to the UnstructuredReader.
    file_extractor = {
        ".pdf": UnstructuredReader(),
    }
    
    # 2. Use SimpleDirectoryReader to scan the directory, but pass in the custom file_extractor.
    # The reader's keyword argument is 'input_dir'.
    documents = SimpleDirectoryReader(
        input_dir=data_dir, 
        file_extractor=file_extractor
    ).load_data()


    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True
    )

    console.print("[bold green]✅ Ingestion complete![/bold green]")
    
    processed_dir = "processed_documents"
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    console.print("Moving processed files to 'processed_documents'...")
    for doc in os.listdir(data_dir):
        source_path = os.path.join(data_dir, doc)
        destination_path = os.path.join(processed_dir, doc)
        os.rename(source_path, destination_path)
        console.print(f"- Moved {doc}")


def list_documents():
    """Lists all unique documents currently in the vector store."""
    console.print("[bold blue]Fetching documents from the knowledge base...[/bold blue]")
    client = qdrant_client.QdrantClient(url=os.getenv("QDRANT_URL"))
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    try:
        response = client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        
        records = response[0]
        if not records:
            console.print("[yellow]No documents found in the knowledge base.[/yellow]")
            return

        unique_files = sorted(list({
            record.payload['file_name'] 
            for record in records if 'file_name' in record.payload
        }))

        if not unique_files:
            console.print("[yellow]Found data in the knowledge base, but could not extract filenames.[/yellow]")
            return

        table = Table(title="Documents in Knowledge Base")
        table.add_column("Filename", justify="left", style="cyan", no_wrap=True)
        for filename in unique_files:
            table.add_row(filename)
        
        console.print(table)

    except Exception as e:
        if "not found" in str(e).lower():
            console.print("[yellow]Knowledge base is empty. Ingest some documents first.[/yellow]")
        else:
            console.print(f"[bold red]Error:[/bold red] Could not connect to Qdrant or collection does not exist. Details: {e}")



def delete_document():
    """Deletes a document and its associated vectors from the store."""
    client = qdrant_client.QdrantClient(url=os.getenv("QDRANT_URL"))
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    filename = Prompt.ask("[bold yellow]Enter the exact filename to delete (e.g., 'document.pdf')[/bold yellow]")

    if not filename:
        console.print("[bold red]Error:[/bold red] Filename cannot be empty.")
        return

    console.print(f"Attempting to delete '{filename}' from the knowledge base...")
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=rest.FilterSelector(
                filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="file_name",
                            match=rest.MatchValue(value=filename),
                        ),
                    ],
                )
            ),
        )
        console.print(f"[bold green]✅ Successfully deleted all entries for '{filename}'.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error during deletion:[/bold red] {e}")


def main():
    setup_environment()
    while True:
        console.print(Panel(
            "[bold cyan]Knowledge Base Management CLI[/bold cyan]\n\n[1] Ingest New Documents\n[2] List Existing Documents\n[3] Delete a Document\n[4] Exit",
            title="Menu",
            border_style="blue"
        ))
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="4")

        if choice == "1":
            ingest_documents()
        elif choice == "2":
            list_documents()
        elif choice == "3":
            delete_document()
        elif choice == "4":
            console.print("[bold magenta]Goodbye![/bold magenta]")
            break

        console.print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold magenta]Exiting program.[/bold magenta]")