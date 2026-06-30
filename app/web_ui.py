import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is in python path to allow importing app module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load env variables
load_dotenv(os.path.join(project_root, ".env"))

from app.orchestrator import AgentOrchestrator
from app.tools.sanitizer import sanitize_text

# Page Configuration
st.set_page_config(
    page_title="ResearchPilot AI — Secure Literature Synthesis Swarm",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS injection for premium aesthetics
st.markdown("""
<style>
    /* Styling headers & gradient backgrounds */
    .title-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    }
    .title-text {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #94a3b8;
    }
    /* Styling for action buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }
</style>
""", unsafe_allow_html=True)

# Main Page Layout
st.markdown("""
<div class="title-container">
    <div class="title-text">🧬 ResearchPilot AI</div>
    <div class="subtitle-text">Secure Multi-Agent Literature Synthesis Swarm & Vector Indexing Pipeline</div>
</div>
""", unsafe_allow_html=True)

# Sidebar configurations and telemetry
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=80)
    st.markdown("### 🛠️ System Telemetry & Configuration")
    
    st.markdown("#### 🤖 Models Configured")
    st.info(f"**Generative Model:** `{os.environ.get('DEFAULT_MODEL', 'gemini-2.5-flash')}`\n\n**Embedding Model:** `{os.environ.get('EMBEDDING_MODEL', 'gemini-embedding-001')}`")
    
    st.markdown("#### 🛡️ Active Security Guardrails")
    st.success("🔒 Input Sanitization Interceptor\n\n📂 Adversarial Prompt Validator\n\n🔗 Citation Hallucination Check")
    
    st.markdown("---")
    st.caption("Powered by Google Gen AI SDK & FastMCP Vault Server.")

# Columns for parameters and control
col_input, col_info = st.columns([2, 1])

with col_input:
    user_topic = st.text_input(
        "Enter target research topic/query:",
        value="RAG Evaluation Frameworks and ROUGE/BLEU limitations",
        placeholder="e.g. Quantum Computing algorithms, RAG Architectures..."
    )
    
    start_pipeline = st.st_button = st.button("Generate Research Assets 🚀")

with col_info:
    st.markdown("""
    #### 📦 Deliverables Produced:
    - **Scraped Findings**: Raw literature aggregated via Google Search Grounding.
    - **Vector Index**: Semantic vector database (FAISS) mapped via FastMCP.
    - **Executive Report**: Structured analysis with verified citations.
    - **Presentation Slides**: Clean PPTX widescreen slide deck.
    """)

# Output directory configuration
output_dir = os.environ.get("OUTPUT_DIR", "./output")
os.makedirs(output_dir, exist_ok=True)
report_path = os.path.join(output_dir, "executive_report.md")
pptx_path = os.path.join(output_dir, "executive_presentation.pptx")
findings_path = os.path.join(output_dir, "research_findings.md")

if start_pipeline:
    if not user_topic.strip():
        st.error("Please enter a valid research topic.")
    else:
        # Run local sanitization check before initiating workflow
        sanitized_topic, was_flagged = sanitize_text(user_topic)
        if was_flagged:
            st.warning("⚠️ Input topic matched a potential jailbreak or override pattern. Malicious phrases were sanitized.")
            
        # Execute workflow within Streamlit Status container
        with st.status("Executing Multi-Agent Workflow...", expanded=True) as status:
            try:
                status.write("🛡️ Step 1: Input text sanitization completed.")
                
                # Load declarative orchestrator
                status.write("🧬 Step 2: Instantiating Multi-Agent Swarm Registry...")
                orchestrator = AgentOrchestrator()
                state = {"topic": sanitized_topic}
                
                # 1. Literature Aggregator
                status.write("🔍 Step 3: Launching Literature Aggregator (ResearchAgent)...")
                research_agent = orchestrator.agents["ResearchAgent"]
                research_output = research_agent.run({"topic": sanitized_topic}, state)
                state.update(research_output)
                status.write(f"✅ Literature Aggregator finished. Output saved to {findings_path}.")
                
                # 2. Vector Indexer
                status.write("🗂️ Step 4: Initializing Vector Indexer (IndexAgent)...")
                status.write("   - Starting FastMCP subprocess server and embedding chunks...")
                index_agent = orchestrator.agents["IndexAgent"]
                index_output = index_agent.run({"topic": sanitized_topic}, state)
                state.update(index_output)
                status.write("✅ Vector Indexer registered chunks to FAISS index.")
                
                # 3. Executive Reporter
                status.write("✍️ Step 5: Invoking Executive Reporter (ReportAgent)...")
                status.write("   - Performing citation checks and rendering slide deck...")
                report_agent = orchestrator.agents["ReportAgent"]
                report_output = report_agent.run({"topic": sanitized_topic}, state)
                state.update(report_output)
                status.write("✅ Executive Reporter compiled report and presentation deck.")
                
                status.update(label="🎉 Asset Generation Succeeded!", state="complete", expanded=False)
                st.success("Execution Completed Successfully! Check outputs below.")
                
            except Exception as e:
                status.update(label="❌ Workflow Execution Failed", state="error")
                st.error(f"Error executing multi-agent pipeline: {e}")

# Render generated output reports and download blocks
if os.path.exists(report_path):
    st.markdown("---")
    st.markdown("### 📝 Synthesized Executive Report")
    
    with open(report_path, "r", encoding="utf-8") as f:
        report_md = f.read()
        
    st.markdown(report_md)
    
    # Download actions
    st.markdown("#### 📥 Download Assets")
    col_dl_md, col_dl_pptx = st.columns(2)
    
    with col_dl_md:
        st.download_button(
            label="Download Markdown Report (.md) 📝",
            data=report_md,
            file_name="executive_report.md",
            mime="text/markdown"
        )
        
    if os.path.exists(pptx_path):
        with open(pptx_path, "rb") as f:
            pptx_bytes = f.read()
            
        with col_dl_pptx:
            st.download_button(
                label="Download Slide Deck Presentation (.pptx) 📊",
                data=pptx_bytes,
                file_name="executive_presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
else:
    st.info("No research assets generated yet. Enter a topic above and click the button to generate.")
