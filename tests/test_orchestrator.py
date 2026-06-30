import os
import unittest
from app.orchestrator import AgentOrchestrator

class TestAgentOrchestrator(unittest.TestCase):
    def setUp(self):
        # We need to make sure we are referencing the correct path for app/agents.json
        # When running tests, the working directory is usually the root of the project
        self.config_path = "app/agents.json"
        
    def test_config_exists(self):
        self.assertTrue(os.path.exists(self.config_path), f"Ecosystem config file missing: {self.config_path}")

    def test_orchestrator_initialization(self):
        # In testing environment, GEMINI_API_KEY might not be present.
        # However, AgentOrchestrator will still initialize the config and agent classes (client init is lazy or works as long as environment has the key. Let's make sure it doesn't fail initialization).
        # We temporarily mock GEMINI_API_KEY if not present so genai.Client() doesn't raise error on init.
        original_key = os.environ.get("GEMINI_API_KEY")
        if not original_key:
            os.environ["GEMINI_API_KEY"] = "mock-key-for-test"
            
        try:
            orchestrator = AgentOrchestrator(config_path=self.config_path)
            
            # Check registered agents
            self.assertIn("ResearchAgent", orchestrator.agents)
            self.assertIn("IndexAgent", orchestrator.agents)
            self.assertIn("ReportAgent", orchestrator.agents)
            
            # Check details of ResearchAgent
            research_agent = orchestrator.agents["ResearchAgent"]
            self.assertEqual(research_agent.agent_id, "ResearchAgent")
            self.assertIn("Google Search Grounding", research_agent.description)
            self.assertEqual(research_agent.model, "gemini-2.0-flash")
            self.assertEqual(research_agent.tools_list, ["google_search"])
        finally:
            if not original_key:
                del os.environ["GEMINI_API_KEY"]
            else:
                os.environ["GEMINI_API_KEY"] = original_key

if __name__ == "__main__":
    unittest.main()
