from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import ShortTermMemory, LongTermMemory, EntityMemory
from crewai_tools import PDFSearchTool
from .models.output_models import (
    CVInfo, 
    VisitorResponse, 
    GitHubRepositoriesResponse,
    TaskAnalysis
)
from .tools.custom_tool import GitHubReposTool
import os

# Initialize memory storage paths
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

LONG_TERM_PATH = os.path.join(MEMORY_DIR, "long_term")
ENTITY_PATH = os.path.join(MEMORY_DIR, "entity")
os.makedirs(LONG_TERM_PATH, exist_ok=True)
os.makedirs(ENTITY_PATH, exist_ok=True)

pdf_search_tool = PDFSearchTool(pdf="knowledge/CV_Assia_Chafi_2025.pdf")
pdf_search_tool.description = (
    "Search the CV PDF with a text query to find relevant information"
)
github_repos_tool = GitHubReposTool()
github_repos_tool.description = (
    "Fetch and list public GitHub repositories associated with 'achafi' GitHub profile, providing their names and potentially brief descriptions."
)

@CrewBase
class PortfolioAssistant:
    """PortfolioAssistant crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        # Initialize long-term and entity memories
        self.long_term_memory = LongTermMemory(storage=LONG_TERM_PATH)
        self.entity_memory = EntityMemory(storage=ENTITY_PATH)

    def get_agent_memories(self, agent_name: str):
        """Get combined memories for an agent"""
        # Each agent gets a fresh short-term memory for the current session
        short_term = ShortTermMemory()
        
        # Share long-term and entity memories across sessions
        return [
            short_term,
            self.long_term_memory,
            self.entity_memory
        ]

    @agent
    def task_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["task_manager"],
            memory=self.get_agent_memories("task_manager"),
            verbose=True
        )

    @agent
    def resume_assistant(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_assistant"], 
            tools=[pdf_search_tool],
            memory=self.get_agent_memories("resume_assistant"),
            verbose=True
        )

    @agent
    def github_project_lister(self) -> Agent:
        return Agent(
            config=self.agents_config["github_project_lister"], 
            tools=[github_repos_tool], 
            memory=self.get_agent_memories("github_project_lister"),
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"], 
            memory=self.get_agent_memories("reporting_analyst"),
            verbose=True
        )

    @task
    def analyze_question(self, question: str) -> Task:
        task_manager_agent = self.task_manager()
        return Task(
            description=self.tasks_config["analyse_question"]["description"],
            expected_output=self.tasks_config["analyse_question"]["expected_output"],
            output_pydantic=TaskAnalysis,
            agent=task_manager_agent
        )

    @task
    def extract_cv_info(self) -> Task:
        resume_assistant_agent = self.resume_assistant()
        return Task(
            description=self.tasks_config["extract_cv_info"]["description"],
            expected_output=self.tasks_config["extract_cv_info"]["expected_output"],
            output_pydantic=CVInfo,
            agent=resume_assistant_agent,
        )
    
    @task
    def list_github_projects_task(self) -> Task:
        github_project_lister_agent = self.github_project_lister()
        return Task(
            description=self.tasks_config["list_github_projects"]["description"],
            expected_output=self.tasks_config["list_github_projects"]["expected_output"],
            output_pydantic=GitHubRepositoriesResponse,
            agent=github_project_lister_agent
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
    def crew(self, question: str = None) -> Crew:
        """Creates the PortfolioAssistant crew with dynamic task selection based on the question"""
        if not question:
            tasks = [
                self.extract_cv_info(),
                self.list_github_projects_task(),
                self.reporting_task(),
            ]
        else:
            # First analyze the question
            analysis_task = self.analyze_question(question)
            tasks = [analysis_task]
            
            # Based on analysis, add required tasks
            analysis = analysis_task.output
            if analysis.needs_resume_info:
                tasks.append(self.extract_cv_info())
            if analysis.needs_github_info:
                tasks.append(self.list_github_projects_task())
            
            # Always add reporting task last
            tasks.append(self.reporting_task())

        return Crew(
            agents=[
                self.task_manager(),
                self.resume_assistant(),
                self.github_project_lister(),
                self.reporting_analyst(),
            ],
            tasks=tasks,
            verbose=True,
        )
