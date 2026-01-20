"""Simple test crew for end-to-end testing without expensive operations."""

from crewai import Agent, Crew, Task, Process


class TestCrew:
    """Minimal crew for testing WebSocket flow without expensive operations."""
    
    def __init__(self, llm_choice: str = "openai"):
        """Initialize test crew with specified LLM."""
        self.llm_choice = llm_choice
    
    def crew(self) -> Crew:
        """Create a minimal test crew."""
        
        # Simple test agent
        test_agent = Agent(
            role="Test Agent",
            goal="Respond with a simple greeting",
            backstory="A friendly test agent for system testing",
            verbose=False,
            allow_delegation=False,
            llm=self.llm_choice
        )
        
        # Simple test task
        test_task = Task(
            description="Say hello and confirm the system is working",
            expected_output="A brief greeting message",
            agent=test_agent
        )
        
        # Create minimal crew
        return Crew(
            agents=[test_agent],
            tasks=[test_task],
            process=Process.sequential,
            verbose=False
        )
