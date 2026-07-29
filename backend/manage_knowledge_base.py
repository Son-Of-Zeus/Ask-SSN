import os
from pathlib import Path

import qdrant_client
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from llama_index.core import Settings, VectorStoreIndex, Document
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding

from docling_parse.pdf_parser import DoclingPdfParser, PdfDocument
from docling_core.types.doc.page import TextCellUnit

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


def parse_pdf_with_docling(pdf_path: str) -> PdfDocument:
    """Load a PDF into a Docling PdfDocument."""
    parser = DoclingPdfParser()
    pdf_doc: PdfDocument = parser.load(path_or_stream=pdf_path)
    return pdf_doc


def extract_page_texts(pdf_doc: PdfDocument):
    """
    Yield per-page text using Docling-Parse.
    Strategy:
    - Iterate pages with pdf_doc.iterate_pages()
    - For each page, concatenate WORD-level cells in reading order.
    """
    for page_no, page in pdf_doc.iterate_pages():
        # Accumulate words in order; fallback to CHAR/LINE if desired
        words = []
        for cell in page.iterate_cells(unit_type=TextCellUnit.WORD):
            # cell.text is a string; filter empty
            t = (cell.text or "").strip()
            if t:
                words.append(t)
        text = " ".join(words).strip()
        yield page_no, text


def ingest_documents_with_docling_by_page():
    """Ingest PDFs from 'knowledge_base' using Docling-Parse with page-level chunks."""
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    data_dir = "knowledge_base"
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        console.print(f"[bold yellow]Warning:[/bold yellow] The '{data_dir}' directory is empty. No documents to ingest.")
        return

    console.print(f"[bold green]Ingesting documents (page chunks) from '{data_dir}' with Docling-Parse...[/bold green]")

    documents: list[Document] = []
    for entry in sorted(os.listdir(data_dir)):
        if not entry.lower().endswith(".pdf"):
            continue
        file_path = os.path.join(data_dir, entry)

        try:
            pdf_doc = parse_pdf_with_docling(file_path)
            page_chunks = 0
            for page_no, page_text in extract_page_texts(pdf_doc):
                if not page_text:
                    continue
                documents.append(
                    Document(
                        text=page_text,
                        metadata={
                            "file_name": entry,
                            "page_label": str(page_no),
                        },
                    )
                )
                page_chunks += 1

            if page_chunks == 0:
                console.print(f"[yellow]- Skipped {entry}: no text content found[/yellow]")
            else:
                console.print(f"- Parsed {entry} ({page_chunks} page chunks)")

        except Exception as e:
            console.print(f"[red]- Failed {entry}:[/red] {e}")

    if not documents:
        console.print("[yellow]No documents parsed. Nothing to index.[/yellow]")
        return

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    console.print("[bold green]✅ Ingestion complete![/bold green]")

    processed_dir = "processed_documents"
    os.makedirs(processed_dir, exist_ok=True)
    console.print("Moving processed files to 'processed_documents'...")
    for doc in os.listdir(data_dir):
        source_path = os.path.join(data_dir, doc)
        destination_path = os.path.join(processed_dir, doc)
        try:
            os.rename(source_path, destination_path)
            console.print(f"- Moved {doc}")
        except Exception as e:
            console.print(f"[yellow]- Could not move {doc}:[/yellow] {e}")


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
            with_vectors=False,
        )
        records = response[0]
        if not records:
            console.print("[yellow]No documents found in the knowledge base.[/yellow]")
            return

        unique_files = sorted(
            list({record.payload["file_name"] for record in records if "file_name" in record.payload})
        )

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
        from qdrant_client.http import models as rest

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
        console.print(
            Panel(
                "[bold cyan]Knowledge Base Management CLI[/bold cyan]\n\n[1] Ingest New Documents (Docling - page chunks)\n[2] List Existing Documents\n[3] Delete a Document\n[4] Exit",
                title="Menu",
                border_style="blue",
            )
        )
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="4")

        if choice == "1":
            ingest_documents_with_docling_by_page()
        elif choice == "2":
            list_documents()
        elif choice == "3":
            delete_document()
        elif choice == "4":
            console.print("[bold magenta]Goodbye![/bold magenta]")
            break

        console.print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold magenta]Exiting program.[/bold magenta]")
