<div align="center">
  <img src="https://img.shields.io/badge/Google%20AI%20SDK-v0.1.0-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google GenAI SDK" />
  <img src="https://img.shields.io/badge/Model%20Context%20Protocol-FastMCP-34A853?style=for-the-badge&logo=python&logoColor=white" alt="MCP Server" />
  <img src="https://img.shields.io/badge/Environment-uv%20manager-FF6F61?style=for-the-badge" alt="UV Package Manager" />
  <img src="https://img.shields.io/badge/Security-Day_4_Sanitizer-EA4335?style=for-the-badge" alt="Security Layer" />
  
  <br />
  <h1 align="center">🚀 ResearchPilot AI 🚀</h1>
  <p align="center"><strong>Secure Multi-Agent Literature Aggregator & Secured Indexer Swarm</strong></p>
  <p align="center"><em>Defending Enterprise Analytics against Indirect Prompt Injections and Hallucinations using Decoupled FastMCP Subprocesses.</em></p>
  
  <a href="https://github.com/[your-username]/research-pilot"><strong>Explore the Repository »</strong></a>
</div>

---

## 📌 Project Overview

**ResearchPilot AI** is a production-grade multi-agent knowledge extraction system built for the *Kaggle 5-Day AI Agents Intensive Course with Google*. 

The application streamlines corporate literature compilation and market synthesis by automating data aggregation, vector database embedding, and presentation compiling. Crucially, ResearchPilot introduces robust architectural defense boundaries designed to capture **Indirect Prompt Injections** and eliminate **Model Hallucinations** before they reach downstream enterprise assets.

### 🌟 Key Enhancements:
* 🤖 **Declarative Multi-Agent Topology (`app/agents.json`)**: Modular separation of execution profiles using the unified `google-genai` SDK.
* ⚡ **Decoupled FastMCP Vault Server (`mcp_server/server.py`)**: Isolation of sensitive data operations using high-speed standard input/output (`stdio`) JSON-RPC communication channels.
* 🛡️ **Input/Output Security Layers**: Real-time script regex sanitizer matching and mathematical citation-URL validation loops.
* 📊 **Widescreen PPTX Artifact Engine**: Direct generation of stylized 10-slide PowerPoint slide decks leveraging strict structured data tracking models.
* 🎨 **Streamlit Web Dashboard**: A fluid local UI that bridges complex multi-process background tasks onto a consumer-facing browser setup.

---

## 📊 Core Swarm Architecture

ResearchPilot completely separates operational concerns. Instead of relying on a fragile single-agent chat setup, the system orchestrates a clean sequence of specialized node steps running inside strict environment bubbles:

```mermaid
graph TD
    User([User Target Topic]) --> Main[app/main.py Entrypoint]
    Main -->|Pipes Topic| RA[ResearchAgent]
    RA -->|Gemini 2.5 Flash Web Grounding| GoogleSearch[Google Search Grounding Engine]
    GoogleSearch -->|Raw Ingested Strings| Sanitizer[app/tools/sanitizer.py Preprocessor]
    
    Sanitizer -->|Scans line-by-line via Regex| Check{Adversarial injection vector?}
    Check -->|Yes| Strip[Strip overrides & Log Security Warning]
    Check -->|No| IA[IndexAgent]
    Strip --> IA
    
    IA -->|Launches stdio subprocess| MCP[FastMCP Vault Server]
    MCP -->|Embeds & indexes data| FAISS[(Local FAISS Vector Index)]
    
    Main -->|Pipes Index Keys| ROA[ReportAgent]
    ROA -->|Queries context over stdio channel| MCP
    MCP -->|Returns top L2 vector matches| ROA
    
    ROA -->|Compiles raw markdown| OutputReport[Raw Inferences]
    OutputReport -->|Programmatically cross-references links| Guardrail[ReportAgent._validate_citations]
    Guardrail -->|Redacts phantom URLs| FinalReport[output/executive_report.md]
    
    ROA -->|Builds design data layout| SlideGen[app/tools/pptx_generator.py]
    SlideGen -->|Writes binary| FinalPPTX[output/executive_presentation.pptx]
## 💻 Codebase Anatomy

research-pilot/
├── packages.txt              # Linux system dependencies for Cloud Environment hooks
├── pyproject.toml           # Project definitions, tracking hooks, and UV constraints
├── mcp_server/
│   └── server.py            # Isolated FastMCP database tool provider server
├── app/
│   ├── agents.json          # Declarative multi-agent system instructions registry
│   ├── web_ui.py            # Beautiful Streamlit dashboard front-end interface
│   ├── orchestrator.py      # Core sequential pipeline orchestration engine
│   ├── agents/
│   │   ├── base_agent.py    # Common agent constructor class
│   │   ├── research_agent.py# Web-grounded collection agent with 429 model fallback
│   │   ├── index_agent.py   # Parameter-passing vector pipeline execution node
│   │   └── report_agent.py  # Fact retrieval engine with programmatic citation check
│   └── tools/
│       ├── sanitizer.py     # Prompt-injection scanning preprocessor hook
│       ├── vector_store.py  # High-density local FAISS matrix configuration wrapper
│       └── pptx_generator.py# Automated python-pptx widescreen slide styling engine
└── output/
    ├── research_findings.md # Intermediary grounded web gathering database logs
    ├── executive_report.md  # Final secure, validated markdown research synthesis
    └── executive_presentation.pptx # Generated professional 10-slide corporate presentation


Clone the Repository:
