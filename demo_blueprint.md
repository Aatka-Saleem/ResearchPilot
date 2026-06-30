# Hackathon Video Demo Blueprint (demo_blueprint.md)

This blueprint outlines the visual onboarding checklist and a minute-by-minute presentation script for a **5-minute hackathon video demo** to maximize technical points from the Kaggle judges.

---

## 📺 Visual Onboarding Checklist (Files to Show On-Screen)

1. 📂 **Topology Config**: [app/agents.json](file:///C:/Users/aatka/research-pilot/app/agents.json)
   * Highlight the separation of parameters and models (e.g. `gemini-2.0-flash` for the grounded ResearchAgent).
2. 🔌 **Process Decoupling**: [mcp_server/server.py](file:///C:/Users/aatka/research-pilot/mcp_server/server.py)
   * Show how FastMCP exposes standard Python tools (`add_to_vector_store`, `query_research_index`) over standard input/output channels.
3. 🛡️ **Active Sanitizer**: [app/tools/sanitizer.py](file:///C:/Users/aatka/research-pilot/app/tools/sanitizer.py)
   * Point out the pre-indexing regex scanner that strips jailbreak override vectors.
4. 🔎 **Anti-Hallucination Guardrails**: [app/agents/report_agent.py](file:///C:/Users/aatka/research-pilot/app/agents/report_agent.py#L53-L98)
   * Highlight the `_validate_citations` programmatic checker that cross-references output markdown URLs against the local FAISS index metadata.
5. 🐳 **Deployability**: [Dockerfile](file:///C:/Users/aatka/research-pilot/Dockerfile) & [deploy.sh](file:///C:/Users/aatka/research-pilot/deploy.sh)
   * Point out the multi-stage caching, the non-root runner user, and the Secret Manager integration (no API key baking).
6. 🎯 **Verification**: Terminal showing test outputs (`uv run python -m unittest discover -s tests`).

---

## ⏱️ Minute-by-Minute Presentation Script Outline

### 0:00 - 0:45 | Introduction & Architecture
* **Narrator Focus**: State the core researcher cognitive overload problem and explain why standard single-agent loops are highly vulnerable to Indirect Prompt Injections (scraped text altering model execution context).
* **On-Screen Visual**: Show the [README.md](file:///C:/Users/aatka/research-pilot/README.md) file, displaying the multi-agent Mermaid tracking diagram to illustrate modular separation.

### 0:45 - 1:45 | Declarative Registry & FastMCP Vault
* **Narrator Focus**: Show how the system config file decouples model configurations and system instructions. Explain how the FastMCP server handles embeddings and vector storage on a separate isolated process boundary.
* **On-Screen Visual**: Show [app/agents.json](file:///C:/Users/aatka/research-pilot/app/agents.json) and [mcp_server/server.py](file:///C:/Users/aatka/research-pilot/mcp_server/server.py). Show the transition from local FAISS references inside the agents to standard JSON-RPC tool calls.

### 1:45 - 2:45 | Input Sanitizer Defense (Day 4 Security)
* **Narrator Focus**: Explain how we prevent malicious web data from injecting overrides into our pipeline. Staging scraped text is sanitized line-by-line using regular expressions to strip out commands before indexing.
* **On-Screen Visual**: Scroll through [app/tools/sanitizer.py](file:///C:/Users/aatka/research-pilot/app/tools/sanitizer.py) and show where it is integrated in [app/agents/research_agent.py](file:///C:/Users/aatka/research-pilot/app/agents/research_agent.py).

### 2:45 - 3:45 | Citation Validator (Anti-Hallucination Guard)
* **Narrator Focus**: Detail the output validation layer. Show how generated Markdown reports are examined for reference links, verifying them against the actual FAISS index database document chunks to guarantee absolute factual backing.
* **On-Screen Visual**: Scroll through `_validate_citations` in [app/agents/report_agent.py](file:///C:/Users/aatka/research-pilot/app/agents/report_agent.py). Explain the placeholder substitution for hallucinated URIs.

### 3:45 - 5:00 | Docker Sync, Deployment & Test Run
* **Narrator Focus**: Highlight production readiness. Explain the multi-stage Docker build utilizing uv caching and GCP Secret Manager bindings at runtime. End by running the test suite to prove compilation success.
* **On-Screen Visual**: Show [Dockerfile](file:///C:/Users/aatka/research-pilot/Dockerfile) and [deploy.sh](file:///C:/Users/aatka/research-pilot/deploy.sh), then execute `uv run python -m unittest discover -s tests` live in the terminal.
