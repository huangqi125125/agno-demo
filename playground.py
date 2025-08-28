from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.playground import Playground
from agno.tools.mcp import MultiMCPTools, MCPTools
from fastapi import FastAPI
from mcp import StdioServerParameters

from common import azure_model, session_storage
from main import search_agent, finance_agent, agent_team

# MCP server parameters setup
github_token = getenv("GITHUB_TOKEN") or getenv("GITHUB_ACCESS_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is required")

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
)

# MCP
mcp_github_agent = Agent(
    name="MCP GitHub Agent",
    instructions=dedent("""\
        You are a GitHub assistant. Help users explore repositories and their activity.

        - Use headings to organize your responses
        - Be concise and focus on relevant information\
    """),
    model=azure_model,
    storage=session_storage,
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
    model=azure_model,
    storage=session_storage,
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


playground = Playground(
    app_id="my_playground",
    agents=[search_agent, finance_agent, mcp_github_agent, mcp_agent],
    teams=[agent_team]
)
app = playground.get_app(lifespan=lifespan)

if __name__ == "__main__":
    playground.serve("playground:app", port=7777, reload=True)
