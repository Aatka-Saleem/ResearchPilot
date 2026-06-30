import os
import sys
from google import genai
from dotenv import load_dotenv

# Ensure project root is in python path to allow importing app module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load env variables for Gemini API key
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

# Import tools and utilities
from app.tools.vector_store import FAISSVectorStore

# Import FastMCP server
from mcp.server.fastmcp import FastMCP

# Instantiate the server
mcp = FastMCP("Research-Pilot-Vault")

# Configuration
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "gemini-embedding-001")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./output")
if not os.path.isabs(OUTPUT_DIR):
    OUTPUT_DIR = os.path.abspath(os.path.join(project_root, OUTPUT_DIR))
INDEX_PREFIX = os.path.join(OUTPUT_DIR, "literature_index")

# Initialize client
client = genai.Client()

def get_vector_store() -> FAISSVectorStore:
    """Helper to initialize and optionally load the existing FAISS index."""
    store = FAISSVectorStore()
    if os.path.exists(f"{INDEX_PREFIX}.index") and os.path.exists(f"{INDEX_PREFIX}.docs.json"):
        store.load(INDEX_PREFIX)
    return store

@mcp.tool()
def add_to_vector_store(chunk_text: str, source_url: str) -> str:
    """Appends a text segment and its metadata to the local FAISS store.

    Args:
        chunk_text: The main text content to index.
        source_url: The source URL or citation path associated with this text.

    Returns:
        A success message or status string.
    """
    try:
        if not chunk_text.strip():
            return "Error: Document text cannot be empty."

        store = get_vector_store()
        
        # Get embedding vector
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=chunk_text
        )
        embedding = response.embeddings[0].values
        
        # Build document text representation with source URL integrated
        formatted_doc = f"{chunk_text}\n[Source: {source_url}]"
        
        store.add_documents([formatted_doc], [embedding])
        store.save(INDEX_PREFIX)
        
        return f"Successfully added chunk. Total documents now: {len(store.documents)}"
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        return f"Error adding to vector store: {repr(e)}"

@mcp.tool()
def query_research_index(query: str) -> str:
    """Queries the local vector database and returns relevant contextual matching text clips.

    Args:
        query: The search query string.

    Returns:
        A string containing matched text segments and source references.
    """
    try:
        store = get_vector_store()
        if not store.documents:
            return "No documents found in the vector index. The store is empty."
            
        # Get embedding for search query
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query
        )
        query_embedding = response.embeddings[0].values
        
        # Query FAISS (pulling top 3 chunks)
        results = store.search(query_embedding, k=3)
        if not results:
            return "No matching documents found in vector index."
            
        formatted_results = []
        for i, res in enumerate(results):
            formatted_results.append(
                f"--- Matches {i+1} (Distance: {res['score']:.4f}) ---\n"
                f"{res['document']}\n"
            )
            
        return "\n".join(formatted_results)
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        return f"Error querying index: {repr(e)}"

if __name__ == "__main__":
    # Runs the stdio MCP server loop
    mcp.run()
