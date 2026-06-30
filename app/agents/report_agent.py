import os
import sys
import asyncio
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.agents.base_agent import BaseAgent
from app.tools.pptx_generator import create_presentation

# Define Pydantic models for structured slide deck generation
class Slide(BaseModel):
    title: str = Field(description="The heading or title of the slide.")
    content: List[str] = Field(description="Bullet points or lines of text on the slide. Keep items concise, maximum 4-5 items.")
    is_title: bool = Field(default=False, description="Set to True if this is the title slide of the deck.")

class PresentationDeck(BaseModel):
    slides: List[Slide] = Field(description="Ordered list of slides in the presentation deck.")

class ReportAgent(BaseAgent):
    """Agent focused on generating markdown reports and pptx slides using context retrieved from an MCP server."""

    async def _query_mcp_research_index(self, sub_queries: List[str]) -> List[str]:
        """Launches the FastMCP server and calls query_research_index for each sub-query.
        
        Args:
            sub_queries: List of search query strings to send to the vector store.
            
        Returns:
            A list of matching text chunks returned by the MCP tool.
        """
        # Run using same python environment executable to avoid module path issues
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server/server.py"]
        )
        
        results = []
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Handshake
                await session.initialize()
                
                # Fetch matching records from vector index for each query
                for query in sub_queries:
                    res = await session.call_tool(
                        "query_research_index",
                        arguments={"query": query}
                    )
                    results.append(res.content[0].text)
        return results

    def _validate_citations(self, report_text: str, index_prefix: str) -> tuple[str, bool]:
        """Programmatically cross-references markdown links against the FAISS index to prevent hallucinations.
        
        Args:
            report_text: The raw generated markdown report.
            index_prefix: Path prefix to the local FAISS index metadata.
            
        Returns:
            A tuple of (sanitized_report_text, was_hallucinated) where:
                sanitized_report_text: Report text with hallucinated citations flagged.
                was_hallucinated: Boolean indicating if a hallucination was blocked.
        """
        import re
        import json
        
        docs_path = f"{index_prefix}.docs.json"
        if not os.path.exists(docs_path):
            return report_text, False
            
        try:
            with open(docs_path, "r", encoding="utf-8") as f:
                raw_chunks = json.load(f)
        except Exception:
            return report_text, False
            
        corpus = "\n".join(raw_chunks).lower()
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', report_text)
        
        cleaned_text = report_text
        hallucination_detected = False
        
        for title, uri in links:
            # Skip anchor or local file links
            if uri.startswith("#") or uri.startswith("file://") or uri.startswith("."):
                continue
                
            # Cross-reference URL against vector index chunks
            if uri.lower() not in corpus:
                print(f"[SECURITY WARNING] Hallucinated citation detected and blocked: {uri}")
                # Replace with flagged placeholder
                cleaned_text = cleaned_text.replace(f"[{title}]({uri})", f"{title} [Hallucination Blocked: Source URL not found in references]")
                hallucination_detected = True
                
        return cleaned_text, hallucination_detected

    def run(self, input_data: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        topic = state.get("topic")
        index_prefix = state.get("vector_index_prefix")
        
        if not topic or not index_prefix:
            raise ValueError("State must contain 'topic' and 'vector_index_prefix'. Run ResearchAgent and IndexAgent first.")
            
        # 1. Generate search queries to gather index context
        sub_queries = [
            f"Core concepts, definitions, and applications of {topic}",
            f"Challenges, limitations, and future outlook of {topic}",
            f"Recent news, advancements, and developments in {topic}"
        ]
        
        print(f"[{self.name}] Formulating sub-queries for vector search: {sub_queries}")
        print(f"[{self.name}] Connecting to FastMCP server to query vector store...")
        
        # Run async MCP communication inside the sync workflow
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio
            nest_asyncio.apply()
            retrieved_contexts = loop.run_until_complete(self._query_mcp_research_index(sub_queries))
        except RuntimeError:
            retrieved_contexts = asyncio.run(self._query_mcp_research_index(sub_queries))
            
        # Join retrieved contexts with clear boundaries
        combined_context = "\n\n---\n\n".join(retrieved_contexts)
        print(f"[{self.name}] Retrieved matching context clips from FastMCP server.")
        
        # 2. Generate Executive Markdown Summary
        print(f"[{self.name}] Synthesizing executive report in markdown...")
        report_prompt = f"""
Using the retrieved literature context below, write a comprehensive, professional executive summary about '{topic}'.
Structure the report using appropriate headings (H1, H2, H3), bullet points, and sections for overview, core findings, key challenges, and future outlook.

Retrieved Context:
{combined_context}
"""
        report_config = self.get_generation_config()
        report_response = self.client.models.generate_content(
            model=self.model,
            contents=report_prompt,
            config=report_config
        )
        
        output_dir = os.environ.get("OUTPUT_DIR", "./output")
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, "executive_report.md")
        
        # Apply output guardrail citation validator
        validated_text, was_hallucinated = self._validate_citations(report_response.text, index_prefix)
        if was_hallucinated:
            print(f"[{self.name}] [SECURITY ALERT] Hallucinated citations were detected and replaced with placeholders.")
            
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(validated_text)
            
        print(f"[{self.name}] Executive report saved to: {report_path}")
        
        # 3. Generate Presentation Slide data using Structured Outputs
        print(f"[{self.name}] Generating structured slide outline...")
        slides_prompt = f"""
Using the retrieved context and the executive summary, create a slide deck outline for '{topic}'.
Provide:
1. A Title Slide (is_title=True)
2. At least 3-4 content slides covering background, key findings, challenges, and conclusions.

Retrieved Context:
{combined_context}
"""
        slides_config = self.get_generation_config()
        slides_config.response_mime_type = "application/json"
        slides_config.response_schema = PresentationDeck
        
        slides_response = self.client.models.generate_content(
            model=self.model,
            contents=slides_prompt,
            config=slides_config
        )
        
        # Parse Pydantic response
        deck_data: PresentationDeck = slides_response.parsed
        
        # Format slides for generator
        slide_list = []
        for slide in deck_data.slides:
            slide_list.append({
                "title": slide.title,
                "content": slide.content,
                "is_title": slide.is_title
            })
            
        pptx_path = os.path.join(output_dir, "executive_presentation.pptx")
        create_presentation(slide_list, pptx_path)
        
        print(f"[{self.name}] Executive presentation slide deck saved to: {pptx_path}")
        
        return {
            "executive_report_path": report_path,
            "executive_presentation_path": pptx_path,
            "slide_count": len(slide_list)
        }

