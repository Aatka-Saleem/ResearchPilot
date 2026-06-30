import os
from typing import Any, Dict
from google import genai
from google.genai import types

class BaseAgent:
    """Base class for all research-pilot agents."""
    def __init__(self, agent_id: str, config_data: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = config_data.get("name", agent_id)
        self.description = config_data.get("description", "")
        self.model = config_data.get("model", "gemini-2.5-flash")
        self.system_instruction = config_data.get("system_instruction", "")
        
        agent_config = config_data.get("config", {})
        self.temperature = agent_config.get("temperature", 0.2)
        self.max_output_tokens = agent_config.get("max_output_tokens", 8192)
        self.tools_list = config_data.get("tools", [])
        
        # Initialize Google Gen AI Client
        # It will automatically pick up GEMINI_API_KEY from the environment.
        self.client = genai.Client()

    def get_generation_config(self, tools: list = None) -> types.GenerateContentConfig:
        """Helper to build GenerateContentConfig with agent's default settings."""
        return types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            tools=tools
        )

    def run(self, input_data: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the agent's step in the pipeline.
        
        Args:
            input_data: Input specific to this run (e.g. prompt, topic, etc.)
            state: The shared orchestration state.
            
        Returns:
            Dict containing the output of this agent's run to be merged into the state.
        """
        raise NotImplementedError("Subclasses must implement the run method.")
