from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.mcp import MultiMCPTools, MCPTools
from agno.tools.yfinance import YFinanceTools
from fastapi import FastAPI
from mcp import StdioServerParameters

model = AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3")

agent_storage = SqliteStorage(
    table_name="agent_sessions",
    db_file="tmp/data.db",
    auto_upgrade_schema=True,
)

# MCP server parameters setup
github_token = getenv("GITHUB_TOKEN") or getenv("GITHUB_ACCESS_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is required")

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
)

search_agent = Agent(
    name="Search Agent",
    model=model,
    markdown=True,
    instructions=[],
    storage=agent_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[DuckDuckGoTools(), GoogleSearchTools()],
    show_tool_calls=True,
)

finance_agent = Agent(
    name="Finance Agent",
    model=model,
    markdown=True,
    instructions=[],
    storage=agent_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[YFinanceTools()],
    show_tool_calls=True,
)

mcp_github_agent = Agent(
    name="MCP GitHub Agent",
    instructions=dedent("""\
        You are a GitHub assistant. Help users explore repositories and their activity.

        - Use headings to organize your responses
        - Be concise and focus on relevant information\
    """),
    model=model,
    storage=agent_storage,
    add_history_to_messages=True,
    num_history_responses=3,
    add_datetime_to_instructions=True,
    markdown=True,
)

mcp_agent = Agent(
    name="Multi MCP Agent",
    instructions=[
        "You are a assistant.",
        "If the user speak Chinese, you should always answer in Chinese"
    ],
    model=model,
    storage=agent_storage,
    add_history_to_messages=True,
    num_history_responses=3,
    add_datetime_to_instructions=True,
    markdown=True,
)

file_path = str(Path(__file__).parent.parent.parent.parent)


# This is required to start the MCP connection correctly in the FastAPI lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP connection lifecycle inside a FastAPI app"""
    global github_tools
    global multi_mcp_tools

    # Startuplogic: connect to our MCP server
    github_tools = MCPTools(server_params=server_params)
    multi_mcp_tools = MultiMCPTools(
        [
            "uvx mcp-server-git",
            f"npx -y @modelcontextprotocol/server-filesystem {file_path}"
        ]
    )
    await github_tools.connect()
    await multi_mcp_tools.connect()

    # Add the MCP tools to our Agent
    mcp_github_agent.tools = [github_tools]
    mcp_agent.tools = [multi_mcp_tools]

    yield

    # Shutdown: Close MCP connection
    await github_tools.close()
    await multi_mcp_tools.close()


agent_team = Team(
    name="Finance Team",
    mode="coordinate",
    members=[search_agent, finance_agent],
    model=model,
    success_criteria="A comprehensive financial news report with clear sections and data-driven insights.",
    instructions=["Always include sources", "use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

playground = Playground(
    app_id="my_playground",
    agents=[search_agent, finance_agent, mcp_github_agent],
    teams=[agent_team]
)
app = playground.get_app(lifespan=lifespan)

if __name__ == "__main__":
    playground.serve("playground:app", port=7777, reload=True)
