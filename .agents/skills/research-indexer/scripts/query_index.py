import os
import sys
import argparse
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ensure project root is in python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def query_mcp(query: str):
    """Launches the FastMCP server subprocess and queries the vector index.
    
    Args:
        query: The search query string.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server/server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool(
                "query_research_index",
                arguments={"query": query}
            )
            print(res.content[0].text)

def main():
    parser = argparse.ArgumentParser(description="Query FAISS vector index via FastMCP server")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    args = parser.parse_args()
    
    print(f"Querying index for: '{args.query}'...")
    asyncio.run(query_mcp(args.query))

if __name__ == "__main__":
    main()
