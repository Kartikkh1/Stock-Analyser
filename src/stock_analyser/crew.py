from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from .tools.finnhub_tools import FinnhubAPITools

@CrewBase
class StockAnalyser():
    """StockAnalyser crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    serper_dev_tool = SerperDevTool()
    finnhub_api_tools = FinnhubAPITools() # API key will be read from FINNHUB_API_KEY environment variable
    @agent
    def researcher_anthropic(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher_anthropic'], # type: ignore[index]
            tools=[self.serper_dev_tool, self.finnhub_api_tools],
            verbose=True
        )

    @agent
    def reporter_anthropic(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter_anthropic'], # type: ignore[index]
            tools=[self.serper_dev_tool, self.finnhub_api_tools],
            verbose=True
        )

    @agent
    def researcher_gemini(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher_gemini'], # type: ignore[index]
            tools=[self.serper_dev_tool, self.finnhub_api_tools],
            verbose=True
        )

    @agent
    def reporter_gemini(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter_gemini'], # type: ignore[index]
            tools=[self.serper_dev_tool, self.finnhub_api_tools],
            verbose=True
        )

    @agent
    def researcher_openai(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher_openai'], # type: ignore[index]
            tools=[self.serper_dev_tool, self.finnhub_api_tools],
            verbose=True
        )

    @agent
    def reporter_openai(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter_openai'], # type: ignore[index]
            tools=[self.serper_dev_tool, self.finnhub_api_tools],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def researcher_anthropic_task(self) -> Task:
        return Task(
            config=self.tasks_config['researcher_anthropic_task'], # type: ignore[index]
        )

    @task
    def reporter_anthropic_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporter_anthropic_task'], # type: ignore[index]
            output_file='output/{name}_anthropic_report.md',
        )

    @task
    def researcher_gemini_task(self) -> Task:
        return Task(
            config=self.tasks_config['researcher_gemini_task'], # type: ignore[index]
        )

    @task
    def reporter_gemini_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporter_gemini_task'], # type: ignore[index]
            output_file='output/{name}_gemini_report.md',
        )

    @task
    def researcher_openai_task(self) -> Task:
        return Task(
            config=self.tasks_config['researcher_openai_task'], # type: ignore[index]
        )

    @task
    def reporter_openai_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporter_openai_task'], # type: ignore[index]
            output_file='output/{name}_open_ai_report.md',
            
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockAnnalyzer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://crewai.com/concepts/knowledge#what-is-knowledge
        return Crew(
            agents=[self.researcher_anthropic(), self.reporter_anthropic(), self.researcher_openai(), self.reporter_openai()],
            tasks=[self.researcher_anthropic_task(), self.reporter_anthropic_task(), self.researcher_openai_task(), self.reporter_openai_task()],
            process=Process.sequential,
            verbose=True,
            tracing=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
