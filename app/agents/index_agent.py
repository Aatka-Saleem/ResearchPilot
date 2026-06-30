import os
import sys
import asyncio
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.agents.base_agent import BaseAgent

class IndexAgent(BaseAgent):
    """Agent focused on document chunking and indexing via Model Context Protocol (MCP)."""

    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """Splits text into chunks of roughly chunk_size characters with overlap."""
        chunks = []
        if not text:
            return chunks
            
        # Clean text slightly
        text = text.strip()
        
        # Simple sliding window approach
        start = 0
        while start < len(text):
            end = start + chunk_size
            # If we're not at the end of the text, try to align to the end of a sentence or paragraph
            if end < len(text):
                # Look for paragraph break or period nearby to avoid splitting mid-sentence
                limit = max(start + chunk_size // 2, text.rfind("\n", start, end))
                if limit == -1 or limit < start + chunk_size // 2:
                    limit = max(start + chunk_size // 2, text.rfind(". ", start, end))
                if limit != -1 and limit > start + chunk_size // 2:
                    end = limit + 1 # Include the delimiter
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap
            if start >= len(text) or end >= len(text):
                break
                
        return chunks

    async def _index_chunks_via_mcp(self, chunks: List[str], source_url: str) -> List[str]:
        """Launches the MCP server and registers all text chunks in a single session."""
        # Use sys.executable to ensure the server runs in the same virtual environment
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server/server.py"]
        )
        
        results = []
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Handshake
                await session.initialize()
                
                # Register chunks sequentially inside the same active session
                for chunk in chunks:
                    res = await session.call_tool(
                        "add_to_vector_store",
                        arguments={
                            "chunk_text": chunk,
                            "source_url": source_url
                        }
                    )
                    results.append(res.content[0].text)
        return results

    def run(self, input_data: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        literature_text = state.get("literature_text", "")
        if not literature_text:
            findings_path = state.get("research_findings_path")
            if findings_path and os.path.exists(findings_path):
                with open(findings_path, "r", encoding="utf-8") as f:
                    literature_text = f.read()
                    
        if not literature_text:
            raise ValueError("No literature text found in state. Run ResearchAgent first.")

        print(f"[{self.name}] Chunking literature text...")
        chunks = self.chunk_text(literature_text)
        print(f"[{self.name}] Generated {len(chunks)} text chunks.")

        if not chunks:
            raise ValueError("Aggregated text is too short or empty to chunk.")

        # Determine source URL metadata
        sources = state.get("sources", [])
        source_url = "local_findings_file"
        if sources and isinstance(sources, list) and len(sources) > 0:
            # Pick first available web citation
            source_url = sources[0].get("uri", "unknown_source")

        print(f"[{self.name}] Connecting to FastMCP server to add {len(chunks)} chunks...")
        # Execute async MCP client operations in sync context
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            results = loop.run_until_complete(self._index_chunks_via_mcp(chunks, source_url))
        except RuntimeError:
            results = asyncio.run(self._index_chunks_via_mcp(chunks, source_url))
            
        print(f"[{self.name}] FastMCP index operations completed. Registered {len(results)} items.")

        output_dir = os.environ.get("OUTPUT_DIR", "./output")
        index_prefix = os.path.join(output_dir, "literature_index")

        return {
            "vector_index_prefix": index_prefix,
            "chunk_count": len(chunks),
            "mcp_status": "synced"
        }

