import os
from typing import Any, Dict, List
from google.genai import types
from app.agents.base_agent import BaseAgent
from app.tools.sanitizer import sanitize_text

class ResearchAgent(BaseAgent):
    """Agent focused on literature aggregation using Google Search Grounding."""
    
    def run(self, input_data: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic")
        if not topic:
            raise ValueError("Input data must contain a 'topic' key.")
        
        print(f"[{self.name}] Researching topic: '{topic}' using Google Search Grounding...")
        
        # Ensure model is set to gemini-2.0-flash as required
        self.model = "gemini-2.0-flash"
        
        # Configure Google Search Grounding Tool using official Pydantic schema
        search_tools = [types.Tool(google_search=types.GoogleSearch())]
        
        # Build configuration using our base config helper
        config = self.get_generation_config(tools=search_tools)
        
        prompt = f"Please research the following topic thoroughly and aggregate the key literature and current state: {topic}"
        
        # Call the Google Gen AI client with automatic fallback for quota exhaustion
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
        except Exception as e:
            # Fallback if gemini-2.0-flash quota is exhausted
            if "gemini-2.0-flash" in self.model and ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)):
                print(f"[{self.name}] [Warning] gemini-2.0-flash quota exhausted. Falling back to gemini-2.5-flash...")
                self.model = "gemini-2.5-flash"
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )
            else:
                raise e
        
        # Parse grounding metadata
        search_queries = []
        sources = []
        
        # Google Search grounding metadata is stored on the candidate
        if response.candidates:
            candidate = response.candidates[0]
            metadata = getattr(candidate, "grounding_metadata", None)
            if metadata:
                # Get the actual search queries formulated by the model
                if getattr(metadata, "web_search_queries", None):
                    search_queries = list(metadata.web_search_queries)
                
                # Get the sources utilized by the model
                if getattr(metadata, "grounding_chunks", None):
                    for chunk in metadata.grounding_chunks:
                        if getattr(chunk, "web", None):
                            sources.append({
                                "title": chunk.web.title,
                                "uri": chunk.web.uri
                            })
        
        # Format and sanitize the aggregated report
        raw_text = response.text
        literature_text, was_sanitized = sanitize_text(raw_text)
        if was_sanitized:
            print(f"[{self.name}] [SECURITY WARNING] Malicious patterns were detected and stripped from the text!")
        
        # Generate custom output markdown representing literature findings
        output_dir = os.environ.get("OUTPUT_DIR", "./output")
        os.makedirs(output_dir, exist_ok=True)
        findings_path = os.path.join(output_dir, "research_findings.md")
        
        with open(findings_path, "w", encoding="utf-8") as f:
            f.write(f"# Research Findings: {topic}\n\n")
            f.write(literature_text)
            f.write("\n\n## Search Grounding Meta\n")
            f.write("### Queries Formulated:\n")
            for q in search_queries:
                f.write(f"- `{q}`\n")
            f.write("\n### Sources Cited:\n")
            for src in sources:
                f.write(f"- [{src['title']}]({src['uri']})\n")
                
        print(f"[{self.name}] Completed research. Findings written to: {findings_path}")
        
        return {
            "topic": topic,
            "research_findings_path": findings_path,
            "literature_text": literature_text,
            "search_queries": search_queries,
            "sources": sources
        }
