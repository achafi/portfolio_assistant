from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
from crewai_tools import PDFSearchTool
from .models.output_models import CVInfo, VisitorResponse

pdf_search_tool = PDFSearchTool(pdf="knowledge/CV_Assia_Chafi_2025.pdf")
pdf_search_tool.description = (
    "Search the CV PDF with a text query to find relevant information"
)


@CrewBase
class PortfolioAssistant:
    """PortfolioAssistant crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def resume_assistant(self) -> Agent:
        return Agent(config=self.agents_config["resume_assistant"], verbose=True)

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(config=self.agents_config["reporting_analyst"], verbose=True)

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def extract_cv_info(self) -> Task:
        resume_assistant_agent = self.resume_assistant()
        return Task(
            description=self.tasks_config["extract_cv_info"]["description"],
            expected_output=self.tasks_config["extract_cv_info"]["expected_output"],
            output_pydantic=CVInfo,
            tools=[pdf_search_tool],
            agent=resume_assistant_agent,
        )

    @task
    def reporting_task(self) -> Task:
        reporting_analyst_agent = self.reporting_analyst()
        return Task(
            description=self.tasks_config["reporting_task"]["description"],
            expected_output=self.tasks_config["reporting_task"]["expected_output"],
            output_pydantic=VisitorResponse,
            output_file="report.md",
            agent=reporting_analyst_agent,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PortfolioAssistant crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=[
                self.resume_assistant(),
                self.reporting_analyst(),
            ],  # Call the functions to get agent objects
            tasks=[
                self.extract_cv_info(),
                self.reporting_task(),
            ],  # Call the functions to get task objects
            verbose=True,
        )
