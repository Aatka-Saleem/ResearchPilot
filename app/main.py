import os
import sys
import argparse
from dotenv import load_dotenv
from app.orchestrator import AgentOrchestrator

def main():
    # Load environment variables from .env
    load_dotenv()
    
    # Verify GEMINI_API_KEY is present
    if not os.environ.get("GEMINI_API_KEY"):
        print("[Error] GEMINI_API_KEY environment variable is not set.")
        print("Please create a '.env' file based on '.env.example' and add your API key.")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="Research Pilot - Multi-Agent Research Orchestrator")
    parser.add_argument(
        "--topic", 
        type=str, 
        default="Next-generation solid state battery technology for electric vehicles",
        help="The research query/topic for literature aggregation and indexing."
    )
    args = parser.parse_args()
    
    # Initialize and execute orchestrator workflow
    orchestrator = AgentOrchestrator()
    try:
        final_state = orchestrator.run_workflow(args.topic)
        
        print("Workflow Executed Successfully! Output Files generated:")
        print(f"1. Research Findings: {final_state.get('research_findings_path')}")
        print(f"2. Executive Report: {final_state.get('executive_report_path')}")
        print(f"3. Slide Deck: {final_state.get('executive_presentation_path')}")
    except Exception as e:
        print(f"[Error] Workflow failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
