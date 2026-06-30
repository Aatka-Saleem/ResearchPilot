import os
import sys
import argparse
import asyncio
from typing import List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ensure project root is in python path to allow importing app module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import chunker from IndexAgent
from app.agents.index_agent import IndexAgent

async def send_to_mcp(chunks: List[str], source_url: str):
    """Connects to the FastMCP server and indexes the text chunks.
    
    Args:
        chunks: List of text chunk segments to upload.
        source_url: Source URL or citation path for metadata tracking.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server/server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for chunk in chunks:
                res = await session.call_tool(
                    "add_to_vector_store",
                    arguments={"chunk_text": chunk, "source_url": source_url}
                )
                print(f"[build_index] Server Response: {res.content[0].text}")

def main():
    parser = argparse.ArgumentParser(description="Build FAISS vector index via FastMCP server")
    parser.add_argument("--file", type=str, required=True, help="Path to text file containing research text")
    parser.add_argument("--url", type=str, default="local_file", help="Source URL or citation path")
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File not found {args.file}")
        sys.exit(1)
        
    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()
        
    # We construct a mock agent config to instantiate the chunker
    agent = IndexAgent("IndexAgent", {})
    chunks = agent.chunk_text(text)
    
    print(f"Read file: {args.file}. Chunks generated: {len(chunks)}")
    asyncio.run(send_to_mcp(chunks, args.url))
    print("Indexing completed successfully.")

if __name__ == "__main__":
    main()
