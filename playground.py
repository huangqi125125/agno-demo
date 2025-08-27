from contextlib import asynccontextmanager
from os import getenv
from textwrap import dedent

from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.mcp import MCPTools
from agno.tools.yfinance import YFinanceTools
from fastapi import FastAPI
from mcp import StdioServerParameters

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
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    markdown=True,
    instructions=[],
    storage=agent_storage,
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    tools=[DuckDuckGoTools(), GoogleSearchTools()],
    show_tool_calls=True,
)

finance_agent = Agent(
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
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
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    storage=agent_storage,
    add_history_to_messages=True,
    num_history_responses=3,
    add_datetime_to_instructions=True,
    markdown=True,
)


# This is required to start the MCP connection correctly in the FastAPI lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP connection lifecycle inside a FastAPI app"""
    global mcp_tools

    # Startuplogic: connect to our MCP server
    mcp_tools = MCPTools(server_params=server_params)
    await mcp_tools.connect()

    # Add the MCP tools to our Agent
    mcp_github_agent.tools = [mcp_tools]

    yield

    # Shutdown: Close MCP connection
    await mcp_tools.close()


agent_team = Team(
    mode="coordinate",
    members=[search_agent, finance_agent],
    model=AzureOpenAI(id="o3", api_version="2025-01-01-preview", azure_deployment="o3"),
    success_criteria="A comprehensive financial news report with clear sections and data-driven insights.",
    instructions=["Always include sources", "use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

playground = Playground(
    app_id="my_playground",
    agents=[search_agent, mcp_github_agent],
    teams=[agent_team]
)
app = playground.get_app(lifespan=lifespan)

if __name__ == "__main__":
    playground.serve("my_playground:app", port=7777, reload=True)
