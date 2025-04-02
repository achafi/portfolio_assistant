from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests

DEFAULT_GITHUB_USERNAME = "achafi"

class GitHubReposToolInput(BaseModel):
    """Input schema for GitHubReposTool."""
    github_username: str = Field(
        default=DEFAULT_GITHUB_USERNAME,
        description="GitHub username to list repositories for"
    )

class GitHubReposTool(BaseTool):
    name: str = "list_github_repos"
    description: str = (
        "Lists all public GitHub repositories for a given username. "
        "Returns repository names and descriptions."
    )
    args_schema: Type[BaseModel] = GitHubReposToolInput

    def _run(self, github_username: str = DEFAULT_GITHUB_USERNAME) -> str:
        url = f"https://api.github.com/users/{github_username}/repos"
        response = requests.get(url)
        
        if response.status_code != 200:
            return f"Error fetching repositories: {response.status_code}"
        
        repos = response.json()
        if not repos:
            return f"No public repositories found for user {github_username}"
        
        repo_list = []
        for repo in repos:
            name = repo['name']
            description = repo['description'] or 'No description available'
            repo_list.append(f"- {name}: {description}")
        
        return "\n".join(repo_list)

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
