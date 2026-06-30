import os
import json
from typing import Dict, Any, List
from app.agents.research_agent import ResearchAgent
from app.agents.index_agent import IndexAgent
from app.agents.report_agent import ReportAgent

class AgentOrchestrator:
    """Manages agent loading, topology definition, and sequential workflow execution."""
    
    def __init__(self, config_path: str = "app/agents.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.agents: Dict[str, Any] = {}
        self._initialize_agents()

    def _load_config(self) -> Dict[str, Any]:
        """Loads declarative agents topology config from JSON."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _initialize_agents(self):
        """Dynamically registers agent modules based on ecosystem config."""
        agent_classes = {
            "ResearchAgent": ResearchAgent,
            "IndexAgent": IndexAgent,
            "ReportAgent": ReportAgent
        }
        
        for agent_data in self.config.get("agents", []):
            agent_id = agent_data.get("id")
            if agent_id in agent_classes:
                # Instantiate agent with its specific config segment
                self.agents[agent_id] = agent_classes[agent_id](agent_id, agent_data)
                print(f"[Orchestrator] Registered agent: {agent_id} - '{agent_data.get('name')}'")
            else:
                print(f"[Orchestrator] Warning: Class not found for agent ID '{agent_id}'")

    def run_workflow(self, topic: str) -> Dict[str, Any]:
        """Runs the multi-agent pipeline sequentially: Research -> Index -> Report.
        
        Args:
            topic: The research query/topic.
            
        Returns:
            The final combined state dictionary.
        """
        print("\n" + "="*60)
        print(f"[Orchestrator] Initializing multi-agent pipeline for: '{topic}'")
        print("="*60 + "\n")
        
        # Shared orchestration state
        state: Dict[str, Any] = {
            "topic": topic
        }
        
        # Sequential pipeline execution
        sequence = ["ResearchAgent", "IndexAgent", "ReportAgent"]
        
        for agent_id in sequence:
            if agent_id not in self.agents:
                raise ValueError(f"Required agent '{agent_id}' is not initialized.")
            
            agent = self.agents[agent_id]
            print(f"[Orchestrator] Starting Agent: {agent.name}...")
            
            # Execute step and retrieve output dict
            agent_output = agent.run({"topic": topic}, state)
            
            # Merge outputs into global state for subsequent agents
            state.update(agent_output)
            print(f"[Orchestrator] Completed Agent: {agent.name}\n")
            
        print("="*60)
        print("[Orchestrator] Multi-agent orchestration pipeline finished.")
        print("="*60 + "\n")
        
        return state
