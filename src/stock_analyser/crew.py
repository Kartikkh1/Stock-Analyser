from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from .tools.finnhub_tools import FinnhubAPITools
from .tools.visualization_tools import VisualizationTools
from .tools.technical_analysis_tools import TechnicalAnalysisTools
from .utils.logger import logger

@CrewBase
class StockAnalyser():
    """StockAnalyser crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    serper_dev_tool = SerperDevTool()
    finnhub_tools = None
    try:
        finnhub_tools = FinnhubAPITools()
        logger.info("FinnhubAPITools initialized successfully.")
    except ValueError as e:
        logger.error(f"Error initializing FinnhubAPITools: {e}", exc_info=True)
    visualization_tools = VisualizationTools()
    technical_analysis_tools = TechnicalAnalysisTools()

    def __init__(self, selected_llm_type: str, stock_name: str):
        self.selected_llm_type = selected_llm_type
        self.stock_name = stock_name
        logger.info(f"StockAnalyser initialized with LLM type: {selected_llm_type}")

    @agent
    def researcher(self) -> Agent:
        researcher_tools = [self.serper_dev_tool]
        if self.finnhub_tools:
            researcher_tools.append(self.finnhub_tools)
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            llm=self.selected_llm_type,
            tools=researcher_tools,
            verbose=True
        )

    @agent
    def reporter(self) -> Agent:
        reporter_tools = [self.serper_dev_tool, self.visualization_tools]
        if self.finnhub_tools:
            reporter_tools.append(self.finnhub_tools)
        return Agent(
            config=self.agents_config['reporter'], # type: ignore[index]
            llm=self.selected_llm_type,
            tools=reporter_tools,
            verbose=True
        )

    @agent
    def technical_analyst(self) -> Agent:
        technical_analyst_tools = [self.technical_analysis_tools]
        if self.finnhub_tools:
            technical_analyst_tools.append(self.finnhub_tools)
        return Agent(
            config=self.agents_config['technical_analyst'], # type: ignore[index]
            llm=self.selected_llm_type,
            tools=technical_analyst_tools,
            verbose=True
        )

    @agent
    def fundamental_analyst(self) -> Agent:
        fundamental_analyst_tools = []
        if self.finnhub_tools:
            fundamental_analyst_tools.append(self.finnhub_tools)
        return Agent(
            config=self.agents_config['fundamental_analyst'], # type: ignore[index]
            llm=self.selected_llm_type,
            tools=fundamental_analyst_tools,
            verbose=True
        )

    @agent
    def sentiment_analyst(self) -> Agent:
        sentiment_analyst_tools = []
        if self.finnhub_tools:
            sentiment_analyst_tools.append(self.finnhub_tools)
        return Agent(
            config=self.agents_config['sentiment_analyst'], # type: ignore[index]
            llm=self.selected_llm_type,
            tools=sentiment_analyst_tools,
            verbose=True
        )

    @task
    def researcher_task(self) -> Task:
        task_config = self.tasks_config['researcher_task']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.researcher(),
        )

    @task
    def reporter_task(self) -> Task:
        task_config = self.tasks_config['reporter_task']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            context=[self.researcher_task(), self.sentiment_analysis_task(), self.technical_analyst_task(), self.chart_pattern_analysis_task(), self.fundamental_analysis_task()],
            output_file=f'output/{self.stock_name}_{self.selected_llm_type}_report.md',
            markdown=task_config['markdown'],
            agent=self.reporter()
        )

    @task
    def technical_analyst_task(self) -> Task:
        task_config = self.tasks_config['technical_analyst_task']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.technical_analyst()
        )

    @task
    def chart_pattern_analysis_task(self) -> Task:
        task_config = self.tasks_config['chart_pattern_analysis_task']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.technical_analyst()
        )

    @task
    def sentiment_analysis_task(self) -> Task:
        task_config = self.tasks_config['sentiment_analysis_task']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=self.sentiment_analyst()
        )

    @task
    def fundamental_analysis_task(self) -> Task:
        task_config = self.tasks_config['fundamental_analysis_task']
        return Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            context=[self.researcher_task()],
            agent=self.fundamental_analyst()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockAnnalyzer crew"""
        return Crew(
            agents=[self.researcher(), self.reporter(), self.technical_analyst(), self.sentiment_analyst(), self.fundamental_analyst()],
            tasks=[self.researcher_task(), self.sentiment_analysis_task(), self.technical_analyst_task(), self.chart_pattern_analysis_task(), self.fundamental_analysis_task(), self.reporter_task()],
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
